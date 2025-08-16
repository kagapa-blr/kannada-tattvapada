export function initUsersTab() {
    console.log("Loading Users Tab...");
    fetch('/admin/users')
        .then(res => res.json())
        .then(data => renderUsersTable(data))
        .catch(err => console.error("Error fetching user list:", err));
}

// Render table rows
function renderUsersTable(users) {
    const tbody = document.querySelector("#userTable tbody");
    tbody.innerHTML = "";

    users.forEach(user => {
        const tr = document.createElement("tr");
        tr.innerHTML += `<td>${user.username}</td>`;
        tr.innerHTML += `<td>${user.email || ""}</td>`;
        tr.innerHTML += `<td>${user.phone || ""}</td>`;
        tr.innerHTML += `<td>${user.is_admin ? "✅" : "❌"}</td>`;

        const actionsTd = document.createElement("td");

        const editBtn = document.createElement("button");
        editBtn.className = "btn btn-sm btn-primary me-2";
        editBtn.textContent = "Edit";
        editBtn.addEventListener("click", () => openEditUserModal(user));
        actionsTd.appendChild(editBtn);

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "btn btn-sm btn-danger";
        deleteBtn.textContent = "Delete";
        deleteBtn.addEventListener("click", () => openDeleteUserModal(user));
        actionsTd.appendChild(deleteBtn);

        tr.appendChild(actionsTd);
        tbody.appendChild(tr);
    });
}

// Modal: Edit User
function openEditUserModal(user) {
    document.getElementById("editUserId").value = user.id;
    document.getElementById("editUsername").value = user.username;
    document.getElementById("editEmail").value = user.email || "";
    document.getElementById("editPhone").value = user.phone || "";
    document.getElementById("editIsAdmin").checked = user.is_admin;

    new bootstrap.Modal(document.getElementById("editUserModal")).show();
}

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
            initUsersTab();
        })
        .catch(err => console.error("Error updating user:", err));
});

// Modal: Delete User
function openDeleteUserModal(user) {
    document.getElementById("deleteUserId").value = user.id;
    document.getElementById("deleteUserName").textContent = user.username;

    new bootstrap.Modal(document.getElementById("deleteUserModal")).show();
}

document.getElementById("confirmDeleteUserBtn").addEventListener("click", () => {
    const id = document.getElementById("deleteUserId").value;

    fetch(`/admin/users/${id}`, { method: "DELETE" })
        .then(res => res.json())
        .then(() => {
            bootstrap.Modal.getInstance(document.getElementById("deleteUserModal")).hide();
            initUsersTab();
        })
        .catch(err => console.error("Error deleting user:", err));
});
