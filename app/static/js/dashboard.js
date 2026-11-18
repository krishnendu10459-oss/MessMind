/**
 * AI-POWERED FOOD WASTE PREDICTION SYSTEM
 * Dashboard Visualizations: dashboard.js
 */

document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/chart-data")
        .then((response) => response.json())
        .then((data) => {
            if (!data || !data.dates || data.dates.length === 0) {
                console.log("No chart data available to plot.");
                return;
            }

            renderConsumptionChart(data);
            renderWastePctChart(data);
        })
        .catch((error) => console.error("Error loading dashboard charts:", error));
});

function renderConsumptionChart(data) {
    const ctx = document.getElementById("consumptionChart");
    if (!ctx) return;

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: data.dates,
            datasets: [
                {
                    label: "Prepared Meals",
                    data: data.prepared,
                    backgroundColor: "rgba(2, 136, 209, 0.75)",
                    borderColor: "#0288d1",
                    borderWidth: 1,
                    borderRadius: 4,
                },
                {
                    label: "Consumed Meals",
                    data: data.consumed,
                    backgroundColor: "rgba(46, 125, 50, 0.85)",
                    borderColor: "#2e7d32",
                    borderWidth: 1,
                    borderRadius: 4,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "top",
                    labels: { font: { size: 12 } },
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function (context) {
                            const index = context.dataIndex;
                            const prep = data.prepared[index];
                            const cons = data.consumed[index];
                            const waste = prep - cons;
                            return `Wasted Surplus: ${waste} meals (${data.waste_percentages[index]}%)`;
                        },
                    },
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: "#f1f5f9" },
                    title: { display: true, text: "Meal Count" },
                },
                x: {
                    grid: { display: false },
                },
            },
        },
    });
}

function renderWastePctChart(data) {
    const ctx = document.getElementById("wastePctChart");
    if (!ctx) return;

    new Chart(ctx, {
        type: "line",
        data: {
            labels: data.dates,
            datasets: [
                {
                    label: "Waste Percentage (%)",
                    data: data.waste_percentages,
                    borderColor: "#f57c00",
                    backgroundColor: "rgba(245, 124, 0, 0.1)",
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "top",
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    suggestedMax: 30,
                    grid: { color: "#f1f5f9" },
                    title: { display: true, text: "Waste % of Prepared" },
                },
                x: {
                    grid: { display: false },
                },
            },
        },
    });
}
