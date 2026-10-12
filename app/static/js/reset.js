(function (global) {
    "use strict";

    function ResetForm() {
        this.form = document.getElementById("reset-form");
        this.scopeSelect = document.getElementById("reset-scope");
        this.categoryField = document.getElementById("category-field");
        this.categorySelect = document.getElementById("reset-category");
        this.confirmationInput = document.getElementById("reset-confirmation");
        this.resultPanel = document.getElementById("reset-result");
    }

    ResetForm.prototype.init = function () {
        if (!this.form) {
            return;
        }
        this.form.addEventListener("submit", this.handleSubmit.bind(this));
        this.scopeSelect.addEventListener("change", this.updateCategoryVisibility.bind(this));
        this.updateCategoryVisibility();
    };

    ResetForm.prototype.updateCategoryVisibility = function () {
        var scope = this.scopeSelect.value;
        if (scope === "expenses") {
            this.categoryField.classList.remove("hidden");
        } else {
            this.categoryField.classList.add("hidden");
        }
    };

    ResetForm.prototype.handleSubmit = function (event) {
        event.preventDefault();

        var scope = this.scopeSelect.value;
        var categoryValue = this.categorySelect.value;
        var confirmation = this.confirmationInput.value.trim();

        var payload = {
            scope: scope,
            category_id: scope === "expenses" && categoryValue ? parseInt(categoryValue, 10) : null,
            confirmation: confirmation
        };

        if (!global.confirm("This will permanently delete data. Continue?")) {
            return;
        }

        fetch("/api/admin/reset", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
            .then(function (response) {
                if (!response.ok) {
                    return response.text().then(function (text) {
                        throw new Error("HTTP " + response.status + ": " + text);
                    });
                }
                return response.json();
            })
            .then(this.renderResult.bind(this))
            .catch(this.renderError.bind(this));
    };

    ResetForm.prototype.renderResult = function (data) {
        this.resultPanel.classList.remove("hidden");
        document.getElementById("result-scope").textContent = data.scope;
        document.getElementById("result-category").textContent =
            data.category_id === null ? "all" : data.category_id;
        document.getElementById("result-expenses").textContent = data.deleted_expenses;
        document.getElementById("result-imports").textContent = data.deleted_imports;
        this.confirmationInput.value = "";
    };

    ResetForm.prototype.renderError = function (error) {
        this.resultPanel.classList.remove("hidden");
        document.getElementById("result-scope").textContent = "error";
        document.getElementById("result-category").textContent = "";
        document.getElementById("result-expenses").textContent = "0";
        document.getElementById("result-imports").textContent = "0";
        global.alert(error.message);
    };

    global.addEventListener("DOMContentLoaded", function () {
        new ResetForm().init();
    });
})(window);
