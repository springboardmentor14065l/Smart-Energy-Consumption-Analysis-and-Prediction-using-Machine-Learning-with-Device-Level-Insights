document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('energyChart').getContext('2d');

    // Gradient for Actual Data
    const gradientActual = ctx.createLinearGradient(0, 0, 0, 400);
    gradientActual.addColorStop(0, 'rgba(59, 130, 246, 0.5)'); // Blue
    gradientActual.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

    // Gradient for Predicted Data
    const gradientPredicted = ctx.createLinearGradient(0, 0, 0, 400);
    gradientPredicted.addColorStop(0, 'rgba(139, 92, 246, 0.5)'); // Purple
    gradientPredicted.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

    let energyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Actual Consumption',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: gradientActual,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Predicted Consumption',
                    data: [],
                    borderColor: '#8b5cf6',
                    backgroundColor: gradientPredicted,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    borderDash: [5, 5],
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: '#9ca3af', usePointStyle: true, boxWidth: 8 }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: true
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b', maxTicksLimit: 10 }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b' },
                    title: { display: true, text: 'Energy (kWh)', color: '#475569' }
                }
            }
        }
    });

    // Fetch Data
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading data:', data.error);
                return;
            }

            // Limit data points to avoid performance issues if too many
            // Taking last 100 points for better visibility if dataset is huge
            const sliceIndex = -200;

            energyChart.data.labels = data.labels.slice(sliceIndex);
            energyChart.data.datasets[0].data = data.actual.slice(sliceIndex);
            energyChart.data.datasets[1].data = data.predicted.slice(sliceIndex);
            energyChart.update();
        })
        .catch(error => console.error('Error fetching data:', error));
});
