let chartInstances = {};

async function fetchPersonalizedData() {
    try {
        const response = await fetch('/api/personalized-insights');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const result = await response.json();
        console.log('API Payload:', result);
        if (result.status === 'success') {
            const data = result.data;

            // Update Persona & Score
            document.getElementById('persona-type').textContent = data.energy_persona;
            document.getElementById('efficiency-score').textContent = data.efficiency_score;

            // Render Persona Characteristics
            const charContainer = document.getElementById('persona-characteristics');
            charContainer.innerHTML = '';
            if (data.persona_details && data.persona_details.characteristics) {
                data.persona_details.characteristics.forEach(char => {
                    const li = document.createElement('li');
                    li.textContent = char;
                    charContainer.appendChild(li);
                });
            }

            // Render Priority Order
            const priorityContainer = document.getElementById('persona-priority');
            priorityContainer.innerHTML = '';
            if (data.persona_details && data.persona_details.priority) {
                data.persona_details.priority.forEach(app => {
                    const li = document.createElement('li');
                    li.textContent = app;
                    priorityContainer.appendChild(li);
                });
            }

            /* 
            // Update Goal Progress (Removed as requested)
            document.getElementById('goal-status').textContent = data.goal_progress;
            const progressPercent = parseFloat(data.goal_progress) || 0;
            document.getElementById('goal-progress-bar').style.width = Math.min(100, progressPercent) + '%';
            */

            // Update Bill
            document.getElementById('estimated-bill').textContent = data.projected_monthly_bill;
            const breakdownContainer = document.getElementById('bill-breakdown');
            breakdownContainer.innerHTML = '';

            data.appliance_breakdown.forEach(item => {
                const div = document.createElement('div');
                div.className = 'bill-item';
                div.innerHTML = `
                    <div>
                        <strong>${item.appliance}</strong><br>
                        <span class="kwh-label">${item.kwh} kWh</span>
                    </div>
                    <span>₹${item.cost.toLocaleString()}</span>
                `;
                breakdownContainer.appendChild(div);
            });

            // Update Prediction
            if (document.getElementById('prediction-value'))
                document.getElementById('prediction-value').textContent = data.forecast_next_hour;
            if (document.getElementById('prediction-impact'))
                document.getElementById('prediction-impact').textContent = "Based on " + data.energy_persona;

            // Update Goal Summary
            document.getElementById('goal-summary-text').textContent = data.goal_summary;

            // Update Alerts
            const alertBox = document.getElementById('alert-box');
            alertBox.innerHTML = '';
            if (data.alerts && data.alerts.length > 0) {
                alertBox.classList.remove('hidden');
                data.alerts.forEach(alert => {
                    const div = document.createElement('div');
                    div.className = `alert-item ${alert.priority}`;
                    div.innerHTML = `⚠️ <strong>${alert.title}:</strong> ${alert.msg}`;
                    alertBox.appendChild(div);
                });
            } else {
                alertBox.classList.add('hidden');
            }

            // Update Rich Suggestions
            const container = document.getElementById('suggestions-container');
            container.innerHTML = '';
            const icons = { 'cooling': '🌬️', 'heating': '🔥', 'appliance': '🍽️', 'digital': '💻', 'kitchen': '🍳', 'vampire': '🌙', 'prediction': '🔮', 'solar': '☀️', 'general': '💡' };

            data.suggestions.forEach(ins => {
                const div = document.createElement('div');
                div.className = `suggestion-item level-${ins.level || 'info'}`;

                let actionsHtml = '';
                if (ins.actions) {
                    actionsHtml = `<ul class="suggestion-actions">${ins.actions.map(a => `<li>${a}</li>`).join('')}</ul>`;
                }

                const priorityHtml = ins.priority ? `<span class="priority-badge ${ins.priority}">${ins.priority} Priority</span>` : '';
                const impactHtml = ins.impact ? `<div class="impact-label">⭐️ Impact: ${ins.impact}</div>` : '';

                div.innerHTML = `
                    <div style="display: flex; gap: 15px; align-items: flex-start;">
                        <span style="font-size: 2rem;">${icons[ins.type] || '💡'}</span>
                        <div style="flex: 1;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <strong>${ins.title}</strong>
                                ${priorityHtml}
                            </div>
                            <div class="suggestion-header">${ins.header}</div>
                            <div class="suggestion-insight">${ins.insight}</div>
                            <div style="color: var(--text-main); font-weight: 500;">Recommendation: ${ins.recommendation}</div>
                            <div class="suggestion-savings">💰 Estimated Impact: ${ins.savings}</div>
                            ${impactHtml}
                            ${actionsHtml}
                        </div>
                    </div>
                `;
                container.appendChild(div);
            });

            // Update Savings Summary Table
            document.getElementById('total-savings-val').textContent = data.savings_summary.total;
            document.getElementById('total-savings-percent').textContent = data.savings_summary.percent;

            // Update Graphs
            updateGraphsFromPayload(data.graphs_data);
        }
    } catch (error) {
        console.error('Error fetching personalized data:', error);
    }
}

