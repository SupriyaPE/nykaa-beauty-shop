/*****************************************
 * CHECKOUT ACCOUNT STATUS (NYKAA FLOW)
 *****************************************/

document.addEventListener("DOMContentLoaded", () => {
    checkAccountStatus();
});

function checkAccountStatus() {
    fetch("/api/checkout/account-status/", {
        method: "GET",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            ...(localStorage.getItem("access")
                ? { Authorization: `Bearer ${localStorage.getItem("access")}` }
                : {})
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "LOGGED_IN") {
            // ✅ Auto skip account step
            window.location.href = "/checkout/address/";
        }

        if (data.status === "EMPTY") {
            alert("Your cart is empty");
            window.location.href = "/";
        }
    })
    .catch(() => {
        alert("Unable to verify checkout status");
    });
}

/*****************************************
 * BUTTON ACTIONS
 *****************************************/

function redirectToLogin() {
    window.location.href = "/login/?next=/checkout/address/";
}

function redirectToSignup() {
    window.location.href = "/signup/?next=/checkout/address/";
}

function continueAsGuest() {
    window.location.href = "/checkout/address/";
}




function goToLogin() {
  // After login, user should come back to address step
  window.location.href = "/accounts/login/?next=/checkout/address/";
}




document.addEventListener("DOMContentLoaded", () => {
  loadCheckoutSummary();
});

function loadCheckoutSummary() {
  fetch("/api/cart/", {
    credentials: "include",
    headers: authHeaders()
  })
    .then(res => res.json())
    .then(data => {
      if (!data.items || data.items.length === 0) {
        document.getElementById("co-item-count").innerText = "0";
        document.getElementById("co-you-pay").innerText = "0";
        document.getElementById("co-savings").innerText = "You are saving ₹0";
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

      const discount = mrp - totalPay;

      document.getElementById("co-item-count").innerText = totalQty;
      document.getElementById("co-you-pay").innerText = totalPay.toFixed(0);
      document.getElementById("co-savings").innerText =
        `You are saving ₹${discount > 0 ? discount.toFixed(0) : 0}`;
    });
}

/* SAME helper as bag.js */
function authHeaders() {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}