document.addEventListener("DOMContentLoaded", () => {

  // Sample Products
  const products = [
    { id: 1, title: "Kannada Tatvapada Vol 1", author: "Author A", price: 350 },
    { id: 2, title: "Kannada Tatvapada Vol 2", author: "Author B", price: 420 },
    { id: 3, title: "Kannada Tatvapada Vol 3", author: "Author C", price: 380 },
    { id: 4, title: "Kannada Tatvapada Vol 4", author: "Author D", price: 400 },
    { id: 5, title: "Kannada Tatvapada Vol 5", author: "Author E", price: 450 },
    { id: 6, title: "Kannada Tatvapada Vol 6", author: "Author F", price: 480 },
    { id: 7, title: "Kannada Tatvapada Vol 7", author: "Author G", price: 500 },
    { id: 8, title: "Kannada Tatvapada Vol 8", author: "Author H", price: 550 }
  ];

  // Cart State
  let cart = JSON.parse(localStorage.getItem("cartItems")) || [];

  // Detect which page
  const productTableBody = document.getElementById("productTableBody");
  const cartTableBody = document.getElementById("cartTableBody");
  const cartCount = document.getElementById("cartCount");
  const goToCartDiv = document.getElementById("goToCartDiv");
  const goToCartBtn = document.getElementById("goToCartBtn");
  const userAddress = document.getElementById("userAddress");
  const cartTotal = document.getElementById("cartTotal");
  const proceedPaymentBtn = document.getElementById("proceedPaymentBtn");

  // ----------------------
  // Product Listing Page
  // ----------------------
  if (productTableBody) {

    function renderProducts() {
      productTableBody.innerHTML = "";
      products.forEach((p, idx) => {
        const inCart = cart.find(i => i.id === p.id);
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${idx + 1}</td>
          <td>${p.title}</td>
          <td>${p.author}</td>
          <td>₹${p.price}</td>
          <td class="text-center">
            <button class="btn btn-sm ${inCart ? "btn-success" : "btn-primary"} btn-toggle" data-id="${p.id}">
              <i class="bi ${inCart ? "bi-check-circle" : "bi-cart-plus"}"></i> ${inCart ? "Added" : "Add"}
            </button>
          </td>`;
        productTableBody.appendChild(row);
      });

      if (!$.fn.DataTable.isDataTable('#productTable')) {
        $('#productTable').DataTable({ pageLength: 5, lengthMenu: [5, 10, 20], columnDefs: [{ orderable: false, targets: [4] }] });
      }
    }

    function updateCartUI() {
      cartCount.textContent = cart.length;
      if (goToCartDiv) goToCartDiv.classList.toggle("d-none", cart.length === 0);
    }

    function toggleCartItem(id, btn) {
      const product = products.find(p => p.id === id);
      const inCart = cart.find(i => i.id === id);

      if (inCart) {
        cart = cart.filter(i => i.id !== id);
        btn.classList.replace("btn-success", "btn-primary");
        btn.innerHTML = `<i class="bi bi-cart-plus"></i> Add`;
      } else {
        cart.push(product);
        btn.classList.replace("btn-primary", "btn-success");
        btn.innerHTML = `<i class="bi bi-check-circle"></i> Added`;
        btn.style.transform = "scale(1.1)";
        setTimeout(() => btn.style.transform = "scale(1)", 200);
      }

      localStorage.setItem("cartItems", JSON.stringify(cart));
      updateCartUI();
    }

    document.addEventListener("click", e => {
      const btn = e.target.closest(".btn-toggle");
      if (btn) toggleCartItem(parseInt(btn.dataset.id, 10), btn);
    });

    if (goToCartBtn) goToCartBtn.addEventListener("click", () => { window.location.href = "/shopping/cart"; });

    renderProducts();
    updateCartUI();
  }

  // ----------------------
  // Cart Page
  // ----------------------
  if (cartTableBody) {
    function renderCartPage() {
      cartTableBody.innerHTML = "";
      let total = 0;

      cart.forEach((item, idx) => {
        const quantity = item.quantity || 1;
        const subtotal = item.price * quantity;
        total += subtotal;

        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${idx + 1}</td>
          <td>${item.title}</td>
          <td>${item.author}</td>
          <td>₹${item.price}</td>
          <td><input type="number" min="1" value="${quantity}" class="form-control quantity-input" data-id="${item.id}"></td>
          <td>₹${subtotal}</td>
          <td class="text-center">
            <button class="btn btn-sm btn-danger btn-remove" data-id="${item.id}">
              <i class="bi bi-trash"></i>
            </button>
          </td>`;
        cartTableBody.appendChild(row);
      });

      if (cartTotal) cartTotal.textContent = total;
    }

    document.addEventListener("input", e => {
      if (e.target.classList.contains("quantity-input")) {
        const id = parseInt(e.target.dataset.id, 10);
        const item = cart.find(i => i.id === id);
        item.quantity = parseInt(e.target.value, 10);
        localStorage.setItem("cartItems", JSON.stringify(cart));
        renderCartPage();
      }
    });

    document.addEventListener("click", e => {
      const btn = e.target.closest(".btn-remove");
      if (btn) {
        const id = parseInt(btn.dataset.id, 10);
        cart = cart.filter(i => i.id !== id);
        localStorage.setItem("cartItems", JSON.stringify(cart));
        renderCartPage();
      }
    });

    if (proceedPaymentBtn) proceedPaymentBtn.addEventListener("click", () => {
      if (!userAddress.value.trim()) {
        alert("Please enter your delivery address.");
        return;
      }
      const order = {
        items: cart,
        total: cart.reduce((sum, i) => sum + (i.price * (i.quantity || 1)), 0),
        address: userAddress.value.trim()
      };
      localStorage.setItem("currentOrder", JSON.stringify(order));
      alert("Order ready! Redirecting to payment...");
      window.location.href = "/payment"; // Replace with payment page
    });

    renderCartPage();
  }
});