function updateGraphsFromPayload(graphs) {
    // 1. Daily Usage Trend
    const dailyLabels = graphs.daily_usage.map(d => d.date);
    const dailyValues = graphs.daily_usage.map(d => d.value);
    renderChart('hourlyChart', 'line', dailyLabels, dailyValues, 'Daily kWh', '#00d7ff');

    // 2. Appliance Mix
    const appLabels = graphs.appliance_split.map(a => a.label);
    const appValues = graphs.appliance_split.map(a => a.value);
    renderChart('deviceChart', 'doughnut', appLabels, appValues, 'Energy Mix', [
        '#00d7ff', '#00af00', '#f59e0b', '#ef4444', '#8b5cf6'
    ]);
}

async function openProfile() {
    try {
        const response = await fetch('/api/profile');
        const data = await response.json();
        if (data.status === 'success') {
            const profile = data.profile;
            const form = document.getElementById('onboarding-form');
            // Pre-fill form
            form.elements['name'].value = profile.name;
            form.elements['house_size'].value = profile.house_size;
            form.elements['residents'].value = profile.residents;
            form.elements['goal'].value = profile.goal;
            form.elements['lifestyle_pattern'].value = profile.lifestyle_pattern;
            form.elements['tariff_type'].value = profile.tariff_type;

            document.getElementById('onboarding-modal').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error opening profile:', error);
    }
}


async function fetchPrediction() {
    try {
        const response = await fetch('/api/predict');
        const data = await response.json();
        if (data.status === 'success') {
            document.getElementById('prediction-value').textContent = data.prediction + ' kWh';
        }
    } catch (error) {
        console.error('Error fetching prediction:', error);
    }
}

async function updateCharts() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();

        renderChart('hourlyChart', 'line', data.hourly.labels, data.hourly.values, 'Hourly Usage', '#00d7ff');
        renderChart('deviceChart', 'doughnut', data.devices.labels, data.devices.values, 'Energy Mix', [
            '#00d7ff', '#00af00', '#f59e0b', '#ef4444', '#8b5cf6'
        ]);
    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

function renderChart(canvasId, type, labels, values, label, color) {
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas ${canvasId} not found`);
        return;
    }
    const ctx = canvas.getContext('2d');
    chartInstances[canvasId] = new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: Array.isArray(color) ? color : color + '33',
                borderColor: Array.isArray(color) ? '#ffffff33' : color,
                borderWidth: 2,
                fill: type === 'line',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: type === 'doughnut', labels: { color: '#94a3b8' } }
            },
            scales: type !== 'doughnut' ? {
                y: { grid: { color: '#ffffff11' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
            } : {}
        }
    });
}

function handleOnboarding(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    fetch('/api/onboarding', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(result => {
            if (result.status === 'success') {
                // Hard reload to ensure server-side is synced and modal hides correctly
                window.location.reload();
            } else {
                alert("Error: " + result.message);
            }
        })
        .catch(err => console.error("Onboarding failed:", err));
}


document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('onboarding-form');
    if (form) form.addEventListener('submit', handleOnboarding);
    fetchPersonalizedData();
});
