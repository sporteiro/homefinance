(function (global) {
    "use strict";

    function Dashboard() {
        this.data = global.homeFinanceDashboard;
        this.renderers = [];
    }

    Dashboard.prototype.init = function () {
        if (!this.data) {
            return;
        }
        this.renderAll();
        this.observeTheme();
        global.addEventListener("resize", this.renderAll.bind(this));
    };

    Dashboard.prototype.renderAll = function () {
        this.renderers = [];
        this.renderCategoryChart();
        this.renderMonthlyChart();
        this.renderYearlyChart();
    };

    Dashboard.prototype.renderCategoryChart = function () {
        var canvas = document.getElementById("chart-categories");
        if (!canvas) {
            return;
        }
        var legend = document.getElementById("legend-categories");
        var labels = this.data.byCategory || [];
        var values = this.data.categoryTotals || [];

        global.HomeFinanceCharts.renderLegend(legend, labels);

        var chart = new global.HomeFinanceCharts.SimpleBarChart(canvas);
        chart.render(labels, values);

        this.renderers.push(function () {
            chart.render(labels, values);
        });
    };

    Dashboard.prototype.renderMonthlyChart = function () {
        var canvas = document.getElementById("chart-months");
        if (!canvas) {
            return;
        }
        var legend = document.getElementById("legend-months");
        var months = this.data.monthsLast12 || { labels: [], perCategory: {} };
        var names = this.data.categoryNames || [];

        global.HomeFinanceCharts.renderLegend(legend, names);

        var chart = new global.HomeFinanceCharts.StackedBarChart(canvas, names);
        chart.render(months.labels, months.perCategory);

        this.renderers.push(function () {
            chart.render(months.labels, months.perCategory);
        });
    };

    Dashboard.prototype.renderYearlyChart = function () {
        var canvas = document.getElementById("chart-years");
        if (!canvas) {
            return;
        }
        var legend = document.getElementById("legend-years");
        var years = this.data.yearsLast10 || { labels: [], perCategory: {} };
        var names = this.data.categoryNames || [];

        global.HomeFinanceCharts.renderLegend(legend, names);

        var chart = new global.HomeFinanceCharts.GroupedBarChart(canvas, names);
        chart.render(years.labels, years.perCategory);

        this.renderers.push(function () {
            chart.render(years.labels, years.perCategory);
        });
    };

    Dashboard.prototype.observeTheme = function () {
        var self = this;
        var observer = new MutationObserver(function (mutations) {
            for (var i = 0; i < mutations.length; i++) {
                if (mutations[i].attributeName === "data-theme") {
                    self.redrawCharts();
                    return;
                }
            }
        });
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ["data-theme"]
        });
    };

    Dashboard.prototype.redrawCharts = function () {
        for (var i = 0; i < this.renderers.length; i++) {
            this.renderers[i]();
        }
    };

    global.addEventListener("DOMContentLoaded", function () {
        new Dashboard().init();
    });
})(window);
