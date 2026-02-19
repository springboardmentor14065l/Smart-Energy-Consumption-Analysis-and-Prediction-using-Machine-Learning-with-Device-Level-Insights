async function getJSON(url) {
  const res = await fetch(url);
  return await res.json();
}

function setChart(imgEl, url) {
  // cache-bust so changes apply immediately
  imgEl.src = `${url}&_=${Date.now()}`;
}

function fmtKwh(x) {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  return `${Number(x).toFixed(2)} kWh`;
}

async function loadSummaries() {
  const data = await getJSON("/api/summary");
  const s = data.summaries;

  const ids = ["hourly", "daily", "weekly", "monthly"];
  for (const p of ids) {
    document.getElementById(`sum-${p}`).textContent = fmtKwh(s[p].total);
    document.getElementById(`avg-${p}`).textContent = `Avg per ${p.slice(0, -2)}: ${fmtKwh(s[p].avg)}`;
  }
}

async function loadAppliances() {
  let apps = [];
  try {
    const data = await getJSON("/api/appliances");
    apps = data.appliances || [];
  } catch (e) {
    const el = document.getElementById("pred-result");
    if (el) el.textContent = `Error loading appliances: ${e}`;
    apps = [];
  }

  const suggest = document.getElementById("suggest-appliance");
  const pred = document.getElementById("pred-appliance");

  function fill(selectEl, includeBlank) {
    selectEl.innerHTML = "";
    if (includeBlank) {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "(Select)";
      selectEl.appendChild(opt);
    }
    for (const a of apps) {
      const opt = document.createElement("option");
      opt.value = a;
      opt.textContent = a;
      selectEl.appendChild(opt);
    }
  }

  fill(suggest, true);
  fill(pred, true);
}

function wireCharts() {
  const overallPeriod = document.getElementById("overall-period");
  const overallChart = document.getElementById("overall-chart");

  const devicePeriod = document.getElementById("device-period");
  const deviceChart = document.getElementById("device-chart");

  const refreshOverall = () =>
    setChart(overallChart, `/api/chart/overall?period=${encodeURIComponent(overallPeriod.value)}`);

  const refreshDevice = () =>
    setChart(deviceChart, `/api/chart/device?period=${encodeURIComponent(devicePeriod.value)}`);

  overallPeriod.addEventListener("change", refreshOverall);
  devicePeriod.addEventListener("change", refreshDevice);

  refreshOverall();
  refreshDevice();
}

function wireSuggestions() {
  const app = document.getElementById("suggest-appliance");
  const period = document.getElementById("suggest-period");
  const btn = document.getElementById("suggest-refresh");
  const tips = document.getElementById("tips");

  async function refresh() {
    const u = new URL("/api/suggestions", window.location.origin);
    u.searchParams.set("period", period.value);
    if (app.value) u.searchParams.set("appliance", app.value);

    const data = await getJSON(u.toString());
    tips.innerHTML = "";
    for (const t of data.tips || []) {
      const li = document.createElement("li");
      li.textContent = t;
      tips.appendChild(li);
    }
  }

  btn.addEventListener("click", refresh);
  period.addEventListener("change", refresh);
}

function wirePrediction() {
  const app = document.getElementById("pred-appliance");
  const home = document.getElementById("pred-home");
  const btn = document.getElementById("pred-run");
  const out = document.getElementById("pred-result");

  async function predict() {
    out.textContent = "Predicting…";

    const payload = {
      appliance: app.value,
      home_id: home.value ? Number(home.value) : null,
    };

    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      out.textContent = `Error: ${data.error || "Unknown error"}`;
      return;
    }

    const source = data.home_id_source ? `, Home source: ${data.home_id_source}` : "";
    out.textContent = `Next predicted consumption: ${fmtKwh(data.prediction_next)} (Appliance: ${data.appliance}, Home: ${data.home_id}${source})`;
  }

  btn.addEventListener("click", predict);
}

async function main() {
  await loadSummaries();
  await loadAppliances();
  wireCharts();
  wireSuggestions();
  wirePrediction();
}

main().catch((e) => {
  console.error(e);
  const el = document.getElementById("pred-result");
  if (el) el.textContent = `Error loading dashboard: ${e}`;
});
