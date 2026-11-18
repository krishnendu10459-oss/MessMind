/**
 * AI-POWERED FOOD WASTE PREDICTION SYSTEM
 * Core UI Script: main.js
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Mobile Sidebar Toggle
    const toggleBtn = document.getElementById("sidebarToggleBtn");
    const sidebar = document.querySelector(".sidebar");

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("open");
        });

        // Close sidebar on click outside on mobile
        document.addEventListener("click", function (e) {
            if (window.innerWidth <= 768 && sidebar.classList.contains("open")) {
                if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
                    sidebar.classList.remove("open");
                }
            }
        });
    }

    // 2. Flash Message Dismissal
    const flashCloses = document.querySelectorAll(".flash-close");
    flashCloses.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const alert = this.closest(".flash-alert");
            if (alert) {
                alert.style.opacity = "0";
                setTimeout(() => alert.remove(), 200);
            }
        });
    });

    // Auto dismiss flash messages after 6 seconds
    setTimeout(function () {
        const alerts = document.querySelectorAll(".flash-alert");
        alerts.forEach(function (alert) {
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 300);
        });
    }, 6000);
});

/**
 * Utility helper to format numbers with commas
 */
function formatNumber(num) {
    if (num === null || num === undefined) return "0";
    return Number(num).toLocaleString();
}
