from __future__ import annotations
import io
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_file
from sklearn.preprocessing import MinMaxScaler


Period = Literal["hourly", "daily", "weekly", "monthly"]


def _find_project_root() -> Path:
    cwd = Path.cwd().resolve()
    for p in [cwd, *cwd.parents]:
        if (p / "dataset").exists():
            return p
    return cwd


ROOT = _find_project_root()
DATA_PATH = ROOT / "dataset" / "Cleaned" / "cleaned_sorted_energy_dataset.xlsx"
MODELS_DIR = ROOT / "models"
METRICS_PATH = ROOT / "outputs" / "lstm_metrics_per_appliance.csv"

TARGET_COL = "Energy Consumption (kWh)"
BASE_EXOG_COLS = ["Outdoor Temperature (C)", "Household Size"]

TIME_STEPS = 8
TOP_N_HOMES = 50


app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)


@dataclass(frozen=True)
class EnergyData:
    df: pd.DataFrame


@dataclass(frozen=True)
class Aggregates:
    overall: dict[Period, pd.Series]
    device_totals: pd.Series
    device_latest: dict[Period, pd.Series]


_energy_cache: Optional[EnergyData] = None
_agg_cache: Optional[Aggregates] = None


def _load_energy_data() -> EnergyData:
    global _energy_cache
    if _energy_cache is not None:
        return _energy_cache

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_excel(DATA_PATH)
    df.columns = df.columns.str.strip()

    required_cols = [
        "Date",
        "Hour",
        "Home ID",
        "Appliance Type",
        TARGET_COL,
        *BASE_EXOG_COLS,
    ]
    missing_required = [c for c in required_cols if c not in df.columns]
    if missing_required:
        raise ValueError(f"Dataset missing required columns: {missing_required}")

    df = df[required_cols].copy()

    df["Date"] = pd.to_datetime(df["Date"])
    df["Timestamp"] = df["Date"] + pd.to_timedelta(df["Hour"], unit="h")

    _energy_cache = EnergyData(df=df)
    return _energy_cache


def _get_aggregates() -> Aggregates:
    """Pre-compute aggregates once so chart endpoints stay fast."""
    global _agg_cache
    if _agg_cache is not None:
        return _agg_cache

    df = _load_energy_data().df

    # Build a single overall time-indexed series once.
    # This is the heavy step; keep it to one groupby over the full dataset.
    base_series = (
        df.dropna(subset=["Timestamp", TARGET_COL])
        .groupby("Timestamp", sort=False)[TARGET_COL]
        .sum()
        .sort_index()
    )

    overall: dict[Period, pd.Series] = {
        "hourly": base_series,
        "daily": base_series.resample("D").sum(),
        # Matches pandas to_period('W') default (weeks ending Sunday).
        "weekly": base_series.groupby(base_series.index.to_period("W-SUN").start_time).sum().sort_index(),
        "monthly": base_series.resample("MS").sum(),
    }

    device_totals = (
        df.dropna(subset=["Appliance Type", TARGET_COL])
        .groupby("Appliance Type")[TARGET_COL]
        .sum()
        .sort_values(ascending=False)
    )

    df_device = df.dropna(subset=["Timestamp", "Appliance Type", TARGET_COL]).copy()
    device_latest: dict[Period, pd.Series] = {}

    def _latest_bucket_bounds(ts_max: pd.Timestamp, period: Period) -> tuple[pd.Timestamp, pd.Timestamp]:
        if period == "hourly":
            start = ts_max.floor("h")
            end = start + pd.Timedelta(hours=1)
            return start, end
        if period == "daily":
            start = ts_max.normalize()
            end = start + pd.Timedelta(days=1)
            return start, end
        if period == "weekly":
            start = ts_max.to_period("W-SUN").start_time
            end = start + pd.Timedelta(days=7)
            return start, end
        if period == "monthly":
            start = ts_max.to_period("M").start_time
            end = start + pd.offsets.MonthBegin(1)
            return pd.Timestamp(start), pd.Timestamp(end)
        raise ValueError("invalid period")

    if df_device.empty:
        for p in ["hourly", "daily", "weekly", "monthly"]:
            device_latest[_normalize_period(p)] = pd.Series(dtype=float)
    else:
        ts_max = pd.to_datetime(df_device["Timestamp"].max())
        for p in ["hourly", "daily", "weekly", "monthly"]:
            period = _normalize_period(p)
            start, end = _latest_bucket_bounds(ts_max, period)
            mask = (df_device["Timestamp"] >= start) & (df_device["Timestamp"] < end)
            by_app = (
                df_device.loc[mask]
                .groupby("Appliance Type")[TARGET_COL]
                .sum()
                .sort_values(ascending=False)
            )
            device_latest[period] = by_app

    _agg_cache = Aggregates(overall=overall, device_totals=device_totals, device_latest=device_latest)
    return _agg_cache


