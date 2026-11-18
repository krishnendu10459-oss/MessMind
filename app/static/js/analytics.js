/**
 * AI-POWERED FOOD WASTE PREDICTION SYSTEM
 * Analytics Visualizations: analytics.js
 */

document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/analytics-charts")
        .then((response) => response.json())
        .then((data) => {
            if (!data) return;

            renderMenuWasteChart(data.menu_analysis);
            renderMealDistributionChart(data.meal_distribution);
            renderFullWasteTrendChart(data.trend);
        })
        .catch((error) => console.error("Error loading analytics charts:", error));
});

function renderMenuWasteChart(menuData) {
    const ctx = document.getElementById("menuWasteChart");
    if (!ctx || !menuData) return;

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: menuData.menus,
            datasets: [
                {
                    label: "Average Wasted Meals per Session",
                    data: menuData.avg_wastes,
                    backgroundColor: "rgba(245, 124, 0, 0.75)",
                    borderColor: "#f57c00",
                    borderWidth: 1,
                    borderRadius: 4,
                },
            ],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Avg Waste: ${context.parsed.x} meals`;
                        },
                    },
                },
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: { display: true, text: "Average Meals Wasted" },
                },
            },
        },
    });
}

function renderMealDistributionChart(mealData) {
    const ctx = document.getElementById("mealDistributionChart");
    if (!ctx || !mealData) return;

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: mealData.labels,
            datasets: [
                {
                    data: mealData.values,
                    backgroundColor: [
                        "rgba(2, 136, 209, 0.8)",
                        "rgba(46, 125, 50, 0.8)",
                        "rgba(245, 124, 0, 0.8)",
                    ],
                    borderColor: "#ffffff",
                    borderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "right",
                    labels: { boxWidth: 14, font: { size: 12 } },
                },
            },
        },
    });
}

function renderFullWasteTrendChart(trendData) {
    const ctx = document.getElementById("fullWasteTrendChart");
    if (!ctx || !trendData) return;

    new Chart(ctx, {
        type: "line",
        data: {
            labels: trendData.dates,
            datasets: [
                {
                    label: "Wasted Meals",
                    data: trendData.wasted_meals,
                    borderColor: "#d32f2f",
                    backgroundColor: "rgba(211, 47, 47, 0.08)",
                    borderWidth: 2,
                    fill: true,
                    tension: 0.25,
                    pointRadius: 3,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "top" },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "Meals Unconsumed" },
                },
                x: {
                    grid: { display: false },
                },
            },
        },
    });
}
