(function (global) {
    "use strict";

    function Dashboard() {
        this.data = global.homeFinanceDashboard;
    }

    Dashboard.prototype.init = function () {
        if (!this.data) {
            return;
        }
        this.renderCategoryChart();
        this.renderMonthlyChart();
    };

    Dashboard.prototype.renderCategoryChart = function () {
        var canvas = document.getElementById("chart-categories");
        if (!canvas) {
            return;
        }
        var chart = new global.HomeFinanceCharts.BarChart(canvas);
        chart.render(this.data.byCategory || [], this.data.categoryTotals || []);
    };

    Dashboard.prototype.renderMonthlyChart = function () {
        var canvas = document.getElementById("chart-months");
        if (!canvas) {
            return;
        }
        var chart = new global.HomeFinanceCharts.BarChart(canvas);
        chart.render(this.data.byMonth || [], this.data.monthTotals || []);
    };

    global.addEventListener("DOMContentLoaded", function () {
        new Dashboard().init();
    });
})(window);
