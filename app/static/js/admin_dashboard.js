// ---------------------------------------------------------
// Admin Dashboard Main Script
// ---------------------------------------------------------

import { initOverviewTab } from "./admin/overview.js";
import { initUsersTab } from "./admin/users.js";
import { initUpdateTab } from "./admin/update_tatvapada.js";
import { initAddTab } from "./admin/add_tatvapada.js";
import { initDeleteTab } from "./admin/delete_tatvapada.js";
import { showLoader, hideLoader } from "./loader.js";
import { initDocumentsTab } from './admin/documents.js'
import apiClient, { BASE_URL } from "./apiClient.js";
import { initTippaniManageTab } from './admin/manageTippani.js'
import { initParibhashikaPadavivaranaManageTab } from './admin/manageparibhashika.js'
import { initArthakoshaManageTab } from './admin/manageArthakosha.js'
document.addEventListener("DOMContentLoaded", () => {
    // ----------------------------
    // DOM References
    // ----------------------------
    const links = document.querySelectorAll(".admin-sidebar a");
    const tabs = document.querySelectorAll(".admin-tab-content");
    const sidebar = document.getElementById("admin-sidebar");
    const main = document.getElementById("admin-main");
    const toggleBtn = document.getElementById("admin-toggle-btn");
    const logoutBtn = document.getElementById("admin-logout-btn");

    // ----------------------------
    // Tab Initializers
    // ----------------------------
    const tabInitFunctions = {
        "admin-overview": initOverviewTab,
        "admin-users": initUsersTab,
        "admin-update": initUpdateTab,
        "admin-add": initAddTab,
        "admin-delete": initDeleteTab,
        "admin-documents": initDocumentsTab,
        "admin-tippani": initTippaniManageTab,
        "admin-paribhashika": initParibhashikaPadavivaranaManageTab,
        "admin-arthakosha": initArthakoshaManageTab, // <-- instantiate the class
    };

    // ----------------------------
    // Helpers
    // ----------------------------
    function loadTab(target) {
        showLoader();

        // Small timeout ensures loader is visible, even for fast loads
        setTimeout(() => {
            // Switch active tab
            tabs.forEach(tab => tab.classList.remove("active"));
            const targetElement = document.getElementById(target);
            if (targetElement) targetElement.classList.add("active");

            // Run tab-specific init (if exists)
            if (tabInitFunctions[target]) {
                Promise.resolve(tabInitFunctions[target]())
                    .finally(hideLoader);
            } else {
                hideLoader();
            }
        }, 200);
    }

    // ----------------------------
    // Sidebar Navigation
    // ----------------------------
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
        loadTab(defaultActiveTab.getAttribute("data-tab"));
    }

    // ----------------------------
    // Sidebar Toggle
    // ----------------------------
    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
        main.classList.toggle("collapsed");
    });

    // ----------------------------
    // Logout Handling
    // ----------------------------
    logoutBtn.addEventListener("click", () => {
        new bootstrap.Modal(
            document.getElementById("logoutConfirmModal")
        ).show();
    });

    document.getElementById("confirmLogoutBtn").addEventListener("click", async () => {
        try {
            await apiClient.get(`${BASE_URL}/logout`);
            bootstrap.Modal.getInstance(
                document.getElementById("logoutConfirmModal")
            ).hide();
            window.location.replace(`${BASE_URL}`);
        } catch (err) {
            console.error("Logout error:", err);
        }
    });


    // ----------------------------
    // Initialize User Info
    // ----------------------------
    initUserFromServer();
});



// ---------------------------------------------------------
// Fetch Logged-in User Info
// ---------------------------------------------------------
async function initUserFromServer() {
    try {
        // Use apiClient instead of raw fetch
        const res = await apiClient.get(`${BASE_URL}/me`);
        const user = res;

        document.getElementById("logged-username").textContent = user.username;
        document.getElementById("modal-logged-username").textContent = user.username;
    } catch (err) {
        console.warn("initUserFromServer: failed to fetch user info:", err.message);
        window.location.href = "`${BASE_URL}/login`";
    }
}
