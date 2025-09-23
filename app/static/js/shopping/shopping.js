/**
 * shopping.js - Organized Shopping & Cart Logic
 */

// ---------------------- Global Cart ----------------------
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

// ---------------------- Product Listing Page ----------------------
function initProductListingPage() {
  const cartCount = $("#cartCount");
  const btnOpenCartModal = $("#btnOpenCartModal");
  const cartModal = new bootstrap.Modal(document.getElementById("cartModal"));
  const cartModalBody = $("#cartModalTableBody");
  const cartModalTotal = $("#cartModalTotal");
  const cartModalEmpty = $("#cartModalEmpty");

  const bookDetailsModal = new bootstrap.Modal(document.getElementById("bookDetailsModal"));
  const detailTitle = $("#detailTitle"), detailAuthor = $("#detailAuthor"),
    detailSamputa = $("#detailSamputa"), detailPrice = $("#detailPrice"),
    detailKoshasheershike = $("#detailKoshasheershike"),
    btnAddToCartFromDetails = $("#btnAddToCartFromDetails");
  let currentDetailItem = null;

  // Initialize Product DataTable
  const table = $("#productTable").DataTable({
    serverSide: true,
    processing: true,
    ajax: async (data, callback) => {
      try {
        const res = await fetch(`/shopping/api/v1/orders/catalog?offset=${data.start}&limit=${data.length}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();

        const products = json.items.map(item => ({
          id: item.id,
          title: item.tatvapadakosha_sheershike || `Samputa ${item.samputa_sankhye}`,
          author: item.tatvapadakarara_hesaru || `Author ID ${item.tatvapada_author_id}`,
          samputa: item.samputa_sankhye,
          price: parseFloat(item.price),
          kosha: item.tatvapadakosha_sheershike || ""
        }));

        callback({ recordsTotal: json.total, recordsFiltered: json.total, data: products });
      } catch (err) {
        console.error(err);
        callback({ recordsTotal: 0, recordsFiltered: 0, data: [] });
      }
    },
    columns: [
      { data: null, render: (data, type, row, meta) => meta.row + 1 },
      { data: "title" },
      { data: "author" },
      { data: "price", render: data => `₹${data.toFixed(2)}` },
      {
        data: null, orderable: false,
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
    language: { emptyTable: "No products available" }
  });

  // ---------------- Update Cart Count ----------------
  function updateCartCount() {
    cartCount.text(cart.length);
  }

  // ---------------- Toggle Cart Item ----------------
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

  // ---------------- Render Cart Modal ----------------
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

  // ---------------- Event Handlers ----------------
  $(document).on("click", ".btn-toggle", e => {
    const id = parseInt($(e.currentTarget).data("id"));
    toggleCartItem(id, $(e.currentTarget));
    table.ajax.reload(null, false);
  });

  $(document).on("click", ".btn-details", e => {
    const id = parseInt($(e.currentTarget).data("id"));
    const data = table.rows().data().toArray().find(d => d.id === id);
    if (!data) return;

    currentDetailItem = data;
    detailTitle.text(data.title);
    detailAuthor.text(data.author);
    detailSamputa.text(data.samputa);
    detailPrice.text(data.price.toFixed(2));
    detailKoshasheershike.text(data.kosha);

    if (isInCart(id)) {
      btnAddToCartFromDetails.removeClass("btn-primary").addClass("btn-success").html('<i class="bi bi-cart-check me-1"></i>In Cart');
    } else {
      btnAddToCartFromDetails.removeClass("btn-success").addClass("btn-primary").html('<i class="bi bi-cart-plus me-1"></i>Add to Cart');
    }

    bookDetailsModal.show();
  });

  btnAddToCartFromDetails.on("click", () => {
    if (currentDetailItem) {
      addToCart(currentDetailItem);
      updateCartCount();
      bookDetailsModal.hide();
      table.ajax.reload(null, false);
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
    table.ajax.reload(null, false);
    updateCartCount();
  });

  cartModalBody.on("input", ".cart-qty-input", e => {
    const id = parseInt(e.target.dataset.id);
    let val = parseInt(e.target.value);
    if (isNaN(val) || val < 1) val = 1;
    updateCartQuantity(id, val);
    renderCartModal();
  });

  $("#btnGoToCartPage").on("click", () => { window.location.href = "/shopping/cart"; });

  updateCartCount();
}

// ---------------------- Cart Page ----------------------
function initCartPage() {
  const cartTableBody = $("#cartTableBody"),
    cartTotalSpan = $("#cartTotal"),
    proceedPaymentBtn = $("#proceedPaymentBtn"),
    cartEmptyMessage = $("#cartEmptyMessage"),
    confirmModal = new bootstrap.Modal(document.getElementById("confirmOrderModal")),
    confirmTotalSpan = $("#confirmTotalAmount"),
    confirmAddressText = $("#confirmAddressText"),
    confirmOrderBtn = $("#confirmOrderBtn");

  // ---------------- Render Cart Table ----------------
  function renderCart() {
    cartTableBody.empty();

    if (cart.length === 0) {
      cartEmptyMessage.removeClass("d-none");
      proceedPaymentBtn.prop("disabled", true);
      cartTotalSpan.text("0.00");
      return;
    }

    cartEmptyMessage.addClass("d-none");
    proceedPaymentBtn.prop("disabled", cart.length === 0);

    let total = 0;
    cart.forEach((item, i) => {
      const qty = item.quantity || 1;
      const subtotal = item.price * qty;
      total += subtotal;
      cartTableBody.append(`
                <tr>
                    <td>${i + 1}</td>
                    <td>${item.title}</td>
                    <td>${item.author}</td>
                    <td>₹${item.price.toFixed(2)}</td>
                    <td><input type="number" min="1" class="form-control form-control-sm quantity-input" data-id="${item.id}" value="${qty}" /></td>
                    <td>₹${subtotal.toFixed(2)}</td>
                    <td class="text-center"><button class="btn btn-sm btn-danger btn-remove" data-id="${item.id}"><i class="bi bi-trash"></i></button></td>
                </tr>
            `);
    });
    cartTotalSpan.text(total.toFixed(2));
  }

  // ---------------- Event Handlers ----------------
  cartTableBody.on("input", ".quantity-input", e => {
    const id = parseInt(e.target.dataset.id);
    let val = parseInt(e.target.value);
    if (isNaN(val) || val < 1) val = 1;
    updateCartQuantity(id, val);
    renderCart();
  });

  cartTableBody.on("click", ".btn-remove", e => {
    const id = parseInt($(e.currentTarget).data("id"));
    removeFromCart(id);
    renderCart();
  });

  proceedPaymentBtn.on("click", () => {
    confirmTotalSpan.text(getCartTotal().toFixed(2));

    // Get address from display card
    const addressText = [
      $("#addrRecipient").text(),
      $("#addrLine").text(),
      $("#addrCityTaluk").text(),
      $("#addrStateCountry").text(),
      $("#addrPostal").text(),
      $("#addrPhone").text()
    ].join(", ");

    confirmAddressText.text(addressText);
    confirmModal.show();
  });

  confirmOrderBtn.on("click", () => {
    const order = {
      items: cart,
      total: getCartTotal(),
      date: new Date().toISOString()
    };
    localStorage.setItem("currentOrder", JSON.stringify(order));
    cart.length = 0;
    saveCart();
    confirmModal.hide();
    alert("Order confirmed! Redirecting to payment page...");
    window.location.href = "/shopping/payment";
  });

  // ---------------- Fetch Default Address ----------------
  async function fetchDefaultAddress() {
    try {
      const res = await fetch('http://127.0.0.1:5000/shopping/api/v1/users/kagapa@gmail.com/addresses');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();

      if (json.success && json.data.length > 0) {
        const defaultAddr = json.data.find(a => a.is_default) || json.data[0];
        if (defaultAddr) {
          $("#addrRecipient").text(defaultAddr.recipient_name || "-");
          $("#addrLine").text(defaultAddr.address_line || "-");
          $("#addrType").text(defaultAddr.address_type || "-");
          $("#addrCityTaluk").text(`${defaultAddr.city || "-"} / ${defaultAddr.taluk_division || "-"}`);
          $("#addrStateCountry").text(`${defaultAddr.state || "-"} / ${defaultAddr.country || "-"}`);
          $("#addrPostal").text(defaultAddr.postal_code || "-");
          $("#addrPhone").text(defaultAddr.phone_number || "-");
          $("#addrInstructions").text(defaultAddr.delivery_instructions || "-");

          proceedPaymentBtn.prop("disabled", cart.length === 0);
        }
      }
    } catch (err) {
      console.error("Failed to fetch addresses:", err);
    }
  }

  fetchDefaultAddress();
  renderCart();
}

// ---------------------- Auto Init ----------------------
$(document).ready(() => {
  if ($("#productTable").length) initProductListingPage();
  else if ($("#cartTableBody").length) initCartPage();
});
