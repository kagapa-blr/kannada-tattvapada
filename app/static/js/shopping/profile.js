// ==============================
// Imports & Global Constants
// ==============================
import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

async function fetchUserEmail() {
  try {
    const response = await apiClient.get(apiEndpoints.auth.me);

    if (response && response.user_email) {
      return response.user_email;
    } else {
      console.warn("No email returned from API");
      return null;
    }
  } catch (error) {
    console.error("Failed to fetch user email:", error);
    return null;
  }
}
let email = ""

// ==============================
// DOM ELEMENTS
// ==============================
const DOM = {
  avatar: document.getElementById("userAvatar"),
  nameDisplay: document.getElementById("userNameDisplay"),
  emailDisplay: document.getElementById("userEmailDisplay"),
  profileView: {
    name: document.getElementById("profileViewName"),
    phone: document.getElementById("profileViewPhone"),
    email: document.getElementById("profileViewEmail"),
    gender: document.getElementById("profileViewGender"),
    dob: document.getElementById("profileViewDOB"),
    language: document.getElementById("profileViewLanguage"),
    lastLogin: document.getElementById("profileViewLastLogin"),
  },
  profileForm: document.getElementById("profileForm"),
  profileInputs: {
    name: document.getElementById("profileName"),
    phone: document.getElementById("profilePhone"),
    email: document.getElementById("profileEmail"),
    gender: document.getElementById("profileGender"),
    dob: document.getElementById("profileDOB"),
    language: document.getElementById("profileLanguage"),
  },
  orderTable: $("#orderTable"),
  addressList: document.getElementById("addressList"),
  addressForm: document.getElementById("addressForm"),
  addressInputs: {
    id: document.getElementById("addressId"),
    recipient: document.getElementById("recipientName"),
    phone: document.getElementById("phoneNumber"),
    addressLine: document.getElementById("addressText"),
    city: document.getElementById("addressCity"),
    pincode: document.getElementById("addressPincode"),
    taluk: document.getElementById("addressTaluk"),
    state: document.getElementById("addressState"),
    country: document.getElementById("addressCountry"),
    type: document.getElementById("addressType"),
    instructions: document.getElementById("deliveryInstructions"),
    latitude: document.getElementById("latitude"),
    longitude: document.getElementById("longitude"),
    isDefault: document.getElementById("isDefault"),
  },
  logoutBtn: document.getElementById("logoutBtn"),
};

// ==============================
// GLOBAL STATE
// ==============================
let userData = null;
let addresses = [];
let orders = [];

