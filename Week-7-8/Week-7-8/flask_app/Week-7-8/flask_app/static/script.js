/* ═══════════════════════════════════════════════════════════════════
   Smart Energy Monitor — script.js
   Dashboard logic: API calls, Chart.js rendering, UI interactions
   ═══════════════════════════════════════════════════════════════════ */

'use strict';

// ── Config ────────────────────────────────────────────────────────────────────
const API = window.location.origin;

const APP_ICONS = {
  'Air Conditioning': '❄️',
  'Computer':         '💻',
  'Dishwasher':       '🍽️',
  'Fridge':           '🧊',
  'Heater':           '🔥',
  'Lights':           '💡',
  'Microwave':        '📡',
  'Oven':             '🍳',
  'TV':               '📺',
  'Washing Machine':  '🫧'
};

const CHART_PALETTE = [
  '#00d4ff','#00e5a0','#9d6fff','#ffb830','#ff4d6d',
  '#0090ff','#ff6b35','#4ecdc4','#ff8fab','#a8dadc'
];

// ── State ─────────────────────────────────────────────────────────────────────
let allStats     = {};
let currentApp   = null;
let appLineChart  = null;
let appDailyChart = null;
let appHourlyChart = null;

// ── Utility ───────────────────────────────────────────────────────────────────
function r2Color(r2) {
  if (r2 >= 0.7) return '#00e5a0';
  if (r2 >= 0.4) return '#ffb830';
  return '#ff4d6d';
}

function chartBaseOptions(extras = {}) {
  return {
    responsive: true,
    maintainAspectRatio: true,
    animation: { duration: 600, easing: 'easeInOutQuart' },
    plugins: {
      legend: {
        labels: {
          color: '#5a7a9e',
          font: { size: 11, family: "'DM Sans', sans-serif" },
          boxWidth: 12,
          padding: 16
        }
      },
      tooltip: {
        backgroundColor: 'rgba(13, 22, 37, 0.95)',
        titleColor: '#00d4ff',
        bodyColor: '#dce8f8',
        borderColor: '#1e3050',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
        titleFont: { family: "'Space Mono', monospace", size: 11 },
        bodyFont:  { family: "'DM Sans', sans-serif",  size: 12 }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#3d5a7a',
          maxTicksLimit: 8,
          font: { size: 10 }
        },
        grid: { color: 'rgba(30,48,80,0.5)' }
      },
      y: {
        ticks: {
          color: '#3d5a7a',
          font: { size: 10 }
        },
        grid: { color: 'rgba(30,48,80,0.5)' }
      }
    },
    ...extras
  };
}

// ── Live Clock ─────────────────────────────────────────────────────────────────
function startClock() {
  const el = document.getElementById('live-time');
  if (!el) return;
  const tick = () => {
    const now = new Date();
    el.textContent = now.toLocaleString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  };
  tick();
  setInterval(tick, 1000);
}

