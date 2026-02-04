document.addEventListener("DOMContentLoaded", () => {

  /* ===============================
     AUTH HEADER HELPER (🔥 FIX)
  =============================== */
  function authHeaders() {
    const token = localStorage.getItem("access_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  const bagBtn = document.getElementById("header-bag-icon");
  const bagDrawer = document.getElementById("bag-drawer");
  const bagOverlay = document.getElementById("bag-overlay");
  const bagClose = document.getElementById("bag-close-btn");

  const bagBody = document.getElementById("bag-body");
  const footerTotal = document.getElementById("footer-total");

  const headerBagCount = document.getElementById("global-bag-count");
  const bagCountUI = document.getElementById("bag-count-ui");

  /* ===============================
     OPEN / CLOSE BAG
  =============================== */
  function openBag() {
    bagDrawer.classList.remove("hidden");
    bagOverlay.classList.remove("hidden");
    document.body.classList.add("bag-open");
    loadBagData();
  }

  function closeBag() {
    bagDrawer.classList.add("hidden");
    bagOverlay.classList.add("hidden");
    document.body.classList.remove("bag-open");
  }

  bagBtn?.addEventListener("click", openBag);
  bagOverlay?.addEventListener("click", closeBag);
  bagClose?.addEventListener("click", closeBag);

  /* ===============================
     LOAD BAG DATA (🔥 FIXED)
  =============================== */
  window.loadBagData = function () {
    bagBody.innerHTML = "<p>Loading your bag...</p>";

    fetch("/api/cart/", {
      credentials: "include",
      headers: {
        ...authHeaders()
      }
    })
      .then(res => res.json())
      .then(data => {

        bagBody.innerHTML = "";
        let total = 0;
        let totalQty = 0;

        if (!data.items || data.items.length === 0) {
          bagBody.innerHTML = "<p class='bag-placeholder'>Your bag is empty</p>";
          footerTotal.innerText = "₹0";
          bagCountUI.innerText = "0";
          headerBagCount.classList.add("hidden");
          return;
        }

        data.items.forEach(item => {
          total += item.subtotal;
          totalQty += item.quantity;

         bagBody.innerHTML += `
            <div class="bag-item" data-id="${item.id}">
              <div class="bag-left">
                <div class="bag-item-name">${item.product}</div>
                <div class="bag-item-variant">${item.variant}</div>

                <div class="bag-meta">
                  <span class="bag-qty" onclick="openQtySelector(${item.id}, ${item.quantity})">
                    Qty: ${item.quantity} ▼
                  </span>
                  <button class="remove-btn" title="Remove">🗑</button>
                </div>

                <div class="bag-pay">
                  You Pay <strong>₹${item.subtotal}</strong>
                </div>
              </div>
            </div>
          `;
        });

        bagBody.innerHTML += `
            <div class="bag-price-details">
              <h4>Price Details</h4>

              <div class="price-row">
                <span>Bag MRP (${totalQty} items)</span>
                <span id="bag-mrp">₹0</span>
              </div>

              <div class="price-row">
                <span>Bag Discount</span>
                <span class="discount">− ₹245</span>
              </div>

              <div class="price-row">
                <span>Shipping and Platform Fee</span>
                <span>₹9</span>
              </div>

              <div class="price-row total">
                <span>You Pay</span>
                <span id="bag-you-pay">₹0</span>
              </div>
            </div>
          `;
  document.getElementById("bag-mrp").innerText = `₹${(total + 245).toFixed(2)}`;
  document.getElementById("bag-you-pay").innerText = `₹${total.toFixed(2)}`;
        footerTotal.innerText = `₹${total.toFixed(2)}`;
        bagCountUI.innerText = totalQty;
        headerBagCount.innerText = totalQty;
        headerBagCount.classList.remove("hidden");
      });
  };

  /* ===============================
     UPDATE / REMOVE / PROCEED
  =============================== */
  document.addEventListener("click", (e) => {

    // REMOVE ITEM
    if (e.target.classList.contains("remove-btn")) {
      const itemId = e.target.closest(".bag-item").dataset.id;

      fetch("/api/cart/remove/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders()
        },
        body: JSON.stringify({ item_id: itemId })
      }).then(loadBagData);
    }

    // UPDATE QUANTITY
    if (e.target.classList.contains("qty-btn")) {
      const itemId = e.target.closest(".bag-item").dataset.id;

      fetch("/api/cart/update/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders()
        },
        body: JSON.stringify({
          item_id: itemId,
          action: e.target.dataset.action
        })
      }).then(loadBagData);
    }

    // PROCEED TO CHECKOUT
    if (e.target.classList.contains("bag-proceed-btn")) {
      proceedToCheckout();
    }
  });

});

/* ===============================
   CHECKOUT ROUTING (UNCHANGED)
=============================== */
function proceedToCheckout() {
  fetch("/api/checkout/account-status/", {
    credentials: "include",
    headers: {
      Authorization: localStorage.getItem("access_token")
        ? `Bearer ${localStorage.getItem("access_token")}`
        : ""
    }
  })
    .then(res => res.json())
    .then(data => {

      if (data.status === "LOGGED_IN") {
        window.location.href = "/checkout/address/";
        return;
      }

      if (data.status === "GUEST") {
        window.location.href = "/checkout/account/";
        return;
      }

      alert("Your cart is empty");
    })
    .catch(() => {
      alert("Checkout failed. Try again.");
    });
}


// QUANTITY CHANGE //

let selectedItemId = null;
let selectedCurrentQty = null;

function openQtySelector(itemId, currentQty) {
  selectedItemId = itemId;
  selectedCurrentQty = currentQty;

  const sheet = document.getElementById("qty-sheet");
  const options = document.getElementById("qty-options");

  options.innerHTML = "";

  for (let i = 1; i <= 5; i++) {
    options.innerHTML += `
      <label class="qty-option">
        <input type="radio" name="qty" ${i === currentQty ? "checked" : ""} 
               onchange="updateQty(${i})">
        ${i}
      </label>
    `;
  }

  sheet.classList.remove("hidden");
}

function closeQtySheet() {
  document.getElementById("qty-sheet").classList.add("hidden");
}

function updateQty(newQty) {
  if (newQty === selectedCurrentQty) {
    closeQtySheet();
    return;
  }

  const action = newQty > selectedCurrentQty ? "increase" : "decrease";
  const diff = Math.abs(newQty - selectedCurrentQty);

  let chain = Promise.resolve();

  for (let i = 0; i < diff; i++) {
    chain = chain.then(() =>
      fetch("/api/cart/update/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders()
        },
        body: JSON.stringify({
          item_id: selectedItemId,
          action: action
        })
      })
    );
  }

  chain.then(() => {
    closeQtySheet();
    loadBagData();
  });
}