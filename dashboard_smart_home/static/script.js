
let overallChart;
let deviceChart;
let pieChart;

// ================= LOAD APPLIANCES =================
async function loadAppliances() {
    const res = await fetch("/api/appliances");
    const data = await res.json();

    const select = document.getElementById("device-select");
    select.innerHTML = "";

    data.appliances.forEach(device => {
        const option = document.createElement("option");
        option.value = device;
        option.textContent = device;
        select.appendChild(option);
    });
}

// ================= OVERALL CHART =================
async function loadOverall() {
    const period = document.getElementById("overall-period").value;

    const res = await fetch(`/api/overall?period=${period}`);
    const data = await res.json();

    const ctx = document.getElementById("overallChart");

    if (overallChart) overallChart.destroy();

    overallChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [{
                label: "Energy Consumption (kWh)",
                data: data.values,
                borderColor: "#2563eb",
                backgroundColor: "rgba(37,99,235,0.2)",
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// ================= DEVICE CHART =================
async function loadDevice() {
    const device = document.getElementById("device-select").value;
    const period = document.getElementById("device-period").value;

    if (!device) {
        alert("Please select a device");
        return;
    }

    const res = await fetch(`/api/device?device=${device}&period=${period}`);
    const data = await res.json();

    const ctx = document.getElementById("deviceChart");

    if (deviceChart) deviceChart.destroy();

    deviceChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [{
                label: device + " Consumption",
                data: data.values,
                borderColor: "#16a34a",
                backgroundColor: "rgba(22,163,74,0.2)",
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// ================= SINGLE DEVICE PREDICTION =================
async function predict() {
    const device = document.getElementById("device-select").value;

    if (!device) {
        alert("Select a device first");
        return;
    }

    const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ device: device })
    });

    const data = await res.json();

    document.getElementById("predictionResult").innerText =
        `Next Hour Prediction for ${data.device}: ${data.prediction.toFixed(2)} kWh`;
}

// ================= ALL DEVICE PIE =================
async function predictAll() {
    const res = await fetch("/api/predict_all");
    const data = await res.json();

    const ctx = document.getElementById("pieChart");

    if (pieChart) pieChart.destroy();

    pieChart = new Chart(ctx, {
        type: "pie",
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    "#2563eb",
                    "#16a34a",
                    "#dc2626",
                    "#ca8a04",
                    "#7c3aed",
                    "#ea580c",
                    "#0891b2"
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// ================= INSIGHTS =================
async function loadInsights() {
    const res = await fetch("/api/insights");
    const data = await res.json();

    let suggestion = "";

    if (data.highest_value > 50) {
        suggestion = "⚠ High consumption detected. Reduce usage during peak hours.";
    } else if (data.highest_value > 30) {
        suggestion = "Moderate consumption. Monitor regularly.";
    } else {
        suggestion = "Good energy management!";
    }

    const insightElement = document.getElementById("insightText");
    if (!insightElement) return;

    insightElement.innerHTML =
        `<strong>${data.highest_device}</strong> consumes highest energy 
        (${data.highest_value.toFixed(2)} kWh). <br><br>
        <strong>Suggestion:</strong> ${suggestion}`;
}

// ================= INIT =================
window.onload = async function () {
    await loadAppliances();
    await loadOverall();
    await loadInsights();
};