def _normalize_period(period: str) -> Period:
    p = period.strip().lower()
    if p not in {"hourly", "daily", "weekly", "monthly"}:
        raise ValueError("period must be one of hourly,daily,weekly,monthly")
    return p  # type: ignore[return-value]


def _period_group_key(ts: pd.Series, period: Period) -> pd.Series:
    if period == "hourly":
        return ts.dt.floor("h")
    if period == "daily":
        return ts.dt.to_period("D").dt.start_time
    if period == "weekly":
        return ts.dt.to_period("W").dt.start_time
    if period == "monthly":
        return ts.dt.to_period("M").dt.start_time
    raise ValueError("invalid period")


def _make_png_response(fig: plt.Figure):
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=150, transparent=True)
    plt.close(fig)
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


def _apply_axes_style(ax: plt.Axes):
    fg = (1.0, 1.0, 1.0, 0.90)
    spine = (1.0, 1.0, 1.0, 0.22)
    grid = (1.0, 1.0, 1.0, 0.12)

    ax.grid(True, color=grid, linestyle="-", linewidth=0.9)
    ax.tick_params(axis="both", labelsize=9, colors=fg)
    ax.xaxis.label.set_color(fg)
    ax.yaxis.label.set_color(fg)
    ax.title.set_color(fg)
    for s in ax.spines.values():
        s.set_color(spine)
    ax.set_facecolor((0, 0, 0, 0))


def _format_time_axis(ax: plt.Axes):
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

    # Make sure x tick labels are readable on dark UI
    for t in ax.get_xticklabels():
        t.set_color((1.0, 1.0, 1.0, 0.90))


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/appliances")
def api_appliances():
    df = _load_energy_data().df
    appliances = sorted(df["Appliance Type"].dropna().unique().tolist())
    return jsonify({"appliances": appliances})


@app.get("/api/metrics")
def api_metrics():
    if not METRICS_PATH.exists():
        return jsonify({"metrics": [], "error": f"Metrics CSV not found: {METRICS_PATH}"})

    df = pd.read_csv(METRICS_PATH)
    metrics = df.to_dict(orient="records")
    return jsonify({"metrics": metrics})


@app.get("/api/summary")
def api_summary():
    agg = _get_aggregates()

    # NOTE:
    # If we return "total" as sum over the whole dataset, it will be identical
    # for hourly/daily/weekly/monthly (sum is invariant to grouping). For a
    # dashboard, the useful value is the most recent bucket's consumption.

    summaries: dict[str, dict[str, float | str]] = {}
    for period in ["hourly", "daily", "weekly", "monthly"]:
        p = _normalize_period(period)
        series = agg.overall[p]

        if len(series):
            latest_value = float(series.iloc[-1])
            latest_time = str(series.index[-1])
            dataset_total = float(series.sum())
            avg_value = float(series.mean())
        else:
            latest_value = 0.0
            latest_time = ""
            dataset_total = 0.0
            avg_value = 0.0

        summaries[p] = {
            # Backward-compatible key used by the UI card value
            "total": latest_value,
            "avg": avg_value,
            # Extra context if needed later
            "latest_time": latest_time,
            "dataset_total": dataset_total,
        }

    return jsonify({"summaries": summaries})


