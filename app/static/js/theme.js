(function (global) {
    "use strict";

    var STORAGE_KEY = "homefinance-theme";
    var DEFAULT_THEME = "dark";

    function getStoredTheme() {
        try {
            var value = global.localStorage.getItem(STORAGE_KEY);
            if (value === "light" || value === "dark") {
                return value;
            }
        } catch (e) {
            // Ignore storage errors.
        }
        return null;
    }

    function storeTheme(theme) {
        try {
            global.localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {
            // Ignore storage errors.
        }
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
    }

    function nextTheme(current) {
        return current === "dark" ? "light" : "dark";
    }

    function updateButtonLabel(button, theme) {
        button.textContent = theme === "dark" ? "Light mode" : "Dark mode";
    }

    function currentTheme() {
        return document.documentElement.getAttribute("data-theme") || DEFAULT_THEME;
    }

    function ThemeToggle(button) {
        this.button = button;
    }

    ThemeToggle.prototype.init = function () {
        if (!this.button) {
            return;
        }
        updateButtonLabel(this.button, currentTheme());
        this.button.addEventListener("click", this.handleClick.bind(this));
    };

    ThemeToggle.prototype.handleClick = function () {
        var theme = nextTheme(currentTheme());
        applyTheme(theme);
        storeTheme(theme);
        updateButtonLabel(this.button, theme);
    };

    global.addEventListener("DOMContentLoaded", function () {
        var stored = getStoredTheme();
        if (stored) {
            applyTheme(stored);
        }
        var button = document.getElementById("theme-toggle");
        new ThemeToggle(button).init();
    });
})(window);
