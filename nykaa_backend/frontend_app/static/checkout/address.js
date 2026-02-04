/*****************************************
 * ADDRESS PAGE – NYKAA FLOW (FINAL FIX)
 *****************************************/

const ACCESS_TOKEN = localStorage.getItem("access_token");


document.addEventListener("DOMContentLoaded", () => {
  detectUserType();
//   loadBagSummary();
});

/*****************************************
 * DETECT USER TYPE (SINGLE SOURCE)
 *****************************************/
function detectUserType() {
  fetch("/api/checkout/account-status/", {
    method: "GET",
    credentials: "include",
    headers: {
      ...(ACCESS_TOKEN ? { Authorization: `Bearer ${ACCESS_TOKEN}` } : {})
    }
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "LOGGED_IN") {
      document.getElementById("saved-addresses").style.display = "block";
      loadSavedAddresses();
      return;
    }
    openAddressDrawer();
  })
  .catch(() => {
    openAddressDrawer();
  });
}

/*****************************************
 * LOAD SAVED ADDRESSES (AUTH USER ONLY)
 *****************************************/
function loadSavedAddresses() {
  fetch("/api/addresses/", {
    headers: {
      Authorization: `Bearer ${ACCESS_TOKEN}`
    }
  })
  .then(res => res.json())
  .then(addresses => {
    const list = document.getElementById("address-list");
    list.innerHTML = "";

    addresses.forEach(addr => {
      const div = document.createElement("div");
      div.className = "address-card";
      div.innerHTML = `
        <p><strong>${addr.name}</strong></p>
        <p>${addr.address_line}, ${addr.city}, ${addr.state} - ${addr.pincode}</p>
        <button onclick="deliverHere(${addr.id})">Deliver Here</button>
      `;
      list.appendChild(div);
    });
  });
}

/*****************************************
 * DRAWER CONTROLS
 *****************************************/
function openAddressDrawer() {
  document.getElementById("address-drawer")?.classList.add("open");
  document.getElementById("drawer-backdrop")?.classList.add("show");
}

function closeAddressDrawer() {
  document.getElementById("address-drawer")?.classList.remove("open");
  document.getElementById("drawer-backdrop")?.classList.remove("show");
}

/*****************************************
 * ADD NEW ADDRESS (LOGGED-IN)
 *****************************************/
function showAddressForm() {
  openAddressDrawer();
}

/*****************************************
 * SAVE ADDRESS & CREATE ORDER
 *****************************************/
function saveAddressAndProceed() {
  const ACCESS_TOKEN = localStorage.getItem("access_token");

  const data = {
    name: document.getElementById("name").value.trim(),
    mobile: document.getElementById("mobile").value.trim(),
    address_line: document.getElementById("address_line").value.trim(),
    city: document.getElementById("city").value.trim(),
    state: document.getElementById("state").value.trim(),
    pincode: document.getElementById("pincode").value.trim(),
  };

  // 🔐 LOGGED-IN USER → SAVE ADDRESS FIRST
  if (ACCESS_TOKEN) {
    fetch("/api/addresses/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${ACCESS_TOKEN}`,
      },
      body: JSON.stringify(data),
    })
    .then(res => res.json())
    .then(() => {
      // ✅ AFTER saving address → create order
      createOrder(data);
    })
    .catch(() => alert("Address save failed"));
    return;
  }

  // 👤 GUEST → DIRECT ORDER (no DB save)
  createOrder(data);
}
// ***********************************************

function createOrder(addressData) {
  fetch("/api/orders/create/", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(ACCESS_TOKEN ? { Authorization: `Bearer ${ACCESS_TOKEN}` } : {})
    },
    body: JSON.stringify(addressData)
  })
  .then(res => res.json())
  .then(data => {
    if (!data.order_id) {
      alert("Order creation failed");
      return;
    }
    localStorage.setItem("current_order_id", data.order_id);
    window.location.href = "/checkout/payment/";
  })
  .catch(() => alert("Order creation failed"));
}

/*****************************************
 * DELIVER HERE (SAVED ADDRESS)
 *****************************************/
function deliverHere(addressId) {
  fetch("/api/orders/create/", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${ACCESS_TOKEN}`
    },
    body: JSON.stringify({ address_id: addressId })
  })
  .then(res => res.json())
  .then(data => {
    localStorage.setItem("current_order_id", data.order_id);
    window.location.href = "/checkout/payment/";
  });
}

/*****************************************
 * BAG SUMMARY (TEMP)
 *****************************************/
function loadBagSummary() {
  document.getElementById("item-count").innerText = "1";
  document.getElementById("total-mrp").innerText = "₹422";
  document.getElementById("you-save").innerText = "₹137";
  document.getElementById("grand-total").innerText = "₹422";
}





document.addEventListener("DOMContentLoaded", () => {
  loadAddressSummary();
});

function loadAddressSummary() {
  fetch("/api/cart/", {
    credentials: "include",
    headers: authHeaders()
  })
    .then(res => res.json())
    .then(data => {

      if (!data.items || data.items.length === 0) {
        document.getElementById("item-count").innerText = "0";
        document.getElementById("total-mrp").innerText = "₹0";
        document.getElementById("you-save").innerText = "₹0";
        document.getElementById("grand-total").innerText = "₹0";
        return;
      }

      let totalQty = 0;
      let totalPay = 0;
      let mrp = 0;

      data.items.forEach(item => {
        totalQty += item.quantity;
        totalPay += item.subtotal;
        mrp += item.price * item.quantity;
      });

      const savings = mrp - totalPay;

      document.getElementById("item-count").innerText = totalQty;
      document.getElementById("total-mrp").innerText = `₹${mrp.toFixed(0)}`;
      document.getElementById("you-save").innerText = `₹${savings > 0 ? savings.toFixed(0) : 0}`;
      document.getElementById("grand-total").innerText = `₹${totalPay.toFixed(0)}`;
    });
}

/* SAME helper as bag & account */
function authHeaders() {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}