@app.get("/api/chart/overall")
def api_chart_overall():
    period = _normalize_period(request.args.get("period", "daily"))

    agg = _get_aggregates()
    series = agg.overall[period]

    # Avoid rendering extremely long series (keeps charts snappy)
    if len(series) > 2000:
        series = series.iloc[-2000:]

    fig = plt.figure(figsize=(9, 3.6))
    fig.patch.set_alpha(0)
    ax = fig.add_subplot(1, 1, 1)
    _apply_axes_style(ax)

    x = series.index
    y = series.values

    # Different chart types by period (adds variety without adding UI)
    if period == "hourly":
        ax.plot(x, y, linewidth=1.9, color="tab:cyan")
        ax.fill_between(x, y, color="tab:cyan", alpha=0.12)
        if len(series) >= 12:
            y_smooth = series.rolling(12, min_periods=1).mean().values
            ax.plot(x, y_smooth, linewidth=1.2, color="tab:orange", alpha=0.9)
    elif period == "daily":
        ax.bar(x, y, width=0.8, color="tab:blue", alpha=0.72)
        if len(series) >= 7:
            y_smooth = series.rolling(7, min_periods=1).mean().values
            ax.plot(x, y_smooth, linewidth=1.8, color="tab:orange")
    elif period == "weekly":
        ax.step(x, y, where="mid", linewidth=1.9, color="tab:green")
        ax.fill_between(x, y, step="mid", color="tab:green", alpha=0.12)
    else:  # monthly
        ax.plot(x, y, linewidth=2.0, color="tab:purple", marker="o", markersize=3.6)

    if len(series):
        ax.axhline(float(series.mean()), color="white", alpha=0.16, linewidth=1.0)
        peak_i = int(np.argmax(y))
        ax.scatter([x[peak_i]], [y[peak_i]], color="tab:red", s=28, zorder=4)

    ax.set_title(f"Overall Consumption ({period})", fontsize=11, pad=10)
    ax.set_ylabel("kWh")
    _format_time_axis(ax)
    return _make_png_response(fig)


@app.get("/api/chart/device")
def api_chart_device():
    period = _normalize_period(request.args.get("period", "monthly"))

    agg = _get_aggregates()
    latest_by_app = agg.device_latest.get(period, pd.Series(dtype=float))
    if latest_by_app.empty:
        latest_by_app = agg.device_totals

    by = latest_by_app.head(10)

    fig = plt.figure(figsize=(9, 3.9))
    fig.patch.set_alpha(0)
    ax = fig.add_subplot(1, 1, 1)
    _apply_axes_style(ax)

    labels = by.index.astype(str)
    values = by.values

    if period in {"hourly", "daily"}:
        ax.barh(labels[::-1], values[::-1], color="tab:blue", alpha=0.82)
        ax.set_xlabel("kWh")
        ax.set_ylabel("Appliance")
    elif period == "weekly":
        top = latest_by_app.head(7)
        other = float(latest_by_app.iloc[7:].sum()) if len(latest_by_app) > 7 else 0.0
        pie_vals = top.values.tolist() + ([other] if other > 0 else [])
        pie_labels = top.index.astype(str).tolist() + (["Other"] if other > 0 else [])
        ax.pie(
            pie_vals,
            labels=pie_labels,
            startangle=90,
            counterclock=False,
            wedgeprops={"width": 0.38, "edgecolor": (1, 1, 1, 0.14)},
            textprops={"fontsize": 9, "color": (1.0, 1.0, 1.0, 0.92)},
        )
        ax.set_aspect("equal")
    else:  # monthly
        ax.bar(labels, values, color="tab:purple", alpha=0.74)
        ax.set_ylabel("kWh")
        ax.tick_params(axis="x", rotation=25)

    ax.set_title(f"Device-wise Usage (Latest bucket, {period})", fontsize=11, pad=10)
    return _make_png_response(fig)


@app.get("/api/suggestions")
def api_suggestions():
    period = _normalize_period(request.args.get("period", "monthly"))
    appliance = (request.args.get("appliance") or "").strip()

    df = _load_energy_data().df

    tips: list[str] = []

    if appliance:
        df_a = df[df["Appliance Type"] == appliance].copy()
        total = float(df_a[TARGET_COL].dropna().sum())
        tips.append(f"{appliance}: total recorded usage is {total:.2f} kWh.")

        if "Fridge" in appliance or "Refrigerator" in appliance:
            tips.append("Keep fridge temperature ~3–5°C and avoid frequent door opening.")
        if "Air" in appliance or "Condition" in appliance:
            tips.append("For AC: raise setpoint by 1–2°C and use fans to reduce runtime.")
        if "Lights" in appliance:
            tips.append("For lights: switch to LEDs and turn off unused rooms.")
        if "Heater" in appliance:
            tips.append("For heaters: seal drafts and avoid heating empty rooms.")
    else:
        tips.append("Select an appliance to get device-specific tips.")

    # Dataset-level tip: highlight highest-consuming appliance.
    by_app = (
        df.dropna(subset=["Appliance Type", TARGET_COL])
        .groupby("Appliance Type")[TARGET_COL]
        .sum()
        .sort_values(ascending=False)
    )
    if len(by_app):
        top_app = str(by_app.index[0])
        tips.append(f"Highest total usage device in dataset: {top_app}.")

    tips.append(f"View period: {period}. Compare your peaks and consider shifting heavy usage to off-peak hours.")

    return jsonify({"tips": tips})


