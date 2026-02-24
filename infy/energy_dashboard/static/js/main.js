document.addEventListener('DOMContentLoaded', function () {
    fetchStats();
});

function fetchStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(stats => {
            if (stats.error) return;

            animateValue('stat-avg-actual', 0, stats.avg_actual, 1000);
            animateValue('stat-avg-predicted', 0, stats.avg_predicted, 1000);
            animateValue('stat-peak', 0, stats.max_actual, 1000);
            document.getElementById('stat-count').textContent = stats.total_readings;
        })
        .catch(err => console.error('Error fetching stats:', err));
}

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = (progress * (end - start) + start).toFixed(2);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}
