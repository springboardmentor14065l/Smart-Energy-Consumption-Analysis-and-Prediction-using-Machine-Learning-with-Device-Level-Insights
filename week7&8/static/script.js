/* ══════════════════════════════════════════════
    Dashboard — script.js

let overallChart, deviceChart, pieChart;
let applianceList        = [];
let deviceStats          = {};   // { device: { mean, std } }
let currentOverallPeriod = 'daily';
let currentDevicePeriod  = 'daily';

const COLORS = ['#00d4ff','#10b981','#f59e0b','#7c3aed','#ef4444',
                '#ec4899','#14b8a6','#f97316','#a78bfa','#84cc16'];

// ══════════════════════════════════════════════
// NAVIGATION
// ══════════════════════════════════════════════
function showPage(name, navEl) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  if (navEl) navEl.classList.add('active');
  if (name === 'devices')  buildRankingTable();
  if (name === 'insights') loadInsights();
}

// ══════════════════════════════════════════════
// PERIOD TOGGLES
// ══════════════════════════════════════════════
function switchPeriod(period, btn) {
  currentOverallPeriod = period;
  btn.closest('.period-toggle').querySelectorAll('.period-btn')
     .forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('period-badge').textContent =
    period.charAt(0).toUpperCase() + period.slice(1);
  loadOverall();
}

function switchDevicePeriod(period, btn) {
  currentDevicePeriod = period;
  btn.closest('.period-toggle').querySelectorAll('.period-btn')
     .forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

// ══════════════════════════════════════════════
// CHART DEFAULTS
// ══════════════════════════════════════════════
function chartDefaults() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#94a3b8', font: { family: 'DM Sans', size: 12 } } },
      tooltip: {
        backgroundColor: '#111827', borderColor: '#1f2d45', borderWidth: 1,
        titleColor: '#00d4ff', bodyColor: '#94a3b8'
      }
    },
    scales: {
      x: { ticks: { color: '#475569', font: { size: 10 } }, grid: { color: '#1a2235' } },
      y: { ticks: { color: '#475569', font: { size: 10 } }, grid: { color: '#1a2235' } }
    }
  };
}

// ══════════════════════════════════════════════
// SMART LEVEL CLASSIFIER — std deviation bands
//
//  High     : prediction > mean + std
//  Moderate : mean - std <= prediction <= mean + std
//  Low      : prediction < mean - std
//
//  Fallback : if std ≈ 0 (very stable device),
//             use ±10% of mean as the band
// ══════════════════════════════════════════════
function classifyLevel(device, prediction) {
  const stats = deviceStats[device];
  if (!stats) return { label: 'N/A', cls: '' };

  const { mean, std } = stats;
  const band = std > 0.0001 ? std : mean * 0.1;

  if (prediction > mean + band) return { label: '▲ High',     cls: 'level-high' };
  if (prediction < mean - band) return { label: '▼ Low',      cls: 'level-low' };
  return                               { label: '● Moderate', cls: 'level-moderate' };
}

// ══════════════════════════════════════════════
// INIT
// ══════════════════════════════════════════════
async function init() {
  const [appRes, statsRes, insRes] = await Promise.all([
    fetch('/api/appliances').then(r => r.json()),
    fetch('/api/device_stats').then(r => r.json()),
    fetch('/api/insights').then(r => r.json())
  ]);

  applianceList = appRes.appliances;
  deviceStats   = statsRes;

  // Populate both device dropdowns
  ['device-select', 'pred-device-select'].forEach(id => {
    const sel = document.getElementById(id);
    sel.innerHTML = '';
    applianceList.forEach(a => {
      const o = document.createElement('option');
      o.value = a; o.textContent = a;
      sel.appendChild(o);
    });
  });

  // Stat cards
  document.getElementById('stat-devices').textContent = applianceList.length;
  document.getElementById('stat-high').textContent    = insRes.highest_device;
  document.getElementById('stat-low').textContent     = insRes.lowest_device;

  await loadOverall();
  loadActualPieChart();
}

// ══════════════════════════════════════════════
// OVERALL TREND CHART
// ══════════════════════════════════════════════
async function loadOverall() {
  const data = await fetch(`/api/overall?period=${currentOverallPeriod}`).then(r => r.json());

  const total = data.values.reduce((a, b) => a + b, 0);
  document.getElementById('stat-total').textContent = total.toFixed(1);

  if (overallChart) overallChart.destroy();

  overallChart = new Chart(document.getElementById('overallChart'), {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [{
        label: 'Energy (kWh)',
        data: data.values,
        borderColor: '#00d4ff',
        backgroundColor: 'rgba(0,212,255,0.07)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 5
      }]
    },
    options: chartDefaults()
  });
}

// ══════════════════════════════════════════════
// ACTUAL CONSUMPTION PIE — real historical share
// ══════════════════════════════════════════════
async function loadActualPieChart() {
  const data = await fetch('/api/device_totals').then(r => r.json());

  if (pieChart) pieChart.destroy();

  pieChart = new Chart(document.getElementById('pieChart'), {
    type: 'doughnut',
    data: {
      labels: Object.keys(data),
      datasets: [{
        data: Object.values(data),
        backgroundColor: COLORS,
        borderWidth: 2,
        borderColor: '#111827'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 }, padding: 10 } },
        tooltip: {
          backgroundColor: '#111827', borderColor: '#1f2d45', borderWidth: 1,
          titleColor: '#00d4ff', bodyColor: '#94a3b8',
          callbacks: {
            label: ctx => {
              const total = ctx.dataset.data.reduce((a,b)=>a+b,0);
              const pct   = ((ctx.parsed / total) * 100).toFixed(1);
              return ` ${ctx.label}: ${ctx.parsed.toFixed(2)} kWh (${pct}%)`;
            }
          }
        }
      }
    }
  });
}

// ══════════════════════════════════════════════
// DEVICE CHART
// ══════════════════════════════════════════════
async function loadDevice() {
  const device = document.getElementById('device-select').value;
  if (!device) return;

  document.getElementById('device-chart-title').textContent = `// ${device.toUpperCase()}`;

  const data = await fetch(
    `/api/device?device=${encodeURIComponent(device)}&period=${currentDevicePeriod}`
  ).then(r => r.json());

  if (deviceChart) deviceChart.destroy();

  deviceChart = new Chart(document.getElementById('deviceChart'), {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [{
        label: `${device} (kWh)`,
        data: data.values,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16,185,129,0.07)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 5
      }]
    },
    options: chartDefaults()
  });
}

// ══════════════════════════════════════════════
// RANKING TABLE (devices page)
// ══════════════════════════════════════════════
async function buildRankingTable() {
  const container = document.getElementById('ranking-table');
  const data      = await fetch('/api/device_totals').then(r => r.json());
  const sorted    = Object.entries(data).sort((a,b) => b[1]-a[1]);
  const maxVal    = sorted[0][1];

  container.innerHTML = `
    <table>
      <thead>
        <tr><th>#</th><th>Device</th><th>Total (kWh)</th><th>Share</th></tr>
      </thead>
      <tbody>
        ${sorted.map(([dev, val], i) => `
          <tr>
            <td><span class="rank-badge">${String(i+1).padStart(2,'0')}</span></td>
            <td>${dev}</td>
            <td style="font-family:var(--font-mono); color:var(--accent)">${val.toFixed(2)}</td>
            <td>
              <div class="bar-row">
                <div class="bar-bg">
                  <div class="bar-fill" style="width:${(val/maxVal*100).toFixed(1)}%"></div>
                </div>
                <span style="font-size:11px;color:var(--muted);width:35px">${(val/maxVal*100).toFixed(0)}%</span>
              </div>
            </td>
          </tr>`).join('')}
      </tbody>
    </table>`;
}

// ══════════════════════════════════════════════
// SINGLE DEVICE PREDICTION
// ══════════════════════════════════════════════
async function runSinglePredict() {
  const device    = document.getElementById('pred-device-select').value;
  const container = document.getElementById('single-pred-result');

  container.innerHTML = '<div class="loading" style="height:160px"><div class="spinner"></div> Running LSTM model…</div>';

  const data = await fetch('/api/predict', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ device })
  }).then(r => r.json());

  const { label, cls } = classifyLevel(device, data.prediction);
  const stats = deviceStats[device];

  container.innerHTML = `
    <div class="pred-device-name">${device}</div>
    <div class="pred-value">${data.prediction.toFixed(4)}<span class="pred-unit"> kWh</span></div>
    <div style="margin-top:16px">
      <span class="level-pill ${cls}">${label}</span>
    </div>
    <div style="margin-top:16px; display:flex; justify-content:center; gap:24px; font-size:12px; color:var(--muted);">
      <div>Mean &nbsp;<strong style="color:var(--text); font-family:var(--font-mono)">${stats ? stats.mean.toFixed(4) : '—'}</strong></div>
      <div>Std Dev &nbsp;<strong style="color:var(--text); font-family:var(--font-mono)">${stats ? stats.std.toFixed(4) : '—'}</strong></div>
    </div>
    <p style="color:var(--muted); font-size:11px; margin-top:10px;">
      Next 1-hour forecast vs this device's historical baseline
    </p>`;
}

// ══════════════════════════════════════════════
// ALL DEVICES PREDICTION TABLE
// ══════════════════════════════════════════════
async function predictAllTable() {
  const container = document.getElementById('all-pred-table');
  container.innerHTML = '<div class="loading" style="height:180px"><div class="spinner"></div> Running all LSTM models…</div>';

  const data   = await fetch('/api/predict_all').then(r => r.json());
  const sorted = Object.entries(data).sort((a,b) => b[1]-a[1]);

  container.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Device</th>
          <th>Forecast (kWh)</th>
          <th>Mean</th>
          <th>Std Dev</th>
          <th>Level</th>
        </tr>
      </thead>
      <tbody>
        ${sorted.map(([dev, val]) => {
          const { label, cls } = classifyLevel(dev, val);
          const s = deviceStats[dev];
          return `<tr>
            <td>${dev}</td>
            <td style="font-family:var(--font-mono); color:var(--accent)">${val.toFixed(4)}</td>
            <td style="font-family:var(--font-mono); color:var(--muted)">${s ? s.mean.toFixed(4) : '—'}</td>
            <td style="font-family:var(--font-mono); color:var(--muted)">${s ? s.std.toFixed(4) : '—'}</td>
            <td><span class="level-pill ${cls}">${label}</span></td>
          </tr>`;
        }).join('')}
      </tbody>
    </table>`;
}

// ══════════════════════════════════════════════
// INSIGHTS
// ══════════════════════════════════════════════
async function loadInsights() {
  const data = await fetch('/api/insights').then(r => r.json());

  document.getElementById('insight-main').innerHTML = `
    <div class="insight-icon">🔥</div>
    <div class="insight-text">
      <div class="insight-title">Top Energy Consumer</div>
      <div class="insight-body">
        <strong>${data.highest_device}</strong> leads total usage at ${data.highest_value.toFixed(2)} kWh.
      </div>
    </div>
    <div class="tip-badge">⚠ Monitor closely</div>`;

  const tips = [
    { icon:'⚡', title:'Peak Hours',
      body:`<strong>${data.highest_device}</strong> consumes ${data.highest_value.toFixed(2)} kWh total. Schedule it outside 6–9 PM to reduce costs.` },
    { icon:'🌙', title:'Night Shift',
      body:`Dishwashers and washing machines used at night can reduce energy bills by up to 30% on time-of-use tariffs.` },
    { icon:'🔋', title:'Standby Drain',
      body:`Devices in standby account for ~10% of household energy. Smart plugs for <strong>${data.lowest_device}</strong> can eliminate phantom loads.` },
    { icon:'📊', title:'Efficiency Win',
      body:`<strong>${data.lowest_device}</strong> is your most efficient device at ${data.lowest_value.toFixed(2)} kWh — a great benchmark for others.` }
  ];

  document.getElementById('tips-section').innerHTML = tips.map(t => `
    <div style="display:flex;gap:16px;padding:16px 0;border-bottom:1px solid var(--border)">
      <div style="font-size:22px">${t.icon}</div>
      <div>
        <div style="font-size:11px;color:var(--muted);margin-bottom:4px;text-transform:uppercase;letter-spacing:1px">${t.title}</div>
        <div style="font-size:14px;line-height:1.6">${t.body}</div>
      </div>
    </div>`).join('');
}

// ══════════════════════════════════════════════
// BOOT
// ══════════════════════════════════════════════
window.onload = init;