// ==============================
// UTILITIES
// ==============================
const Utils = {
  getInitials: (name) => {
    if (!name) return "";
    const parts = name.trim().split(/\s+/);
    return parts.length === 1
      ? parts[0].slice(0, 2).toUpperCase()
      : (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  },
  randomGradient: () => {
    const colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA500", "#6A5ACD", "#6a11cb", "#2575fc", "#20c997"];
    let a = colors[Math.floor(Math.random() * colors.length)];
    let b;
    do {
      b = colors[Math.floor(Math.random() * colors.length)];
    } while (b === a);
    return `linear-gradient(135deg, ${a}, ${b})`;
  },
  escapeHtml: (str) =>
    String(str)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;"),
  fetchPostalDetailsByPIN: async (pincode) => {
    try {
      const res = await fetch(`https://api.postalpincode.in/pincode/${pincode}`);
      const data = await res.json();
      if (data[0]?.Status === "Success" && data[0]?.PostOffice?.length) {
        const po = data[0].PostOffice[0];
        return {
          city: po.District || "",
          taluk: po.Division || "",
          state: po.State || "",
          country: po.Country || "",
        };
      }
    } catch (e) {
      console.error("PIN fetch error:", e);
    }
    return null;
  }
};

// ==============================
// RENDER FUNCTIONS
// ==============================
const Render = {


  user: () => {
    if (!userData) return;

    // Avatar and header
    DOM.avatar.textContent = Utils.getInitials(userData.name);
    DOM.avatar.style.background = Utils.randomGradient();
    DOM.nameDisplay.textContent = userData.name || "-";
    DOM.emailDisplay.textContent = userData.email || "-";

    // Profile view (<dd>)
    const view = DOM.profileView;
    view.name.textContent = userData.name || "-";
    view.phone.textContent = userData.phone || "-";
    view.email.textContent = userData.email || "-";
    view.gender.textContent = userData.gender || "-";
    view.dob.textContent = userData.date_of_birth || "-";
    view.language.textContent = userData.preferred_language || "-";
    view.lastLogin.textContent = userData.last_login_at || "-";

    // Profile inputs (for editing)
    const inputs = DOM.profileInputs;
    inputs.name.value = userData.name || "";
    inputs.phone.value = userData.phone || "";
    inputs.email.value = userData.email || "";
    inputs.gender.value = userData.gender || "";
    inputs.language.value = userData.preferred_language || "";

    // Set date input (yyyy-MM-dd) safely for <input type="date">
    if (userData.date_of_birth) {
      const date = new Date(userData.date_of_birth);
      // Ensure valid date
      if (!isNaN(date)) {
        inputs.dob.value = date.toISOString().slice(0, 10);
      }
    } else {
      inputs.dob.value = "";
    }
  },


  orders: () => {
    const table = DOM.orderTable;

    if ($.fn.DataTable.isDataTable(table)) {
      table.DataTable().clear().destroy();
    }

    if (!orders.length) {
      table.find("tbody").html(`<tr><td colspan="5" class="text-center text-muted">No orders found.</td></tr>`);
      return;
    }

    const tbody = table.find("tbody");
    tbody.html("");

    orders.forEach((order, idx) => {
      const statusClass = order.status.toUpperCase() === "DELIVERED"
        ? "success"
        : order.status.toUpperCase() === "SHIPPED"
          ? "info"
          : "warning";

      tbody.append(`
        <tr data-index="${idx}" style="cursor:pointer;">
          <td>${idx + 1}</td>
          <td>${Utils.escapeHtml(order.order_number)}</td>
          <td>${order.created_at?.slice(0, 10) || ""}</td>
          <td><span class="badge bg-${statusClass}">${Utils.escapeHtml(order.status.toUpperCase())}</span></td>
          <td class="text-end">${order.total_amount !== undefined ? order.total_amount : ""}</td>
        </tr>
      `);
    });

    table.DataTable({
      paging: true,
      searching: true,
      ordering: true,
      order: [[2, "desc"]],
      columnDefs: [{ orderable: false, targets: 3 }]
    });

    tbody.find("tr").on("click", function () {
      const idx = parseInt($(this).data("index"), 10);
      showOrderModal(orders[idx]);
    });
  },

  addresses: () => {
    const container = DOM.addressList;
    container.innerHTML = "";
    if (!addresses.length) {
      container.innerHTML = `<p class="text-muted mb-0">No addresses saved yet.</p>`;
      return;
    }
    addresses.forEach((addr, idx) => {
      const card = document.createElement("div");
      card.className = "card mb-2 shadow-sm";
      card.innerHTML = `
        <div class="card-body d-flex justify-content-between align-items-center">
          <div>
            <strong>${Utils.escapeHtml(addr.recipient_name || "")}</strong> 
            <span class="badge bg-primary ms-1">${Utils.escapeHtml(addr.address_type || "")}</span>
            ${addr.is_default ? '<span class="badge bg-success ms-1">Default</span>' : ''}
            <p class="mb-1">${Utils.escapeHtml(addr.address_line)}</p>
            <small class="text-muted">${Utils.escapeHtml(addr.city)}, ${Utils.escapeHtml(addr.postal_code)}</small>
            <p class="text-muted small mb-0">${Utils.escapeHtml(addr.delivery_instructions || "")}</p>
          </div>
          <div>
            <button class="btn btn-sm btn-outline-primary me-2 edit-btn" data-index="${idx}" title="Edit">
              <i class="bi bi-pencil-fill"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger delete-btn" data-index="${idx}" title="Delete">
              <i class="bi bi-trash-fill"></i>
            </button>
          </div>
        </div>
      `;
      container.appendChild(card);
    });
  }
};

// ==============================
// SHOW ORDER MODAL
// ==============================
const showOrderModal = (order) => {
  const addr = order.address_info;
  document.getElementById("modalShippingInfo").innerHTML = `
    <strong>${Utils.escapeHtml(addr.recipient_name)}</strong> (${Utils.escapeHtml(addr.phone_number)})<br>
    ${Utils.escapeHtml(addr.address_line)}, ${Utils.escapeHtml(addr.city)}, ${Utils.escapeHtml(addr.state)}, ${Utils.escapeHtml(addr.postal_code)}, ${Utils.escapeHtml(addr.country)}<br>
    <small>${Utils.escapeHtml(addr.address_type)} | ${Utils.escapeHtml(addr.delivery_instructions || "")}</small>
  `;

  const tbody = document.querySelector("#modalItemsTable tbody");
  tbody.innerHTML = "";
  order.items.forEach((item, i) => {
    const total = item.price * item.quantity;
    tbody.innerHTML += `
      <tr>
        <td>${i + 1}</td>
        <td>${Utils.escapeHtml(item.title)}</td>
        <td>${Utils.escapeHtml(item.author_name)}</td>
        <td>${item.quantity}</td>
        <td>${item.price}</td>
        <td>${total}</td>
      </tr>
    `;
  });

  document.getElementById("modalOrderSummary").innerHTML = `
    <strong>Total Amount:</strong> ₹${order.total_amount}<br>
    <strong>Total Amount:</strong> ₹${order.total_amount}<br>
    <strong>Order ID:</strong> ${Utils.escapeHtml(order.order_number.toUpperCase())}<br>
    <strong>Status:</strong> ${Utils.escapeHtml(order.status.toUpperCase())}<br>
    <strong>Payment Method:</strong> ${order.payment_method ? Utils.escapeHtml(order.payment_method) : "N/A"}<br>
    <strong>Order Notes:</strong> ${order.notes ? Utils.escapeHtml(order.notes) : "-"}
  `;

  new bootstrap.Modal(document.getElementById("orderModal")).show();
};

// ==============================
// API FUNCTIONS
// ==============================
const API = {
  loadUserData: async () => {
    try {
      showLoader();
      email = await fetchUserEmail();
      const userRes = await apiClient.get(apiEndpoints.shopping.getUserByEmail(email));
      if (!userRes.success) throw new Error(userRes.message || "Failed to fetch user");
      userData = userRes.data;

      const addrRes = await apiClient.get(apiEndpoints.shopping.listAddressesByEmail(email));
      if (!addrRes.success) throw new Error(addrRes.message || "Failed to fetch addresses");
      addresses = addrRes.data;

      const orderRes = await apiClient.get(apiEndpoints.shopping.listOrdersByEmail(email));
      if (!orderRes.success) throw new Error(orderRes.message || "Failed to fetch orders");
      orders = orderRes.data;

      Render.user();
      Render.addresses();
      Render.orders();
    } catch (err) {
      //alert("Failed to load user profile: " + err.message);
      console.error(err);
    } finally {
      hideLoader();
    }
  },

  saveAddress: async (address, idx = null) => {
    try {
      showLoader();
      let res;
      if (idx !== null && addresses[idx]) {
        const addrId = addresses[idx].id;
        res = await apiClient.put(apiEndpoints.shopping.updateAddress(addrId), address);
        if (!res.success) throw new Error(res.message || "Failed to update address");
        addresses[idx] = res.data;
      } else {
        res = await apiClient.post(apiEndpoints.shopping.createAddress(email), address);
        if (!res.success) throw new Error(res.message || "Failed to create address");
        addresses.push(res.data);
      }
      if (res.data.is_default) {
        addresses = addresses.map((a) => a.id === res.data.id ? a : { ...a, is_default: false });
      }
      Render.addresses();
    } catch (err) {
      alert("Failed to save address: " + err.message);
      console.error(err);
    } finally {
      hideLoader();
    }
  },

  deleteAddress: async (id) => {
    try {
      showLoader();
      const res = await apiClient.delete(apiEndpoints.shopping.deleteAddress(id));
      if (!res.success) throw new Error(res.message || "Failed to delete address");
      addresses = addresses.filter(a => a.id !== id);
      Render.addresses();
    } catch (err) {
      alert("Failed to delete address: " + err.message);
      console.error(err);
    } finally {
      hideLoader();
    }
  },

  updateProfile: async (payload) => {
    try {
      showLoader();
      const res = await apiClient.put(apiEndpoints.shopping.updateUserByEmail(userData.email), payload);
      if (!res.success) throw new Error(res.message || "Profile update failed");
      Object.assign(userData, payload);
      Render.user();
      bootstrap.Modal.getInstance(document.getElementById("profileModal")).hide();
    } catch (err) {
      alert("Failed to update profile: " + err.message);
      console.error(err);
    } finally {
      hideLoader();
    }
  },


};

async function callProtectedApi() {
  console.log('Validating user session...');
  try {
    const response = await apiClient.get(apiEndpoints.auth.me);
    console.log('API response:', response);
    // handle success if needed
  } catch (err) {
    console.log('API error status:', err.status);

    if (err.status === 401) {
      const modalEl = document.getElementById('sessionExpiredModal');
      if (modalEl) {
        // Set login URL dynamically
        const loginBtn = modalEl.querySelector('#sessionLoginBtn');
        if (loginBtn) {
          loginBtn.setAttribute('href', apiEndpoints.auth.login);
        }

        const sessionModal = new bootstrap.Modal(modalEl, { backdrop: 'static', keyboard: false });
        sessionModal.show();
      } else {
        console.error("Session Expired modal element not found!");
      }
    } else {
      console.error("API error:", err);
    }
  }
}



// ==============================
// EVENT HANDLERS
// ==============================
const Handlers = {
  onPINBlur: async () => {
    const pincode = DOM.addressInputs.pincode.value.trim();
    if (/^\d{6}$/.test(pincode)) {
      const details = await Utils.fetchPostalDetailsByPIN(pincode);
      if (details) {
        DOM.addressInputs.city.value = details.city;
        DOM.addressInputs.taluk.value = details.taluk;
        DOM.addressInputs.state.value = details.state;
        DOM.addressInputs.country.value = details.country;
      }
    }
  },

  onProfileSubmit: async (e) => {
    e.preventDefault();
    const payload = {
      name: DOM.profileInputs.name.value.trim(),
      phone: DOM.profileInputs.phone.value.trim(),
      gender: DOM.profileInputs.gender.value,
      date_of_birth: DOM.profileInputs.dob.value || null,
      preferred_language: DOM.profileInputs.language.value.trim(),
    };
    await API.updateProfile(payload);
  },

  onAddressSubmit: async (e) => {
    e.preventDefault();
    const idx = DOM.addressInputs.id.value ? parseInt(DOM.addressInputs.id.value, 10) : null;
    const payload = {
      recipient_name: DOM.addressInputs.recipient.value.trim(),
      phone_number: DOM.addressInputs.phone.value.trim(),
      address_line: DOM.addressInputs.addressLine.value.trim(),
      postal_code: DOM.addressInputs.pincode.value.trim(),
      city: DOM.addressInputs.city.value.trim(),
      taluk_division: DOM.addressInputs.taluk.value.trim(),
      state: DOM.addressInputs.state.value.trim(),
      country: DOM.addressInputs.country.value.trim(),
      address_type: DOM.addressInputs.type.value,
      delivery_instructions: DOM.addressInputs.instructions.value.trim(),
      latitude: DOM.addressInputs.latitude.value ? parseFloat(DOM.addressInputs.latitude.value) : null,
      longitude: DOM.addressInputs.longitude.value ? parseFloat(DOM.addressInputs.longitude.value) : null,
      is_default: DOM.addressInputs.isDefault.checked,
    };
    await API.saveAddress(payload, idx);
    DOM.addressForm.reset();
    DOM.addressInputs.id.value = "";
    bootstrap.Modal.getInstance(document.getElementById("addressModal")).hide();
  },

  onAddressListClick: (ev) => {
    const editBtn = ev.target.closest(".edit-btn");
    const delBtn = ev.target.closest(".delete-btn");
    if (editBtn) {
      const idx = parseInt(editBtn.dataset.index, 10);
      const addr = addresses[idx];
      DOM.addressInputs.id.value = idx;
      DOM.addressInputs.recipient.value = addr.recipient_name || "";
      DOM.addressInputs.phone.value = addr.phone_number || "";
      DOM.addressInputs.addressLine.value = addr.address_line || "";
      DOM.addressInputs.city.value = addr.city || "";
      DOM.addressInputs.pincode.value = addr.postal_code || "";
      DOM.addressInputs.taluk.value = addr.taluk_division || "";
      DOM.addressInputs.state.value = addr.state || "";
      DOM.addressInputs.country.value = addr.country || "";
      DOM.addressInputs.type.value = addr.address_type || "Home";
      DOM.addressInputs.instructions.value = addr.delivery_instructions || "";
      DOM.addressInputs.latitude.value = addr.latitude || "";
      DOM.addressInputs.longitude.value = addr.longitude || "";
      DOM.addressInputs.isDefault.checked = !!addr.is_default;
      new bootstrap.Modal(document.getElementById("addressModal")).show();
    }
    if (delBtn) {
      const idx = parseInt(delBtn.dataset.index, 10);
      const addrId = addresses[idx].id;
      if (confirm("Delete this address?")) API.deleteAddress(addrId);
    }
  },

  onLogout: async () => {
    try {
      showLoader();
      //await apiClient.post(apiEndpoints.auth.logout);
      window.location.href = apiEndpoints.auth.logout;
    } catch (err) {
      alert("Logout failed: " + err.message);
      console.error(err);
    } finally {
      hideLoader();
    }
  }


};

// ==============================
// INITIALIZATION
// ==============================



const profileInit = () => {
  // Load user data
  API.loadUserData();
  // Attach event listeners
  DOM.addressInputs.pincode.addEventListener("blur", Handlers.onPINBlur);
  DOM.profileForm.addEventListener("submit", Handlers.onProfileSubmit);
  DOM.addressForm.addEventListener("submit", Handlers.onAddressSubmit);
  DOM.addressList.addEventListener("click", Handlers.onAddressListClick);
  DOM.logoutBtn.addEventListener("click", Handlers.onLogout);
};
// Ensure session validation runs after DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  callProtectedApi();

  // Initialize profile page
  profileInit();
});