def _build_recent_sequence(df_app: pd.DataFrame, home_id: int) -> tuple[np.ndarray, MinMaxScaler]:
    df_h = df_app[df_app["Home ID"].astype(int) == int(home_id)].copy()
    if df_h.empty:
        raise ValueError("No data for that home_id")

    df_h = df_h.sort_values("Timestamp").copy()
    df_h["hour"] = df_h["Timestamp"].dt.hour
    df_h["day"] = df_h["Timestamp"].dt.day
    df_h["weekday"] = df_h["Timestamp"].dt.weekday
    df_h["month"] = df_h["Timestamp"].dt.month

    exog_cols = ["hour", "day", "weekday", "month", *BASE_EXOG_COLS]
    missing = [c for c in [TARGET_COL, *exog_cols] if c not in df_h.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    delta_hours = df_h["Timestamp"].diff().dt.total_seconds().div(3600.0).fillna(0.0)
    delta_hours = delta_hours.clip(lower=0.0, upper=48.0)

    feats = df_h[exog_cols].copy()
    feats["delta_hours"] = delta_hours.to_numpy()

    raw = np.concatenate([df_h[[TARGET_COL]].to_numpy(), feats.to_numpy()], axis=1)

    if len(raw) <= TIME_STEPS:
        raise ValueError("Not enough history to build a sequence")

    # Fit scaler on this home's history (simple, consistent with dashboard usage).
    scaler_y = MinMaxScaler()
    scaler_X = MinMaxScaler()
    scaler_y.fit(raw[:, 0:1])
    scaler_X.fit(raw[:, 1:])

    scaled = np.concatenate([scaler_y.transform(raw[:, 0:1]), scaler_X.transform(raw[:, 1:])], axis=1)

    window = scaled[-TIME_STEPS:, :]
    X_seq = window.reshape(1, TIME_STEPS, window.shape[1])
    return X_seq, scaler_y


def _auto_home_sequence(df_app: pd.DataFrame) -> tuple[int, np.ndarray, MinMaxScaler]:
    """Pick a home_id for this appliance that has enough history to predict."""
    home_counts = (
        df_app["Home ID"].dropna().astype(int).value_counts().head(TOP_N_HOMES)
    )
    for hid in home_counts.index.tolist():
        try:
            X_seq, scaler_y = _build_recent_sequence(df_app, int(hid))
            return int(hid), X_seq, scaler_y
        except Exception:
            continue
    raise ValueError("No home has enough history for this appliance")


@app.post("/api/predict")
def api_predict():
    payload = request.get_json(silent=True) or {}
    appliance = str(payload.get("appliance", "")).strip()
    home_id = payload.get("home_id", None)

    if not appliance:
        return jsonify({"error": "appliance is required"}), 400
    home_id_provided = home_id is not None and str(home_id).strip() != ""

    safe_app = appliance.replace(" ", "_")
    model_path = MODELS_DIR / f"lstm_{safe_app}_top{TOP_N_HOMES}_ts{TIME_STEPS}.h5"
    if not model_path.exists():
        return jsonify({"error": f"Model not found: {model_path}"}), 404

    df = _load_energy_data().df
    df_app = df[df["Appliance Type"] == appliance].copy()
    if df_app.empty:
        return jsonify({"error": "Unknown appliance"}), 400

    try:
        from tensorflow.keras.models import load_model

        model = load_model(model_path)
        if home_id_provided:
            home_id_used = int(home_id)
            X_seq, scaler_y = _build_recent_sequence(df_app, home_id_used)
            home_id_source = "provided"
        else:
            home_id_used, X_seq, scaler_y = _auto_home_sequence(df_app)
            home_id_source = "auto"

        y_pred_scaled = model.predict(X_seq, verbose=0)
        y_pred = float(scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1))[0, 0])

        return jsonify(
            {
                "appliance": appliance,
                "home_id": int(home_id_used),
                "home_id_source": home_id_source,
                "prediction_next": y_pred,
                "units": "kWh",
                "model_path": model_path.relative_to(ROOT).as_posix(),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        )
    except Exception as e:  # keep API simple
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    # NOTE: use_reloader=False avoids unexpected restarts when heavy libraries
    # (like TensorFlow) are imported during requests.
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)