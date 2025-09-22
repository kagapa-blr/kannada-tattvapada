/**
 * shopping.js for Kannada Tatvapada Shop
 * Fetches product catalog from backend API, supports server-side pagination, cart management, and order workflow.
 */

let cart = loadCart();

// -------------------- Cart Storage --------------------
function loadCart() {
  try {
    return JSON.parse(localStorage.getItem("cartItems")) || [];
  } catch {
    return [];
  }
}

function saveCart() {
  localStorage.setItem("cartItems", JSON.stringify(cart));
}

function isInCart(productId) {
  return cart.some(item => item.id === productId);
}

function getCartItem(productId) {
  return cart.find(item => item.id === productId);
}

function addToCart(product) {
  if (!isInCart(product.id)) {
    cart.push({ ...product, quantity: 1 });
    saveCart();
    return true;
  }
  return false;
}

function removeFromCart(productId) {
  cart = cart.filter(item => item.id !== productId);
  saveCart();
}

function updateCartItemQuantity(productId, quantity) {
  const item = getCartItem(productId);
  if (item) {
    item.quantity = quantity > 0 ? quantity : 1;
    saveCart();
  }
}

function getCartTotal() {
  return cart.reduce((acc, item) => acc + item.price * (item.quantity || 1), 0);
}

// -------------------- Product Listing Page --------------------
export function initProductListingPage() {
  const productTableBody = document.getElementById("productTableBody");
  const cartCount = document.getElementById("cartCount");
  const btnOpenCartModal = document.getElementById("btnOpenCartModal");
  const cartModal = new bootstrap.Modal(document.getElementById("cartModal"), { keyboard: false });
  const cartModalBody = document.getElementById("cartModalTableBody");
  const cartModalTotal = document.getElementById("cartModalTotal");
  const cartModalEmpty = document.getElementById("cartModalEmpty");
  const btnGoToCartPage = document.getElementById("btnGoToCartPage");

  // Initialize DataTable with server-side processing
  const table = $("#productTable").DataTable({
    serverSide: true,
    processing: true,
    ajax: async (data, callback) => {
      const offset = data.start;
      const limit = data.length;

      try {
        const res = await fetch(`/shopping/api/v1/orders/catalog?offset=${offset}&limit=${limit}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();

        const products = json.items.map(item => ({
          id: item.id,
          title: item.tatvapada_sheershike || `Samputa ${item.samputa_sankhye}`,
          author: item.tatvapadakosha_sheershike || `Author ID ${item.tatvapada_author_id}`,
          price: parseFloat(item.price)
        }));

        callback({
          recordsTotal: json.total,
          recordsFiltered: json.total,
          data: products
        });
      } catch (err) {
        console.error("Error fetching products:", err);
        callback({
          recordsTotal: 0,
          recordsFiltered: 0,
          data: []
        });
      }
    },
    columns: [
      { data: null, render: (data, type, row, meta) => meta.row + 1 },
      { data: "title" },
      { data: "author" },
      { data: "price", render: (data) => `₹${data}` },
      {
        data: null,
        orderable: false,
        render: (data) => {
          const inCart = isInCart(data.id);
          return `<button type="button" class="btn btn-sm ${inCart ? "btn-success" : "btn-primary"} btn-toggle" data-id="${data.id}">
          ${inCart ? "Added" : "Add"}
        </button>`;
        }
      }
    ],
    pageLength: 10,             // default page length
    lengthMenu: [10, 20, 50, 100], // dropdown options
    language: { emptyTable: "No products available" }
  });


  function updateCartCount() {
    cartCount.textContent = cart.length;
  }

  function toggleCartItem(productId, button) {
    const rowData = table.rows().data().toArray().find(p => p.id === productId);
    if (!rowData) return;

    if (isInCart(productId)) {
      removeFromCart(productId);
      button.classList.replace("btn-success", "btn-primary");
      button.textContent = "Add";
    } else {
      addToCart(rowData);
      button.classList.replace("btn-primary", "btn-success");
      button.textContent = "Added";
    }
    updateCartCount();
  }

  function renderCartModal() {
    cartModalBody.innerHTML = "";
    if (cart.length === 0) {
      cartModalEmpty.classList.remove("d-none");
      cartModalTotal.textContent = "0.00";
      return;
    } else {
      cartModalEmpty.classList.add("d-none");
    }

    let total = 0;
    cart.forEach((item, index) => {
      const subtotal = item.price * (item.quantity || 1);
      total += subtotal;
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${index + 1}</td>
        <td>${item.title}</td>
        <td>₹${item.price}</td>
        <td>
          <input type="number" min="1" class="form-control form-control-sm cart-qty-input" data-id="${item.id}" value="${item.quantity || 1}" />
        </td>
        <td>₹${subtotal.toFixed(2)}</td>
        <td class="text-center">
          <button type="button" class="btn btn-sm btn-danger btn-remove" data-id="${item.id}">Remove</button>
        </td>
      `;
      cartModalBody.appendChild(tr);
    });
    cartModalTotal.textContent = total.toFixed(2);
  }

  document.body.addEventListener("click", (e) => {
    const toggleBtn = e.target.closest(".btn-toggle");
    if (toggleBtn) {
      const id = parseInt(toggleBtn.dataset.id, 10);
      toggleCartItem(id, toggleBtn);
      table.ajax.reload(null, false); // refresh current page
    }
  });

  btnOpenCartModal.addEventListener("click", () => {
    renderCartModal();
    cartModal.show();
  });

  cartModalBody.addEventListener("click", (e) => {
    const btnRemove = e.target.closest(".btn-remove");
    if (btnRemove) {
      const id = parseInt(btnRemove.dataset.id, 10);
      removeFromCart(id);
      renderCartModal();
      table.ajax.reload(null, false);
      updateCartCount();
    }
  });

  cartModalBody.addEventListener("input", (e) => {
    if (e.target.classList.contains("cart-qty-input")) {
      const id = parseInt(e.target.dataset.id, 10);
      let val = parseInt(e.target.value, 10);
      if (isNaN(val) || val < 1) val = 1;
      updateCartItemQuantity(id, val);
      renderCartModal();
    }
  });

  btnGoToCartPage.addEventListener("click", () => {
    window.location.href = "cart.html";
  });

  updateCartCount();
}

// -------------------- Cart Page --------------------
export function initCartPage() {
  const cartTableBody = document.getElementById("cartTableBody");
  const cartTotalSpan = document.getElementById("cartTotal");
  const userAddress = document.getElementById("userAddress");
  const proceedPaymentBtn = document.getElementById("proceedPaymentBtn");
  const cartEmptyMessage = document.getElementById("cartEmptyMessage");

  const confirmModal = new bootstrap.Modal(document.getElementById("confirmOrderModal"), { keyboard: false });
  const confirmTotalSpan = document.getElementById("confirmTotalAmount");
  const confirmAddressText = document.getElementById("confirmAddressText");
  const confirmOrderBtn = document.getElementById("confirmOrderBtn");

  function renderCart() {
    cartTableBody.innerHTML = "";
    if (cart.length === 0) {
      cartEmptyMessage.classList.remove("d-none");
      proceedPaymentBtn.disabled = true;
      cartTotalSpan.textContent = "0.00";
      return;
    } else {
      cartEmptyMessage.classList.add("d-none");
      proceedPaymentBtn.disabled = false;
    }

    let total = 0;
    cart.forEach((item, index) => {
      const quantity = item.quantity || 1;
      const subtotal = item.price * quantity;
      total += subtotal;
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${index + 1}</td>
        <td>${item.title}</td>
        <td>${item.author}</td>
        <td>₹${item.price}</td>
        <td>
          <input type="number" min="1" value="${quantity}" class="form-control form-control-sm quantity-input" data-id="${item.id}" />
        </td>
        <td>₹${subtotal.toFixed(2)}</td>
        <td class="text-center">
          <button type="button" class="btn btn-sm btn-danger btn-remove" data-id="${item.id}">Remove</button>
        </td>
      `;
      cartTableBody.appendChild(tr);
    });
    cartTotalSpan.textContent = total.toFixed(2);
  }

  cartTableBody.addEventListener("input", (e) => {
    if (e.target.classList.contains("quantity-input")) {
      const id = parseInt(e.target.dataset.id, 10);
      let val = parseInt(e.target.value, 10);
      if (isNaN(val) || val < 1) val = 1;
      updateCartItemQuantity(id, val);
      renderCart();
    }
  });

  cartTableBody.addEventListener("click", (e) => {
    const btnRemove = e.target.closest(".btn-remove");
    if (btnRemove) {
      const id = parseInt(btnRemove.dataset.id, 10);
      removeFromCart(id);
      renderCart();
    }
  });

  userAddress.addEventListener("input", () => {
    proceedPaymentBtn.disabled = userAddress.value.trim() === "" || cart.length === 0;
  });

  proceedPaymentBtn.addEventListener("click", () => {
    if (userAddress.value.trim() === "") {
      alert("Please enter your delivery address.");
      return;
    }

    confirmTotalSpan.textContent = getCartTotal().toFixed(2);
    confirmAddressText.textContent = userAddress.value.trim();
    confirmModal.show();
  });

  confirmOrderBtn.addEventListener("click", () => {
    const order = {
      items: cart,
      total: getCartTotal(),
      address: userAddress.value.trim(),
      date: new Date().toISOString()
    };
    localStorage.setItem("currentOrder", JSON.stringify(order));
    cart.length = 0;
    saveCart();

    confirmModal.hide();
    alert("Order confirmed! Redirecting to payment page...");
    window.location.href = "payment.html";
  });

  renderCart();
  proceedPaymentBtn.disabled = userAddress.value.trim() === "" || cart.length === 0;
}

// -------------------- Init --------------------
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("productTableBody")) {
    initProductListingPage();
  } else if (document.getElementById("cartTableBody")) {
    initCartPage();
  }
});