// ── API Helpers ────────────────────────────────────────────────────────────────
async function apiFetch(url) {
  const res = await fetch(API + url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function apiPost(url, body) {
  const res = await fetch(API + url, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(body)
  });
  return res.json();
}

// ── Init ───────────────────────────────────────────────────────────────────────
async function init() {
  startClock();

  try {
    const [overview, stats, suggestions] = await Promise.all([
      apiFetch('/api/overview'),
      apiFetch('/api/all_stats'),
      apiFetch('/api/suggestions')
    ]);

    allStats = stats;

    renderKPIs(overview);
    renderPieChart(stats);
    renderOverallHourly(stats);
    renderApplianceBtns(Object.keys(stats));
    renderSuggestions(suggestions);
    renderMetricsTable(stats);
    renderMetricsCharts(stats);
    populatePredSelect(Object.keys(stats));

    // Auto-select first appliance
    const first = Object.keys(stats)[0];
    if (first) selectAppliance(first);

  } catch (err) {
    console.error('Init failed:', err);
    document.getElementById('kpi-grid').innerHTML =
      `<p style="color:#ff4d6d;padding:1rem">⚠ Failed to load data. Is Flask running?<br><small>${err.message}</small></p>`;
  }
}

// ── KPI Cards ──────────────────────────────────────────────────────────────────
function renderKPIs(ov) {
  const kpis = [
    { icon: '⚡', val: ov.total_kwh.toLocaleString() + ' kWh', label: 'Total Energy' },
    { icon: '🔌', val: ov.num_appliances,                       label: 'Appliances' },
    { icon: '🤖', val: ov.models_loaded > 0 ? ov.models_loaded + ' LSTM' : 'Stat. Mode', label: 'AI Models' },
    { icon: '📈', val: (ov.avg_r2 * 100).toFixed(1) + '%',     label: 'Avg R² Score' },
    { icon: '🏆', val: ov.top_consumer,                         label: 'Top Consumer' }
  ];

  document.getElementById('kpi-grid').innerHTML = kpis.map(k => `
    <div class="kpi-card">
      <span class="kpi-icon">${k.icon}</span>
      <div class="kpi-value">${k.val}</div>
      <div class="kpi-label">${k.label}</div>
    </div>
  `).join('');
}

// ── Pie Chart ──────────────────────────────────────────────────────────────────
function renderPieChart(stats) {
  const labels = Object.keys(stats);
  const vals   = labels.map(a => stats[a].total_kwh);

  new Chart(document.getElementById('pie-chart').getContext('2d'), {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: vals,
        backgroundColor: CHART_PALETTE,
        borderWidth: 2,
        borderColor: '#111c2e',
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: '#5a7a9e',
            font: { size: 11 },
            boxWidth: 10,
            padding: 10
          }
        },
        tooltip: {
          backgroundColor: 'rgba(13,22,37,0.95)',
          titleColor: '#00d4ff',
          bodyColor:  '#dce8f8',
          borderColor: '#1e3050',
          borderWidth: 1,
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.raw.toLocaleString()} kWh`
          }
        }
      },
      cutout: '60%'
    }
  });
}

// ── Overall Hourly Chart ───────────────────────────────────────────────────────
async function renderOverallHourly(stats) {
  // Use first appliance for hourly pattern display
  const firstApp = Object.keys(stats)[0];
  const d = await apiFetch('/api/appliance/' + encodeURIComponent(firstApp));
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`);

  new Chart(document.getElementById('hourly-chart').getContext('2d'), {
    type: 'bar',
    data: {
      labels: hours,
      datasets: [{
        label: firstApp + ' avg (kWh)',
        data:  d.hourly_avg,
        backgroundColor: 'rgba(0, 212, 255, 0.55)',
        borderColor:     'rgba(0, 212, 255, 0.9)',
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: chartBaseOptions()
  });
}

// ── Appliance Buttons ──────────────────────────────────────────────────────────
function renderApplianceBtns(apps) {
  document.getElementById('appliance-btns').innerHTML = apps.map(a => `
    <div class="app-btn" id="btn-${a.replace(/ /g,'_')}" onclick="selectAppliance('${a}')">
      <span class="app-icon">${APP_ICONS[a] || '⚡'}</span>
      ${a}
    </div>
  `).join('');
}

function populatePredSelect(apps) {
  const sel = document.getElementById('pred-app');
  sel.innerHTML = '';
  apps.forEach(a => {
    const o = new Option((APP_ICONS[a] || '⚡') + ' ' + a, a);
    sel.add(o);
  });
}

// ── Select Appliance ───────────────────────────────────────────────────────────
async function selectAppliance(name) {
  // Update button highlights
  document.querySelectorAll('.app-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById('btn-' + name.replace(/ /g, '_'));
  if (btn) btn.classList.add('active');

  currentApp = name;

  const d = await apiFetch('/api/appliance/' + encodeURIComponent(name));

  // Update titles
  const icon = APP_ICONS[name] || '⚡';
  document.getElementById('app-chart-title').textContent =
    `${icon} ${name} — Actual vs Predicted (7 days)`;
  document.getElementById('app-daily-title').textContent =
    `${name} — Daily Totals (14 days)`;
  document.getElementById('app-hourly-title').textContent =
    `${name} — Hourly Average Pattern`;

  // Stats row
  document.getElementById('app-stat-row').innerHTML = `
    <div class="stat-item">
      <div class="s-val">${d.total_kwh.toLocaleString()} kWh</div>
      <div class="s-lbl">Total</div>
    </div>
    <div class="stat-item">
      <div class="s-val">${d.avg_kwh}</div>
      <div class="s-lbl">Avg / hr</div>
    </div>
    <div class="stat-item">
      <div class="s-val">${d.max_kwh}</div>
      <div class="s-lbl">Peak</div>
    </div>
    <div class="stat-item">
      <div class="s-val" style="color:${r2Color(d.r2 || 0)}">${d.r2 ?? '—'}</div>
      <div class="s-lbl">R² Score</div>
    </div>
    <div class="stat-item">
      <div class="s-val">${d.mae}</div>
      <div class="s-lbl">MAE (kWh)</div>
    </div>
  `;

  // ── Line Chart: Actual vs Predicted
  if (appLineChart) appLineChart.destroy();
  appLineChart = new Chart(
    document.getElementById('app-line-chart').getContext('2d'),
    {
      type: 'line',
      data: {
        labels: d.timestamps,
        datasets: [
          {
            label:       'Actual',
            data:        d.actual_vals,
            borderColor: '#00d4ff',
            backgroundColor: 'rgba(0,212,255,0.06)',
            tension:     0.3,
            pointRadius: 0,
            borderWidth: 2,
            fill: true
          },
          {
            label:       'Predicted',
            data:        d.pred_vals,
            borderColor: '#ffb830',
            backgroundColor: 'transparent',
            tension:     0.3,
            pointRadius: 0,
            borderWidth: 2,
            borderDash:  [5, 4]
          }
        ]
      },
      options: chartBaseOptions()
    }
  );

  // ── Daily Bar Chart
  if (appDailyChart) appDailyChart.destroy();
  appDailyChart = new Chart(
    document.getElementById('app-daily-chart').getContext('2d'),
    {
      type: 'bar',
      data: {
        labels: d.daily_labels,
        datasets: [{
          label:           'Daily kWh',
          data:            d.daily_vals,
          backgroundColor: 'rgba(157, 111, 255, 0.65)',
          borderColor:     'rgba(157, 111, 255, 0.9)',
          borderWidth: 1,
          borderRadius: 5
        }]
      },
      options: chartBaseOptions()
    }
  );

  // ── Hourly Pattern
  if (appHourlyChart) appHourlyChart.destroy();
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`);
  appHourlyChart = new Chart(
    document.getElementById('app-hourly-chart').getContext('2d'),
    {
      type: 'line',
      data: {
        labels: hours,
        datasets: [{
          label:           'Avg kWh/hr',
          data:            d.hourly_avg,
          borderColor:     '#00e5a0',
          backgroundColor: 'rgba(0, 229, 160, 0.12)',
          fill:       true,
          tension:    0.4,
          pointRadius: 3,
          pointBackgroundColor: '#00e5a0',
          borderWidth: 2
        }]
      },
      options: chartBaseOptions()
    }
  );
}

// ── Prediction ─────────────────────────────────────────────────────────────────
async function runPrediction() {
  const app    = document.getElementById('pred-app').value;
  const valRaw = parseFloat(document.getElementById('pred-val').value);
  const val    = isNaN(valRaw)
    ? (allStats[app]?.avg_kwh || 2)
    : valRaw;

  // Generate 24-hour history with natural variation
  const hist = Array.from({ length: 24 }, (_, i) => {
    const variation = (Math.random() - 0.5) * val * 0.35;
    const trend = val * 0.15 * Math.sin(2 * Math.PI * i / 24);
    return Math.max(0, val + variation + trend);
  });

  const btn = document.getElementById('pred-btn');
  btn.disabled = true;
  btn.textContent = 'Predicting...';

  try {
    const result = await apiPost('/api/predict', {
      appliance:       app,
      historical_data: hist
    });

    document.getElementById('pred-output').textContent = result.prediction;
    document.getElementById('pred-unit').textContent   = ' kWh';

    const confClass = `badge-${result.confidence}`;
    document.getElementById('pred-meta').innerHTML = `
      <span class="badge badge-lstm">${result.model_type}</span>
      <span class="badge ${confClass}">Confidence: ${result.confidence.toUpperCase()}</span>
      <span style="color:var(--muted);font-size:.8rem;font-family:var(--font-mono)">
        R²: ${result.r2} &nbsp;|&nbsp; MAE: ${result.mae} kWh
      </span>
    `;

    const resultEl = document.getElementById('predict-result');
    resultEl.style.display = 'block';
    resultEl.style.animation = 'none';
    void resultEl.offsetWidth;
    resultEl.style.animation = 'fadeIn 0.3s ease';

  } catch (err) {
    console.error('Prediction failed:', err);
  } finally {
    btn.disabled = false;
    btn.textContent = '⚡ Predict Next Hour';
  }
}

// Allow Enter key on input
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('pred-val');
  if (input) {
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') runPrediction();
    });
  }
});

// ── Suggestions ────────────────────────────────────────────────────────────────
function renderSuggestions(suggestions) {
  document.getElementById('suggestions-grid').innerHTML = suggestions.map(s => `
    <div class="suggestion-card" style="border-left-color:${s.color}">
      <div class="sug-header">
        <span class="sug-icon">${s.icon}</span>
        <span class="sug-title">${s.title}</span>
        <span class="sug-badge" style="background:${s.color}22;color:${s.color}">
          ${s.saving_potential}
        </span>
      </div>
      <div class="sug-detail">${s.detail}</div>
      <div class="sug-tip">💡 ${s.tip}</div>
    </div>
  `).join('');
}

// ── Metrics Table ──────────────────────────────────────────────────────────────
function renderMetricsTable(stats) {
  document.getElementById('metrics-tbody').innerHTML = Object.entries(stats).map(
    ([app, s]) => {
      const r2Pct = Math.max(0, Math.min(100, s.r2 * 100));
      const col   = r2Color(s.r2);
      return `
        <tr>
          <td>${APP_ICONS[app] || '⚡'} ${app}</td>
          <td><span class="badge badge-lstm">${s.has_model ? 'LSTM' : 'Fallback'}</span></td>
          <td style="font-family:var(--font-mono)">${s.mae}</td>
          <td style="font-family:var(--font-mono)">${s.rmse}</td>
          <td style="color:${col};font-family:var(--font-mono);font-weight:700">${s.r2}</td>
          <td>
            <div class="r2-bar">
              <div class="r2-fill" style="width:${r2Pct}%;background:${col}"></div>
            </div>
          </td>
          <td style="color:var(--muted);font-family:var(--font-mono)">${s.avg_kwh} kWh</td>
        </tr>
      `;
    }
  ).join('');
}

// ── Metrics Charts ─────────────────────────────────────────────────────────────
function renderMetricsCharts(stats) {
  const labels = Object.keys(stats);
  const r2vals = labels.map(a => stats[a].r2);
  const mavals = labels.map(a => stats[a].mae);
  const r2cols = r2vals.map(r2Color);

  // R² Chart
  new Chart(document.getElementById('r2-chart').getContext('2d'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label:           'R² Score',
        data:            r2vals,
        backgroundColor: r2cols.map(c => c + 'aa'),
        borderColor:     r2cols,
        borderWidth: 1,
        borderRadius: 5
      }]
    },
    options: chartBaseOptions({
      scales: {
        x: { ticks: { color: '#3d5a7a', font: { size: 9 } }, grid: { color: 'rgba(30,48,80,0.5)' } },
        y: { min: -1, max: 1, ticks: { color: '#3d5a7a', font: { size: 10 } }, grid: { color: 'rgba(30,48,80,0.5)' } }
      }
    })
  });

  // MAE Chart
  new Chart(document.getElementById('mae-chart').getContext('2d'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label:           'MAE (kWh)',
        data:            mavals,
        backgroundColor: 'rgba(255, 184, 48, 0.6)',
        borderColor:     'rgba(255, 184, 48, 0.9)',
        borderWidth: 1,
        borderRadius: 5
      }]
    },
    options: chartBaseOptions()
  });
}

// ── Boot ───────────────────────────────────────────────────────────────────────
init();
