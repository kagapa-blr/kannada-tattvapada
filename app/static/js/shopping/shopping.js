import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

// ---------------- Cart helpers ----------------
let cart = JSON.parse(localStorage.getItem("cartItems")) || [];

function saveCart() {
  localStorage.setItem("cartItems", JSON.stringify(cart));
}

function isInCart(id) {
  return cart.some(item => item.id === id);
}

function getCartItem(id) {
  return cart.find(item => item.id === id);
}

function addToCart(product) {
  if (!isInCart(product.id)) {
    cart.push({ ...product, quantity: 1 });
    saveCart();
    return true;
  }
  return false;
}

function removeFromCart(id) {
  cart = cart.filter(i => i.id !== id);
  saveCart();
}

function updateCartQuantity(id, qty) {
  const item = getCartItem(id);
  if (item) {
    item.quantity = qty > 0 ? qty : 1;
    saveCart();
  }
}

function getCartTotal() {
  return cart.reduce((acc, item) => acc + (item.price * (item.quantity || 1)), 0);
}

// ---------------- Product Listing Page ----------------
function initProductListingPage() {
  const cartCount = $("#cartCount");
  const btnOpenCartModal = $("#btnOpenCartModal");
  const cartModal = new bootstrap.Modal(document.getElementById("cartModal"));
  const cartModalBody = $("#cartModalTableBody");
  const cartModalTotal = $("#cartModalTotal");
  const cartModalEmpty = $("#cartModalEmpty");

  const bookDetailsModal = new bootstrap.Modal(document.getElementById("bookDetailsModal"));
  const detailTitle = $("#detailTitle"),
    detailSubtitle = $("#detailSubtitle"),
    detailAuthor = $("#detailAuthor"),
    detailSamputa = $("#detailSamputa"),
    detailPrice = $("#detailPrice"),
    detailDiscountPrice = $("#detailDiscountPrice"),
    detailStock = $("#detailStock"),
    detailPages = $("#detailPages"),
    detailPublisher = $("#detailPublisher"),
    detailLanguage = $("#detailLanguage"),
    detailDescription = $("#detailDescription"),
    detailKoshasheershike = $("#detailKoshasheershike"),
    detailCoverImage = $("#detailCoverImage"),
    btnAddToCartFromDetails = $("#btnAddToCartFromDetails");

  let currentDetailItem = null;

  const table = $("#productTable").DataTable({
    serverSide: true,
    processing: true,
    ajax: async (data, callback) => {
      try {
        const params = new URLSearchParams({
          start: data.start,
          length: data.length,
          draw: data.draw,
          search_word: data.search.value || ""
        });
        const res = await fetch(`/books/api/?${params.toString()}`);
        const json = await res.json();
        callback({
          recordsTotal: json.recordsTotal,
          recordsFiltered: json.recordsFiltered,
          data: json.data // keep full API object
        });
      } catch (err) {
        console.error(err);
        callback({ recordsTotal: 0, recordsFiltered: 0, data: [] });
      }
    },
    columns: [
      { data: null, render: (data, type, row, meta) => meta.row + 1 },
      { data: "title" },
      { data: "author_name" },
      { data: "price", render: data => `₹${parseFloat(data).toFixed(2)}` },
      {
        data: null,
        orderable: false,
        render: data => `
          <div class="btn-action">
            <button class="btn btn-sm ${isInCart(data.id) ? "btn-success" : "btn-primary"} btn-toggle" data-id="${data.id}">
              <i class="bi ${isInCart(data.id) ? "bi-cart-check" : "bi-cart-plus"}"></i>
            </button>
            <button class="btn btn-sm btn-info btn-details" data-id="${data.id}">
              <i class="bi bi-info-circle"></i>
            </button>
          </div>`
      }
    ],
    pageLength: 10,
    lengthMenu: [10, 20, 50, 100],
    language: {
      emptyTable: "No books available",
      search: "Search by title, subtitle or author:"
    }
  });

  function updateCartCount() {
    cartCount.text(cart.length);
    cart.length > 0 ? cartCount.show() : cartCount.hide();
  }

  function toggleCartItem(id, btn) {
    const rowData = table.rows().data().toArray().find(p => p.id === id);
    if (!rowData) return;

    if (isInCart(id)) {
      removeFromCart(id);
      btn.removeClass("btn-success").addClass("btn-primary").html(`<i class="bi bi-cart-plus"></i>`);
    } else {
      addToCart(rowData);
      btn.removeClass("btn-primary").addClass("btn-success").html(`<i class="bi bi-cart-check"></i>`);
    }
    updateCartCount();
  }

  function renderCartModal() {
    cartModalBody.empty();
    if (cart.length === 0) {
      cartModalEmpty.removeClass("d-none");
      cartModalTotal.text("0.00");
      return;
    }
    cartModalEmpty.addClass("d-none");

    let total = 0;
    cart.forEach((item, i) => {
      const subtotal = item.price * (item.quantity || 1);
      total += subtotal;
      cartModalBody.append(`
        <tr>
          <td>${i + 1}</td>
          <td>${item.title}</td>
          <td>₹${item.price.toFixed(2)}</td>
          <td><input type="number" min="1" class="form-control form-control-sm cart-qty-input" data-id="${item.id}" value="${item.quantity || 1}" /></td>
          <td>₹${subtotal.toFixed(2)}</td>
          <td class="text-center"><button class="btn btn-sm btn-danger btn-remove" data-id="${item.id}"><i class="bi bi-trash"></i></button></td>
        </tr>
      `);
    });
    cartModalTotal.text(total.toFixed(2));
  }

  // ---------------- Event handlers ----------------
  $(document).on("click", ".btn-toggle", e => {
    const id = parseInt($(e.currentTarget).data("id"));
    toggleCartItem(id, $(e.currentTarget));
  });

  $(document).on("click", ".btn-details", async e => {
    const id = parseInt($(e.currentTarget).data("id"));
    try {
      const res = await fetch(`/books/api/${id}`);
      const book = await res.json();
      currentDetailItem = book;

      detailTitle.text(book.title);
      detailSubtitle.text(book.subtitle || "-");
      detailAuthor.text(book.author_name || "-");
      detailSamputa.text(book.samputa_sankhye || "-");
      detailPrice.text(book.price.toFixed(2));
      detailDiscountPrice.text(book.discount_price ? book.discount_price.toFixed(2) : "-");
      detailStock.text(book.stock_quantity || "-");
      detailPages.text(book.number_of_pages || "-");
      detailPublisher.text(book.publisher_name || "-");
      detailLanguage.text(book.language || "-");
      detailDescription.text(book.description || "-");
      detailKoshasheershike.text(book.tatvapadakosha_sheershike || "-");
      detailCoverImage.attr("src", book.cover_image_url || "/static/images/placeholder.png");

      if (isInCart(id)) {
        btnAddToCartFromDetails.removeClass("btn-primary").addClass("btn-success").html('<i class="bi bi-cart-check me-1"></i>In Cart');
      } else {
        btnAddToCartFromDetails.removeClass("btn-success").addClass("btn-primary").html('<i class="bi bi-cart-plus me-1"></i>Add to Cart');
      }

      bookDetailsModal.show();
    } catch (err) {
      console.error(err);
      alert("Failed to fetch book details.");
    }
  });

  btnAddToCartFromDetails.on("click", () => {
    if (currentDetailItem) {
      addToCart(currentDetailItem);
      updateCartCount();
      bookDetailsModal.hide();
    }
  });

  btnOpenCartModal.on("click", () => {
    renderCartModal();
    cartModal.show();
  });

  cartModalBody.on("click", ".btn-remove", e => {
    const id = parseInt($(e.currentTarget).data("id"));
    removeFromCart(id);
    renderCartModal();
    updateCartCount();
  });

  cartModalBody.on("input", ".cart-qty-input", e => {
    const id = parseInt(e.target.dataset.id);
    let val = parseInt(e.target.value);
    if (isNaN(val) || val < 1) val = 1;
    updateCartQuantity(id, val);
    renderCartModal();
  });

  $("#btnGoToCartPage").on("click", () => window.location.href = "/shopping/cart");

  updateCartCount();
}




