import { initOverviewTab } from "./tabs/overview.js";
import { initUsersTab } from "./tabs/users.js";
import { initUpdateTab } from "./tabs/update.js";
import { initAddTab } from "./tabs/add.js";
import { initDeleteTab } from "./tabs/delete.js";

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

    // Sidebar navigation tab switching
    links.forEach(link => {
        link.addEventListener("click", () => {
            links.forEach(l => l.classList.remove("active"));
            link.classList.add("active");
            tabs.forEach(tab => tab.classList.remove("active"));

            const target = link.getAttribute("data-tab");
            const targetElement = document.getElementById(target);
            if (targetElement) {
                targetElement.classList.add("active");
            }
            if (tabInitFunctions[target]) {
                tabInitFunctions[target]();
            }
        });
    });

    // Load default active tab on page load
    const defaultActiveTab = document.querySelector(".admin-sidebar a.active");
    if (defaultActiveTab) {
        const target = defaultActiveTab.getAttribute("data-tab");
        if (tabInitFunctions[target]) {
            tabInitFunctions[target]();
        }
    }

    // Sidebar collapse toggle
    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
        main.classList.toggle("collapsed");
    });

    // Logout action
    logoutBtn.addEventListener("click", () => {
        alert("Logging out...");
        // TODO: API call or redirect
    });
});
