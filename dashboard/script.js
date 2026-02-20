let charts = {};

window.onload = function () {
    const appliance = document.getElementById("appliance").value;
    loadHistorical(appliance);
    loadSuggestions(appliance);
    loadAnalytics(appliance);
    loadModelComparison(appliance);
};

async function getPrediction() {

    const appliance = document.getElementById("appliance").value;

    const pred = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ appliance })
    });

    const predData = await pred.json();

    document.getElementById("result").innerHTML =
        `Predicted Next Hour: ${predData.next_hour_prediction_kWh.toFixed(2)} kWh`;

    loadHistorical(appliance);
    loadSuggestions(appliance);
    loadAnalytics(appliance);
    loadModelComparison(appliance);
}

async function loadHistorical(appliance) {

    const res = await fetch("http://127.0.0.1:5000/historical", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ appliance })
    });

    const data = await res.json();

    document.getElementById("histHour").innerText = data.hourly_total.toFixed(2);
    document.getElementById("histWeek").innerText = data.weekly_total.toFixed(2);
    document.getElementById("histMonth").innerText = data.monthly_total.toFixed(2);
}

async function loadSuggestions(appliance) {

    const res = await fetch("http://127.0.0.1:5000/suggestions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ appliance })
    });

    const data = await res.json();

    const list = document.getElementById("suggestionList");
    list.innerHTML = "";

    data.suggestions.forEach(s => {
        const li = document.createElement("li");
        li.innerText = s;
        list.appendChild(li);
    });
}

async function loadAnalytics(appliance) {

    const res = await fetch("http://127.0.0.1:5000/analytics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ appliance })
    });

    const data = await res.json();

    createChart("hourlyChart", data.hourly_labels, data.hourly_values, "Hourly");
    createChart("dailyChart", data.daily_labels, data.daily_values, "Daily");
    createChart("weeklyChart", data.weekly_labels, data.weekly_values, "Weekly");
    createChart("monthlyChart", data.monthly_labels, data.monthly_values, "Monthly");
}

async function loadModelComparison(appliance) {

    const res = await fetch("http://127.0.0.1:5000/model_comparison", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ appliance })
    });

    const data = await res.json();

    document.getElementById("lrMae").innerText = data.lr_mae.toFixed(3);
    document.getElementById("lstmMae").innerText = data.lstm_mae.toFixed(3);
    document.getElementById("bestModel").innerText = data.best_model;
}

function createChart(canvasId, labels, values, label) {

    const canvas = document.getElementById(canvasId);
    if (!canvas || !labels || labels.length === 0) return;

    const ctx = canvas.getContext("2d");

    if (charts[canvasId]) charts[canvasId].destroy();

    charts[canvasId] = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: `${label} Consumption (kWh)`,
                data: values,
                borderColor: "#38bdf8",
                backgroundColor: "rgba(56,189,248,0.2)",
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: "Time" } },
                y: { title: { display: true, text: "Energy (kWh)" }, beginAtZero: true }
            }
        }
    });
}