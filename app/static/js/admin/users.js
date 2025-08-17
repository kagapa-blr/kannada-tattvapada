import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

// ---------------- Initialize Users Tab ----------------
export async function initUsersTab() {
    try {
        showLoader();
        const users = await apiClient.get(apiEndpoints.admin.users);
        renderUsersTable(users);
    } catch (err) {
        console.error("Error fetching user list:", err);
    } finally {
        hideLoader();
    }
}

// ---------------- Render Table Rows ----------------
function renderUsersTable(users) {
    const tbody = document.querySelector("#userTable tbody");
    tbody.innerHTML = "";

    users.forEach((user, index) => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
      <td class="text-center fw-semibold">${index + 1}</td>   <!-- Serial Number -->
      <td>${user.username}</td>
      <td>${user.email || ""}</td>
      <td>${user.phone || ""}</td>
      <td class="text-center">${user.is_admin ? "✅" : "❌"}</td>
    `;

        const actionsTd = document.createElement("td");
        actionsTd.className = "text-center";

        // Edit button
        const editBtn = document.createElement("button");
        editBtn.className = "btn btn-sm btn-primary me-2";
        editBtn.innerHTML = "✏️ Edit";
        editBtn.addEventListener("click", () => openEditUserModal(user));
        actionsTd.appendChild(editBtn);

        // Delete button
        const deleteBtn = document.createElement("button");
        deleteBtn.className = "btn btn-sm btn-danger";
        deleteBtn.innerHTML = "🗑 Delete";
        deleteBtn.addEventListener("click", () => openDeleteUserModal(user));
        actionsTd.appendChild(deleteBtn);

        tr.appendChild(actionsTd);
        tbody.appendChild(tr);
    });
}

// ---------------- Edit User ----------------
function openEditUserModal(user) {
    document.getElementById("editUserId").value = user.id;
    document.getElementById("editUsername").value = user.username;
    document.getElementById("editEmail").value = user.email || "";
    document.getElementById("editPhone").value = user.phone || "";
    document.getElementById("editIsAdmin").checked = user.is_admin;

    new bootstrap.Modal(document.getElementById("editUserModal")).show();
}

document.getElementById("saveUserChangesBtn").addEventListener("click", async () => {
    const id = document.getElementById("editUserId").value;
    const updatedUser = {
        username: document.getElementById("editUsername").value,
        email: document.getElementById("editEmail").value,
        phone: document.getElementById("editPhone").value,
        is_admin: document.getElementById("editIsAdmin").checked
    };

    try {
        showLoader();
        await apiClient.put(apiEndpoints.admin.userById(id), updatedUser);
        bootstrap.Modal.getInstance(document.getElementById("editUserModal")).hide();
        await initUsersTab(); // refresh after save
    } catch (err) {
        console.error("Error updating user:", err);
    } finally {
        hideLoader();
    }
});

// ---------------- Delete User ----------------
function openDeleteUserModal(user) {
    document.getElementById("deleteUserId").value = user.id;
    document.getElementById("deleteUserName").textContent = user.username;

    new bootstrap.Modal(document.getElementById("deleteUserModal")).show();
}

document.getElementById("confirmDeleteUserBtn").addEventListener("click", async () => {
    const id = document.getElementById("deleteUserId").value;

    try {
        showLoader();
        await apiClient.delete(apiEndpoints.admin.userById(id));
        bootstrap.Modal.getInstance(document.getElementById("deleteUserModal")).hide();
        await initUsersTab(); // refresh after delete
    } catch (err) {
        console.error("Error deleting user:", err);
    } finally {
        hideLoader();
    }
});
