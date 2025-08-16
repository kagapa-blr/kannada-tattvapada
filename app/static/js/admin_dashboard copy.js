// /js/admin_dashboard.js
import { initAddTatvapadaUI } from "./addTatvapada.js";

document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".admin-sidebar a");
    const tabs = document.querySelectorAll(".admin-tab-content");
    const sidebar = document.getElementById("admin-sidebar");
    const main = document.getElementById("admin-main");
    const toggleBtn = document.getElementById("admin-toggle-btn");
    const logoutBtn = document.getElementById("admin-logout-btn");

    // Placeholder init functions for each tab
    function initOverviewTab() {
        fetch('/admin/overview')
            .then(res => res.json())
            .then(data => {
                // Update stat cards
                document.getElementById("totalSamputa").textContent = data.total_samputa;
                document.getElementById("totalTatvapada").textContent = data.total_tatvapada;
                document.getElementById("totalAuthors").textContent = data.total_authors;
                document.getElementById("totalAdmins").textContent = data.total_admins;

                // Update table rows
                const tbody = document.getElementById("samputaTableBody");
                tbody.innerHTML = ""; // clear existing rows

                data.tatvapada_per_samputa.forEach(item => {
                    const tr = document.createElement("tr");

                    const tdSamputa = document.createElement("td");
                    tdSamputa.textContent = item.samputa_sankhye;
                    tdSamputa.style.padding = "10px";

                    const tdCount = document.createElement("td");
                    tdCount.textContent = item.count;
                    tdCount.style.padding = "10px";

                    tr.appendChild(tdSamputa);
                    tr.appendChild(tdCount);

                    tbody.appendChild(tr);
                });
            })
            .catch(err => {
                console.error("Error fetching overview data:", err);
            });
    }



    // Master initializer for the Users tab
    function initUsersTab() {
        console.log("Loading Users Tab...");

        fetch('/admin/users')
            .then(res => res.json())
            .then(data => {
                renderUsersTable(data);
            })
            .catch(err => {
                console.error("Error fetching user list:", err);
            });
    }




    function initUpdateTab() {
        console.log("Init Update Tatvapada Tab");

    }

    function initAddTab() {
        console.log("Init Add Tatvapada Tab");

        // Only initialize if the add form exists
        initAddTatvapadaUI();
    }


    function initDeleteTab() {
        console.log("Init Delete Tatvapada Tab");
        // TODO: Add delete tatvapada tab JS here
    }

    // Mapping data-tab attribute values to init functions
    const tabInitFunctions = {
        "admin-overview": initOverviewTab,
        "admin-users": initUsersTab,
        "admin-update": initUpdateTab,
        "admin-add": initAddTab,
        "admin-delete": initDeleteTab,
    };

    // Tab switching
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

            // Call the appropriate init function if exists
            if (tabInitFunctions[target]) {
                tabInitFunctions[target]();
            }
        });
    });

    // Initialize the default active tab on page load
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

    // Logout
    logoutBtn.addEventListener("click", () => {
        alert("Logging out...");
        // Here you can call your logout API or redirect
    });
});





// Render table rows
function renderUsersTable(users) {
    const tbody = document.querySelector("#userTable tbody");
    tbody.innerHTML = "";

    users.forEach(user => {
        const tr = document.createElement("tr");

        // Username
        tr.innerHTML += `<td>${user.username}</td>`;

        // Email
        tr.innerHTML += `<td>${user.email || ""}</td>`;

        // Phone
        tr.innerHTML += `<td>${user.phone || ""}</td>`;

        // Admin
        tr.innerHTML += `<td>${user.is_admin ? "✅" : "❌"}</td>`;

        // Actions
        const actionsTd = document.createElement("td");

        // Edit Button
        const editBtn = document.createElement("button");
        editBtn.className = "btn btn-sm btn-primary me-2";
        editBtn.textContent = "Edit";
        editBtn.addEventListener("click", () => openEditUserModal(user));
        actionsTd.appendChild(editBtn);

        // Delete Button
        const deleteBtn = document.createElement("button");
        deleteBtn.className = "btn btn-sm btn-danger";
        deleteBtn.textContent = "Delete";
        deleteBtn.addEventListener("click", () => openDeleteUserModal(user));
        actionsTd.appendChild(deleteBtn);

        tr.appendChild(actionsTd);

        tbody.appendChild(tr);
    });
}

// Open Edit User Modal
function openEditUserModal(user) {
    document.getElementById("editUserId").value = user.id;
    document.getElementById("editUsername").value = user.username;
    document.getElementById("editEmail").value = user.email || "";
    document.getElementById("editPhone").value = user.phone || "";
    document.getElementById("editIsAdmin").checked = user.is_admin;

    new bootstrap.Modal(document.getElementById("editUserModal")).show();
}

// Save changes from Edit User Modal
document.getElementById("saveUserChangesBtn").addEventListener("click", () => {
    const id = document.getElementById("editUserId").value;
    const updatedUser = {
        username: document.getElementById("editUsername").value,
        email: document.getElementById("editEmail").value,
        phone: document.getElementById("editPhone").value,
        is_admin: document.getElementById("editIsAdmin").checked
    };

    fetch(`/admin/users/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedUser)
    })
        .then(res => res.json())
        .then(() => {
            bootstrap.Modal.getInstance(document.getElementById("editUserModal")).hide();
            initUsersTab(); // Refresh table
        })
        .catch(err => console.error("Error updating user:", err));
});

// Open Delete Confirmation Modal
function openDeleteUserModal(user) {
    document.getElementById("deleteUserId").value = user.id;
    document.getElementById("deleteUserName").textContent = user.username;

    new bootstrap.Modal(document.getElementById("deleteUserModal")).show();
}

// Confirm Delete
document.getElementById("confirmDeleteUserBtn").addEventListener("click", () => {
    const id = document.getElementById("deleteUserId").value;

    fetch(`/admin/users/${id}`, { method: "DELETE" })
        .then(res => res.json())
        .then(() => {
            bootstrap.Modal.getInstance(document.getElementById("deleteUserModal")).hide();
            initUsersTab(); // Refresh table
        })
        .catch(err => console.error("Error deleting user:", err));
});