function initCartPage() {
  const cartTableBody = $("#cartTableBody"),
    cartTotalSpan = $("#cartTotal"),
    proceedPaymentBtn = $("#proceedPaymentBtn"),
    cartEmptyMessage = $("#cartEmptyMessage"),
    confirmModal = new bootstrap.Modal(document.getElementById("confirmOrderModal")),
    confirmTotalSpan = $("#confirmTotalAmount"),
    confirmAddressText = $("#confirmAddressText"),
    confirmOrderBtn = $("#confirmOrderBtn");

  let userData = null;
  let addressData = null;

  // -----------------------
  // Render Cart Table
  // -----------------------
  function renderCart() {
    cartTableBody.empty();

    if (!cart || cart.length === 0) {
      cartEmptyMessage.removeClass("d-none");
      proceedPaymentBtn.prop("disabled", true);
      cartTotalSpan.text("0.00");
      return;
    }

    cartEmptyMessage.addClass("d-none");

    let total = 0;
    cart.forEach((item, i) => {
      const qty = item.quantity || 1;
      const subtotal = item.price * qty;
      total += subtotal;

      cartTableBody.append(`
        <tr class="cart-row">
          <td>${i + 1}</td>
          <td>${item.title}</td>
          <td>${item.author_name}</td>
          <td>₹${item.price.toFixed(2)}</td>
          <td>
            <input type="number" min="1" class="form-control form-control-sm quantity-input" data-id="${item.id}" value="${qty}" />
          </td>
          <td>₹${subtotal.toFixed(2)}</td>
          <td class="text-center">
            <button class="btn btn-sm btn-danger btn-remove" data-id="${item.id}">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        </tr>
      `);
    });

    cartTotalSpan.text(total.toFixed(2));
    updatePayButtonState();
  }

  // -----------------------
  // Enable/Disable Pay Button
  // -----------------------
  function updatePayButtonState() {
    const hasCart = cart && cart.length > 0;
    const hasAddress = addressData !== null;
    proceedPaymentBtn.prop("disabled", !(hasCart && hasAddress));
  }

  // -----------------------
  // Handle Quantity Change
  // -----------------------
  cartTableBody.on("input", ".quantity-input", e => {
    const id = parseInt(e.target.dataset.id);
    let val = parseInt(e.target.value);
    if (isNaN(val) || val < 1) val = 1;
    updateCartQuantity(id, val); // update storage
    renderCart();
  });

  // -----------------------
  // Handle Remove Item
  // -----------------------
  cartTableBody.on("click", ".btn-remove", e => {
    const id = parseInt($(e.currentTarget).data("id"));
    removeFromCart(id);
    renderCart();
  });

  // -----------------------
  // Proceed Payment
  // -----------------------
  proceedPaymentBtn.on("click", () => {
    if (!userData || !addressData) return;

    const totalAmount = getCartTotal();
    confirmTotalSpan.text(totalAmount.toFixed(2));
    confirmAddressText.text($("#fullAddress").text());
    confirmModal.show();
  });

  // -----------------------

  // -----------------------
  // Confirm Order & Cashfree Checkout
  // -----------------------
  confirmOrderBtn.on("click", async () => {
    const totalAmount = getCartTotal();
    if (totalAmount <= 0) return alert("Cart total invalid.");

    try {
      // Prepare full order payload
      const orderPayload = {
        email: userData.email,
        phone: userData.phone,
        name: userData.name || "Guest User",
        amount: totalAmount,
        user: userData,       // full user info
        address: addressData, // full address info
        items: cart,          // all cart items
        order_note: `Order for ${userData.name || userData.email} on ${new Date().toLocaleString()}`
      };

      // Call backend API to create Cashfree order
      const res = await fetch("/payment/api/v1/create-order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(orderPayload)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || "Failed to create order");
      }

      const data = await res.json();
      const paymentSessionId = data.data?.payment_session_id;
      const orderId = data.data?.order_id;

      if (!paymentSessionId || !orderId) throw new Error("Payment Session ID or Order ID missing");

      // Initialize Cashfree Checkout with redirect callbacks
      const cashfree = Cashfree({ mode: "sandbox" }); // or "production"
      cashfree.checkout({
        paymentSessionId,
        redirectTarget: "_self",
        onSuccess: function () {
          window.location.href = `/payment/success?order_id=${orderId}`;
        },
        onFailure: function () {
          window.location.href = `/payment/failure?order_id=${orderId}`;
        }
      });

      // Save order locally for tracking
      const localOrder = {
        items: cart,
        total: totalAmount,
        user: userData,
        address: addressData,
        date: new Date().toISOString(),
        order_id: orderId
      };
      localStorage.setItem("currentOrder", JSON.stringify(localOrder));

      // Clear cart after starting checkout
      cart.length = 0;
      saveCart();
      confirmModal.hide();

    } catch (err) {
      console.error("Payment initiation failed:", err);
      alert("Failed to initiate payment: " + err.message);
    }
  });


  // -----------------------
  // Fetch User Info & Address
  // -----------------------
  async function fetchUserAndAddress() {
    try {
      const res = await fetch("http://127.0.0.1:5000/shopping/api/v1/users/default/kagapa@gmail.com");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();

      console.log('json', json)

      if (json.success && json.data) {
        userData = json.data.user;
        addressData = json.data.address;

        $("#userName").text(userData.name || "-");
        $("#userEmail").text(userData.email || "-");
        $("#userPhone").text(userData.phone || "-");

        $("#fullAddress").text(
          `${addressData.recipient_name}, ${addressData.address_line}, ${addressData.city}, ${addressData.state}, ${addressData.country} - ${addressData.postal_code}, 📞 ${addressData.phone_number}`
        );

        updatePayButtonState();
      }
    } catch (err) {
      console.error("Failed to fetch user/address:", err);
    }
  }

  // -----------------------
  // Initialize
  // -----------------------
  fetchUserAndAddress();
  renderCart();
}



$(document).ready(() => {
  if ($("#productTable").length) initProductListingPage();
  else if ($("#cartTableBody").length) initCartPage();
});
