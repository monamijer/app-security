// Helper global pour les graphiques Chart.js
window.AC = window.AC || {};

AC.makeBar = function(canvasId, labels, values, color = '#1e3a8a') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Valeur',
                data: values,
                backgroundColor: color,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
};

AC.makeDoughnut = function(canvasId, labels, values, colors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{ data: values, backgroundColor: colors }]
        },
        options: { responsive: true }
    });
};