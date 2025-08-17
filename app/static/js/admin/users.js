// static/js/admin/users.js
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


// ---------------- Render Users Table ----------------
// ---------------- Render Users Table ----------------
function renderUsersTable(users) {
    const tbody = document.querySelector("#userTable tbody");
    tbody.innerHTML = "";

    users.forEach((user, index) => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td class="text-center fw-semibold">${index + 1}</td>
            <td>${user.username}</td>
            <td>${user.email || ""}</td>
            <td>${user.phone || ""}</td>
            <td class="text-center">${user.is_admin ? "Yes" : "No"}</td>
        `;

        const actionsTd = document.createElement("td");
        actionsTd.className = "text-center";

        // Create a wrapper for compact icons
        const actionsWrapper = document.createElement("div");
        actionsWrapper.style.display = "flex";
        actionsWrapper.style.justifyContent = "center";
        actionsWrapper.style.gap = "6px";  // small spacing
        actionsWrapper.style.fontSize = "16px"; // reduce emoji size

        // --- Edit (✏️) ---
        const editBtn = document.createElement("span");
        editBtn.style.cursor = "pointer";
        editBtn.title = "Edit User";
        editBtn.textContent = "✏️";
        editBtn.addEventListener("click", () => openEditUserModal(user));
        actionsWrapper.appendChild(editBtn);

        // --- Reset Password (🔑) ---
        const resetBtn = document.createElement("span");
        resetBtn.style.cursor = "pointer";
        resetBtn.title = "Reset Password";
        resetBtn.textContent = "🔑";
        resetBtn.addEventListener("click", () => openResetPasswordModal(user));
        actionsWrapper.appendChild(resetBtn);

        // --- Delete (🗑️) ---
        const deleteBtn = document.createElement("span");
        deleteBtn.style.cursor = "pointer";
        deleteBtn.title = "Delete User";
        deleteBtn.textContent = "🗑️";
        deleteBtn.addEventListener("click", () => openDeleteUserModal(user));
        actionsWrapper.appendChild(deleteBtn);

        actionsTd.appendChild(actionsWrapper);
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

document.getElementById("editUserForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("editUserId").value;

    const updatedUser = {
        username: document.getElementById("editUsername").value,
        email: document.getElementById("editEmail").value,
        phone: document.getElementById("editPhone").value,
        is_admin: document.getElementById("editIsAdmin").checked,
    };

    try {
        showLoader();
        await apiClient.put(apiEndpoints.admin.userById(id), updatedUser);
        bootstrap.Modal.getInstance(document.getElementById("editUserModal")).hide();
        await initUsersTab(); // Refresh
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
        await initUsersTab(); // Refresh
    } catch (err) {
        console.error("Error deleting user:", err);
    } finally {
        hideLoader();
    }
});

// ---------------- Reset Password ----------------
function openResetPasswordModal(user) {
    document.getElementById("resetPasswordUserId").value = user.id;
    document.getElementById("resetPasswordUserName").textContent = user.username;

    new bootstrap.Modal(document.getElementById("resetPasswordModal")).show();
}

document.getElementById("confirmResetPasswordBtn").addEventListener("click", async () => {
    const id = document.getElementById("resetPasswordUserId").value;
    const newPassword = document.getElementById("newPasswordInput").value.trim();

    if (!newPassword) {
        alert("Please enter a new password.");
        return;
    }

    try {
        showLoader();
        await apiClient.post(apiEndpoints.admin.resetPassword(id), { new_password: newPassword });
        bootstrap.Modal.getInstance(document.getElementById("resetPasswordModal")).hide();
        alert("Password has been reset successfully.");
    } catch (err) {
        console.error("Error resetting password:", err);
        alert("Failed to reset password. Please try again.");
    } finally {
        hideLoader();
    }
});
