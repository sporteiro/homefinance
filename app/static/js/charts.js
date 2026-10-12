(function (global) {
    "use strict";

    var PALETTE = [
        "#2b6cb0",
        "#2c7a7b",
        "#805ad5",
        "#c05621",
        "#718096",
        "#b83280",
        "#38a169",
        "#d69e2e",
        "#319795",
        "#dd6b20"
    ];

    function formatNumber(value) {
        var number = Number(value);
        if (isNaN(number)) {
            return "0";
        }
        return number.toFixed(2);
    }

    function BarChart(canvas) {
        this.canvas = canvas;
        this.context = canvas.getContext("2d");
        this.padding = { top: 16, right: 16, bottom: 48, left: 64 };
        this.barGap = 8;
    }

    BarChart.prototype.render = function (labels, values) {
        if (!labels || labels.length === 0) {
            this.clear();
            this.drawEmptyMessage();
            return;
        }

        this.clear();
        this.drawAxes(labels, values);
        this.drawBars(labels, values);
    };

    BarChart.prototype.clear = function () {
        var ratio = global.devicePixelRatio || 1;
        var rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width * ratio;
        this.canvas.height = rect.height * ratio;
        this.context.setTransform(ratio, 0, 0, ratio, 0, 0);
        this.context.clearRect(0, 0, rect.width, rect.height);
    };

    BarChart.prototype.drawEmptyMessage = function () {
        var rect = this.canvas.getBoundingClientRect();
        this.context.fillStyle = "#656d76";
        this.context.font = "14px system-ui, sans-serif";
        this.context.textAlign = "center";
        this.context.fillText("No data available", rect.width / 2, rect.height / 2);
    };

    BarChart.prototype.drawAxes = function (labels, values) {
        var rect = this.canvas.getBoundingClientRect();
        var maxValue = this.maxValue(values);
        var plot = this.plotArea(rect);

        this.context.strokeStyle = "#dcdfe4";
        this.context.lineWidth = 1;
        this.context.beginPath();
        this.context.moveTo(plot.x, plot.y);
        this.context.lineTo(plot.x, plot.y + plot.height);
        this.context.lineTo(plot.x + plot.width, plot.y + plot.height);
        this.context.stroke();

        this.drawYAxisLabels(plot, maxValue);
    };

    BarChart.prototype.drawYAxisLabels = function (plot, maxValue) {
        var steps = 4;
        this.context.fillStyle = "#656d76";
        this.context.font = "11px system-ui, sans-serif";
        this.context.textAlign = "right";
        this.context.textBaseline = "middle";

        for (var i = 0; i <= steps; i++) {
            var value = (maxValue / steps) * i;
            var y = plot.y + plot.height - (plot.height / steps) * i;
            this.context.fillText(formatNumber(value), plot.x - 8, y);
        }
    };

    BarChart.prototype.drawBars = function (labels, values) {
        var rect = this.canvas.getBoundingClientRect();
        var maxValue = this.maxValue(values);
        var plot = this.plotArea(rect);
        var count = labels.length;
        var slotWidth = plot.width / count;
        var barWidth = Math.max(slotWidth - this.barGap, 4);

        this.context.textAlign = "center";
        this.context.textBaseline = "top";
        this.context.font = "11px system-ui, sans-serif";

        for (var i = 0; i < count; i++) {
            var value = Number(values[i]) || 0;
            var barHeight = maxValue > 0 ? (value / maxValue) * plot.height : 0;
            var x = plot.x + slotWidth * i + (slotWidth - barWidth) / 2;
            var y = plot.y + plot.height - barHeight;

            this.context.fillStyle = PALETTE[i % PALETTE.length];
            this.context.fillRect(x, y, barWidth, barHeight);

            this.context.fillStyle = "#1f2328";
            this.context.fillText(
                String(labels[i]),
                plot.x + slotWidth * i + slotWidth / 2,
                plot.y + plot.height + 8
            );
        }
    };

    BarChart.prototype.plotArea = function (rect) {
        return {
            x: this.padding.left,
            y: this.padding.top,
            width: rect.width - this.padding.left - this.padding.right,
            height: rect.height - this.padding.top - this.padding.bottom
        };
    };

    BarChart.prototype.maxValue = function (values) {
        var max = 0;
        for (var i = 0; i < values.length; i++) {
            var value = Number(values[i]) || 0;
            if (value > max) {
                max = value;
            }
        }
        return max === 0 ? 1 : max;
    };

    global.HomeFinanceCharts = {
        BarChart: BarChart
    };
})(window);
