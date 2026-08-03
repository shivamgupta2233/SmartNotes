// ============================
// Smart Notes - Script
// ============================

document.addEventListener("DOMContentLoaded", function () {

    const btn = document.getElementById("darkModeBtn");

    // Load saved theme
    if (localStorage.getItem("theme") === "dark") {

        document.body.classList.add("dark-mode");

        if (btn) {
            btn.innerHTML = "☀️ Light";
        }

    } else {

        if (btn) {
            btn.innerHTML = "🌙 Dark";
        }

    }

    // Toggle Theme
    if (btn) {

        btn.addEventListener("click", function () {

            document.body.classList.toggle("dark-mode");

            if (document.body.classList.contains("dark-mode")) {

                localStorage.setItem("theme", "dark");

                btn.innerHTML = "☀️ Light";

            } else {

                localStorage.setItem("theme", "light");

                btn.innerHTML = "🌙 Dark";

            }

        });

    }

});