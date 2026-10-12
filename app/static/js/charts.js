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
        "#dd6b20",
        "#3182ce",
        "#9b2c2c"
    ];

    var tooltipElement = null;

    function getTooltip() {
        if (tooltipElement) {
            return tooltipElement;
        }
        tooltipElement = document.createElement("div");
        tooltipElement.className = "chart-tooltip";
        tooltipElement.style.display = "none";
        document.body.appendChild(tooltipElement);
        return tooltipElement;
    }

    function showTooltip(html, clientX, clientY) {
        var tip = getTooltip();
        tip.innerHTML = html;
        tip.style.display = "block";

        var offset = 12;
        var tipRect = tip.getBoundingClientRect();
        var x = clientX + offset;
        var y = clientY + offset;

        if (x + tipRect.width > global.innerWidth) {
            x = clientX - tipRect.width - offset;
        }
        if (y + tipRect.height > global.innerHeight) {
            y = clientY - tipRect.height - offset;
        }

        tip.style.left = x + "px";
        tip.style.top = y + "px";
    }

    function hideTooltip() {
        if (tooltipElement) {
            tooltipElement.style.display = "none";
        }
    }

    function themeColors() {
        var styles = global.getComputedStyle(document.documentElement);
        return {
            axis: styles.getPropertyValue("--color-border").trim() || "#dcdfe4",
            text: styles.getPropertyValue("--color-text").trim() || "#1f2328",
            muted: styles.getPropertyValue("--color-muted").trim() || "#656d76"
        };
    }

    function formatEuro(value) {
        var number = Number(value);
        if (isNaN(number)) {
            return "0.00 EUR";
        }
        return number.toFixed(2) + " EUR";
    }

    function colorForIndex(index) {
        return PALETTE[index % PALETTE.length];
    }

    function colorMap(names) {
        var map = {};
        for (var i = 0; i < names.length; i++) {
            map[names[i]] = colorForIndex(i);
        }
        return map;
    }

    function renderLegend(container, names) {
        if (!container) {
            return;
        }
        container.innerHTML = "";
        var map = colorMap(names);
        for (var i = 0; i < names.length; i++) {
            var name = names[i];
            var item = document.createElement("span");
            item.className = "legend-item";

            var swatch = document.createElement("span");
            swatch.className = "legend-swatch";
            swatch.style.backgroundColor = map[name];

            var label = document.createElement("span");
            label.className = "legend-label";
            label.textContent = name;

            item.appendChild(swatch);
            item.appendChild(label);
            container.appendChild(item);
        }
    }

    function setupCanvas(canvas) {
        var ratio = global.devicePixelRatio || 1;
        var rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * ratio;
        canvas.height = rect.height * ratio;
        var ctx = canvas.getContext("2d");
        ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
        ctx.clearRect(0, 0, rect.width, rect.height);
        return { ctx: ctx, width: rect.width, height: rect.height };
    }

    function drawEmpty(ctx, width, height, colors) {
        ctx.fillStyle = colors.muted;
        ctx.font = "14px system-ui, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("No data available", width / 2, height / 2);
    }

    function maxOf(values) {
        var max = 0;
        for (var i = 0; i < values.length; i++) {
            var v = Number(values[i]) || 0;
            if (v > max) max = v;
        }
        return max === 0 ? 1 : max;
    }

    function drawAxes(ctx, colors, plotX, plotY, plotW, plotH, maxValue) {
        ctx.strokeStyle = colors.axis;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(plotX, plotY);
        ctx.lineTo(plotX, plotY + plotH);
        ctx.lineTo(plotX + plotW, plotY + plotH);
        ctx.stroke();

        ctx.fillStyle = colors.muted;
        ctx.font = "11px system-ui, sans-serif";
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";
        var steps = 4;
        for (var s = 0; s <= steps; s++) {
            var value = (maxValue / steps) * s;
            var y = plotY + plotH - (plotH / steps) * s;
            ctx.fillText(formatEuro(value), plotX - 8, y);
        }
    }

    function drawXLabel(ctx, colors, label, x, y) {
        ctx.fillStyle = colors.text;
        ctx.font = "11px system-ui, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillText(String(label), x, y);
    }

    function attachHitDetection(canvas, hitAreas) {
        canvas.onmousemove = function (event) {
            var rect = canvas.getBoundingClientRect();
            var x = event.clientX - rect.left;
            var y = event.clientY - rect.top;

            for (var i = hitAreas.length - 1; i >= 0; i--) {
                var area = hitAreas[i];
                if (
                    x >= area.x &&
                    x <= area.x + area.w &&
                    y >= area.y &&
                    y <= area.y + area.h
                ) {
                    var html =
                        '<div class="chart-tooltip-title">' +
                        area.title +
                        "</div>" +
                        '<div class="chart-tooltip-value">' +
                        formatEuro(area.value) +
                        "</div>";
                    showTooltip(html, event.clientX, event.clientY);
                    canvas.style.cursor = "pointer";
                    return;
                }
            }

            hideTooltip();
            canvas.style.cursor = "default";
        };

        canvas.onmouseleave = function () {
            hideTooltip();
            canvas.style.cursor = "default";
        };
    }

    function SimpleBarChart(canvas) {
        this.canvas = canvas;
        this.padding = { top: 16, right: 16, bottom: 56, left: 72 };
        this.barGap = 8;
        this.hitAreas = [];
    }

    SimpleBarChart.prototype.render = function (labels, values, options) {
        options = options || {};
        var setup = setupCanvas(this.canvas);
        var colors = themeColors();
        this.hitAreas = [];

        if (!labels || labels.length === 0) {
            drawEmpty(setup.ctx, setup.width, setup.height, colors);
            attachHitDetection(this.canvas, this.hitAreas);
            return;
        }

        var padding = this.padding;
        var plotX = padding.left;
        var plotY = padding.top;
        var plotW = setup.width - padding.left - padding.right;
        var plotH = setup.height - padding.top - padding.bottom;
        var maxValue = maxOf(values);
        var customColors = options.colors || null;

        drawAxes(setup.ctx, colors, plotX, plotY, plotW, plotH, maxValue);

        var slot = plotW / labels.length;
        var barWidth = Math.max(slot - this.barGap, 4);

        for (var i = 0; i < labels.length; i++) {
            var v = Number(values[i]) || 0;
            var barH = maxValue > 0 ? (v / maxValue) * plotH : 0;
            var x = plotX + slot * i + (slot - barWidth) / 2;
            var yBar = plotY + plotH - barH;

            setup.ctx.fillStyle = customColors
                ? customColors[i % customColors.length]
                : colorForIndex(i);
            setup.ctx.fillRect(x, yBar, barWidth, barH);

            drawXLabel(
                setup.ctx,
                colors,
                labels[i],
                plotX + slot * i + slot / 2,
                plotY + plotH + 8
            );

            this.hitAreas.push({
                x: x,
                y: yBar,
                w: barWidth,
                h: Math.max(barH, 4),
                title: String(labels[i]),
                value: v
            });
        }

        attachHitDetection(this.canvas, this.hitAreas);
    };

    function StackedBarChart(canvas, categoryNames) {
        this.canvas = canvas;
        this.categoryNames = categoryNames || [];
        this.colors = colorMap(this.categoryNames);
        this.padding = { top: 16, right: 16, bottom: 56, left: 72 };
        this.barGap = 8;
        this.hitAreas = [];
    }

    StackedBarChart.prototype.render = function (labels, perCategory) {
        var setup = setupCanvas(this.canvas);
        var colors = themeColors();
        this.hitAreas = [];

        if (!labels || labels.length === 0) {
            drawEmpty(setup.ctx, setup.width, setup.height, colors);
            attachHitDetection(this.canvas, this.hitAreas);
            return;
        }

        var padding = this.padding;
        var plotX = padding.left;
        var plotY = padding.top;
        var plotW = setup.width - padding.left - padding.right;
        var plotH = setup.height - padding.top - padding.bottom;

        var totals = [];
        for (var i = 0; i < labels.length; i++) {
            var sum = 0;
            for (var c = 0; c < this.categoryNames.length; c++) {
                var series = perCategory[this.categoryNames[c]] || [];
                sum += Number(series[i]) || 0;
            }
            totals.push(sum);
        }
        var maxValue = maxOf(totals);

        drawAxes(setup.ctx, colors, plotX, plotY, plotW, plotH, maxValue);

        var slot = plotW / labels.length;
        var barWidth = Math.max(slot - this.barGap, 4);

        for (var j = 0; j < labels.length; j++) {
            var baseY = plotY + plotH;
            var x = plotX + slot * j + (slot - barWidth) / 2;

            for (var c2 = 0; c2 < this.categoryNames.length; c2++) {
                var name = this.categoryNames[c2];
                var seriesValues = perCategory[name] || [];
                var v = Number(seriesValues[j]) || 0;
                if (v <= 0) continue;
                var h = maxValue > 0 ? (v / maxValue) * plotH : 0;
                baseY -= h;
                setup.ctx.fillStyle = this.colors[name];
                setup.ctx.fillRect(x, baseY, barWidth, h);

                this.hitAreas.push({
                    x: x,
                    y: baseY,
                    w: barWidth,
                    h: Math.max(h, 4),
                    title: String(labels[j]) + " - " + name,
                    value: v
                });
            }

            drawXLabel(
                setup.ctx,
                colors,
                labels[j],
                plotX + slot * j + slot / 2,
                plotY + plotH + 8
            );
        }

        attachHitDetection(this.canvas, this.hitAreas);
    };

    function GroupedBarChart(canvas, categoryNames) {
        this.canvas = canvas;
        this.categoryNames = categoryNames || [];
        this.colors = colorMap(this.categoryNames);
        this.padding = { top: 16, right: 16, bottom: 56, left: 72 };
        this.groupGap = 12;
        this.barGap = 2;
        this.hitAreas = [];
    }

    GroupedBarChart.prototype.render = function (labels, perCategory) {
        var setup = setupCanvas(this.canvas);
        var colors = themeColors();
        this.hitAreas = [];

        if (!labels || labels.length === 0) {
            drawEmpty(setup.ctx, setup.width, setup.height, colors);
            attachHitDetection(this.canvas, this.hitAreas);
            return;
        }

        var padding = this.padding;
        var plotX = padding.left;
        var plotY = padding.top;
        var plotW = setup.width - padding.left - padding.right;
        var plotH = setup.height - padding.top - padding.bottom;

        var maxValue = 0;
        for (var c = 0; c < this.categoryNames.length; c++) {
            var series = perCategory[this.categoryNames[c]] || [];
            for (var i = 0; i < series.length; i++) {
                var v = Number(series[i]) || 0;
                if (v > maxValue) maxValue = v;
            }
        }
        maxValue = maxValue === 0 ? 1 : maxValue;

        drawAxes(setup.ctx, colors, plotX, plotY, plotW, plotH, maxValue);

        var groupCount = labels.length;
        var seriesCount = Math.max(this.categoryNames.length, 1);
        var groupWidth = plotW / groupCount;
        var usableWidth = groupWidth - this.groupGap;
        var barWidth = Math.max(usableWidth / seriesCount - this.barGap, 2);

        for (var g = 0; g < groupCount; g++) {
            var groupX = plotX + groupWidth * g + this.groupGap / 2;

            for (var c2 = 0; c2 < this.categoryNames.length; c2++) {
                var name = this.categoryNames[c2];
                var seriesValues = perCategory[name] || [];
                var val = Number(seriesValues[g]) || 0;
                var barH = (val / maxValue) * plotH;
                var x = groupX + c2 * (barWidth + this.barGap);
                var yBar = plotY + plotH - barH;

                setup.ctx.fillStyle = this.colors[name];
                setup.ctx.fillRect(x, yBar, barWidth, barH);

                if (val > 0) {
                    this.hitAreas.push({
                        x: x,
                        y: yBar,
                        w: barWidth,
                        h: Math.max(barH, 4),
                        title: String(labels[g]) + " - " + name,
                        value: val
                    });
                }
            }

            drawXLabel(
                setup.ctx,
                colors,
                labels[g],
                plotX + groupWidth * g + groupWidth / 2,
                plotY + plotH + 8
            );
        }

        attachHitDetection(this.canvas, this.hitAreas);
    };

    global.HomeFinanceCharts = {
        SimpleBarChart: SimpleBarChart,
        StackedBarChart: StackedBarChart,
        GroupedBarChart: GroupedBarChart,
        colorMap: colorMap,
        renderLegend: renderLegend
    };
})(window);
