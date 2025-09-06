import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

// ---------------- Current Logged-in User ----------------
let currentUser = null;

async function fetchCurrentUser() {
    try {
        const res = await apiClient.get(apiEndpoints.auth.me);
        currentUser = res; // store logged-in user info
    } catch (err) {
        console.error("Failed to fetch current user:", err);
        currentUser = { user_type: "user" }; // fallback
    }
}

// ---------------- Initialize Users Tab ----------------
export async function initUsersTab() {
    try {
        showLoader();
        await fetchCurrentUser(); // fetch current user first
        const users = await apiClient.get(apiEndpoints.admin.users);
        renderUsersTable(users);
    } catch (err) {
        showAlert("usersAlert", "danger", "Failed to load users. " + err);
    } finally {
        hideLoader();
    }
}

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

        const actionsWrapper = document.createElement("div");
        actionsWrapper.style.display = "flex";
        actionsWrapper.style.justifyContent = "center";
        actionsWrapper.style.gap = "6px";
        actionsWrapper.style.fontSize = "16px";

        // --- Edit ---
        const editBtn = document.createElement("span");
        editBtn.style.cursor = "pointer";
        editBtn.title = "Edit User";
        editBtn.textContent = "✏️";
        if (currentUser.user_type !== "admin") {
            editBtn.style.opacity = "0.5";
            editBtn.style.pointerEvents = "none";
        }
        editBtn.addEventListener("click", () => openEditUserModal(user));
        actionsWrapper.appendChild(editBtn);

        // --- Reset Password ---
        const resetBtn = document.createElement("span");
        resetBtn.style.cursor = "pointer";
        resetBtn.title = "Reset Password";
        resetBtn.textContent = "🔑";
        if (currentUser.user_type !== "admin") {
            resetBtn.style.opacity = "0.5";
            resetBtn.style.pointerEvents = "none";
        }
        resetBtn.addEventListener("click", () => openResetPasswordModal(user));
        actionsWrapper.appendChild(resetBtn);

        // --- Delete ---
        const deleteBtn = document.createElement("span");
        deleteBtn.style.cursor = "pointer";
        deleteBtn.title = "Delete User";
        deleteBtn.textContent = "🗑️";
        if (currentUser.user_type !== "admin") {
            deleteBtn.style.opacity = "0.5";
            deleteBtn.style.pointerEvents = "none";
        }
        deleteBtn.addEventListener("click", () => openDeleteUserModal(user));
        actionsWrapper.appendChild(deleteBtn);

        actionsTd.appendChild(actionsWrapper);
        tr.appendChild(actionsTd);
        tbody.appendChild(tr);
    });
}

// ---------------- Show Alert ----------------
function showAlert(elementId, type, message) {
    const alertEl = document.getElementById(elementId);
    alertEl.className = `alert alert-${type}`;
    alertEl.textContent = message;
    alertEl.classList.remove("d-none");
}

// ---------------- Edit User ----------------
function openEditUserModal(user) {
    document.getElementById("editUserId").value = user.id;
    document.getElementById("editUsername").value = user.username;
    document.getElementById("editEmail").value = user.email || "";
    document.getElementById("editPhone").value = user.phone || "";
    document.getElementById("editIsAdmin").checked = user.is_admin;
    document.getElementById("editUserAlert").classList.add("d-none");

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
    const alertElId = "editUserAlert";

    try {
        showLoader();
        const res = await apiClient.put(apiEndpoints.admin.userById(id), updatedUser);
        bootstrap.Modal.getInstance(document.getElementById("editUserModal")).hide();
        await initUsersTab();
        showAlert("usersAlert", "success", res.message || "User updated successfully.");
    } catch (err) {
        showAlert(alertElId, "danger", err?.response?.data?.error || "Failed to update user. " + err);
    } finally {
        hideLoader();
    }
});

// ---------------- Delete User ----------------
function openDeleteUserModal(user) {
    document.getElementById("deleteUserId").value = user.id;
    document.getElementById("deleteUserName").textContent = user.username;
    document.getElementById("deleteUserAlert").classList.add("d-none");

    new bootstrap.Modal(document.getElementById("deleteUserModal")).show();
}

document.getElementById("confirmDeleteUserBtn").addEventListener("click", async () => {
    const id = document.getElementById("deleteUserId").value;
    const alertElId = "deleteUserAlert";

    try {
        showLoader();
        const res = await apiClient.delete(apiEndpoints.admin.userById(id));
        bootstrap.Modal.getInstance(document.getElementById("deleteUserModal")).hide();
        await initUsersTab();
        showAlert("usersAlert", "success", res.message || "User deleted successfully.");
    } catch (err) {
        showAlert(alertElId, "danger", err?.response?.data?.error || "Failed to delete user. " + err);
    } finally {
        hideLoader();
    }
});

// ---------------- Reset Password ----------------
function openResetPasswordModal(user) {
    document.getElementById("resetPasswordUserId").value = user.id;
    document.getElementById("resetPasswordUserName").textContent = user.username;
    document.getElementById("newPasswordInput").value = "";
    document.getElementById("resetPasswordAlert").classList.add("d-none");

    new bootstrap.Modal(document.getElementById("resetPasswordModal")).show();
}

document.getElementById("confirmResetPasswordBtn").addEventListener("click", async () => {
    const id = document.getElementById("resetPasswordUserId").value;
    const newPassword = document.getElementById("newPasswordInput").value.trim();
    const alertElId = "resetPasswordAlert";

    if (!newPassword) {
        showAlert(alertElId, "warning", "Please enter a new password.");
        return;
    }

    try {
        showLoader();
        const res = await apiClient.post(apiEndpoints.admin.resetPassword(id), { new_password: newPassword });
        bootstrap.Modal.getInstance(document.getElementById("resetPasswordModal")).hide();
        showAlert("usersAlert", "success", res.message || "Password reset successfully.");
    } catch (err) {
        showAlert(alertElId, "danger", err?.response?.data?.error || "Failed to reset password. " + err);
    } finally {
        hideLoader();
    }
});
