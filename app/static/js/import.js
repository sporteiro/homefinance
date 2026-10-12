(function (global) {
    "use strict";

    function ImportForm() {
        this.form = document.getElementById("import-form");
        this.resultPanel = document.getElementById("import-result");
    }

    ImportForm.prototype.init = function () {
        if (!this.form) {
            return;
        }
        this.form.addEventListener("submit", this.handleSubmit.bind(this));
    };

    ImportForm.prototype.handleSubmit = function (event) {
        event.preventDefault();

        var formData = new FormData(this.form);
        var endpoint = "/api/imports/csv";

        fetch(endpoint, {
            method: "POST",
            body: formData
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

    ImportForm.prototype.renderResult = function (data) {
        this.resultPanel.classList.remove("hidden");
        document.getElementById("result-filename").textContent = data.filename;
        document.getElementById("result-total").textContent = data.rows_total;
        document.getElementById("result-imported").textContent = data.rows_imported;
        document.getElementById("result-skipped").textContent = data.rows_skipped;

        var errorsBox = document.getElementById("result-errors");
        var errorsList = document.getElementById("result-errors-list");
        errorsList.innerHTML = "";

        if (data.errors && data.errors.length > 0) {
            errorsBox.classList.remove("hidden");
            data.errors.forEach(function (error) {
                var item = document.createElement("li");
                item.textContent = error;
                errorsList.appendChild(item);
            });
        } else {
            errorsBox.classList.add("hidden");
        }
    };

    ImportForm.prototype.renderError = function (error) {
        this.resultPanel.classList.remove("hidden");
        var errorsBox = document.getElementById("result-errors");
        var errorsList = document.getElementById("result-errors-list");
        errorsBox.classList.remove("hidden");
        errorsList.innerHTML = "";

        var item = document.createElement("li");
        item.textContent = error.message;
        errorsList.appendChild(item);
    };

    global.addEventListener("DOMContentLoaded", function () {
        new ImportForm().init();
    });
})(window);
