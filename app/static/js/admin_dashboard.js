import { initOverviewTab } from "./admin/overview.js";
import { initUsersTab } from "./admin/users.js";
import { initUpdateTab } from "./admin/update_tatvapada.js";
import { initAddTab } from "./admin/add_tatvapada.js";
import { initDeleteTab } from "./admin/delete_tatvapada.js";
import { showLoader, hideLoader } from "./loader.js";

document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".admin-sidebar a");
    const tabs = document.querySelectorAll(".admin-tab-content");
    const sidebar = document.getElementById("admin-sidebar");
    const main = document.getElementById("admin-main");
    const toggleBtn = document.getElementById("admin-toggle-btn");
    const logoutBtn = document.getElementById("admin-logout-btn");

    const tabInitFunctions = {
        "admin-overview": initOverviewTab,
        "admin-users": initUsersTab,
        "admin-update": initUpdateTab,
        "admin-add": initAddTab,
        "admin-delete": initDeleteTab,
    };

    // Helper: load a tab with loader
    function loadTab(target) {
        showLoader();

        // Small timeout to ensure loader is visible even for quick loads
        setTimeout(() => {
            tabs.forEach(tab => tab.classList.remove("active"));
            const targetElement = document.getElementById(target);
            if (targetElement) {
                targetElement.classList.add("active");
            }
            if (tabInitFunctions[target]) {
                // Allow async tab init (like fetching API data)
                Promise.resolve(tabInitFunctions[target]()).finally(() => {
                    hideLoader();
                });
            } else {
                hideLoader();
            }
        }, 200);
    }

    // Sidebar navigation tab switching
    links.forEach(link => {
        link.addEventListener("click", () => {
            links.forEach(l => l.classList.remove("active"));
            link.classList.add("active");
            const target = link.getAttribute("data-tab");
            loadTab(target);
        });
    });

    // Load default active tab on page load
    const defaultActiveTab = document.querySelector(".admin-sidebar a.active");
    if (defaultActiveTab) {
        const target = defaultActiveTab.getAttribute("data-tab");
        loadTab(target);
    }

    // Sidebar collapse toggle
    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
        main.classList.toggle("collapsed");
    });

    // Logout action
    logoutBtn.addEventListener("click", () => {
        fetch("/logout", { method: "GET", credentials: "include" })
            .then(() => window.location.replace("/login"))
            .catch(err => console.error("Logout error:", err));
    });
});
