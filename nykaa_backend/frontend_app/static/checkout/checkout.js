/*********************************
 * CHECKOUT ACCOUNT STATUS (NYKAA)
 *********************************/
document.addEventListener("DOMContentLoaded", () => {
  const accountWrapper = document.getElementById("checkout-account-wrapper");
  if (!accountWrapper) return;

  fetch("/api/checkout/account-status/", {
    method: "GET",
    credentials: "include",
    headers: {
      ...(localStorage.getItem("access")
        ? { Authorization: `Bearer ${localStorage.getItem("access")}` }
        : {}),
    },
  })
    .then(res => res.json())
    .then(data => {
      // 🔐 Logged-in user → skip account
      if (data.status === "LOGGED_IN") {
        window.location.href = "/checkout/address/";
        return;
      }

      // 👤 Guest with cart → show options
      if (data.status === "GUEST") {
        accountWrapper.classList.remove("hidden");
        return;
      }

      // 🛑 Empty cart → go back to cart
      window.location.href = "/cart/";
    })
    .catch(() => {
      window.location.href = "/cart/";
    });

  // Login & Signup → OTP flow (same page)
  document.getElementById("checkout-login-btn")
    ?.addEventListener("click", () => {
      window.location.href = "/accounts/login/";
    });

  document.getElementById("checkout-signup-btn")
    ?.addEventListener("click", () => {
      window.location.href = "/accounts/login/";
    });

  // Guest → Address directly
  document.getElementById("checkout-guest-btn")
    ?.addEventListener("click", () => {
      window.location.href = "/checkout/address/";
    });
});



/*********************************
 * CSRF TOKEN HELPER (GUEST FLOW)
 *********************************/
function getCSRFToken() {
  const name = "csrftoken";
  const cookies = document.cookie.split(";");

  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(name + "=")) {
      return cookie.substring(name.length + 1);
    }
  }
  return "";
}


/*********************************
 * RAZORPAY PAYMENT – NYKAA FLOW
 *********************************/
document.addEventListener("DOMContentLoaded", () => {
  const payBtn = document.getElementById("pay-btn");
  if (!payBtn) return;

  payBtn.addEventListener("click", async () => {
    payBtn.disabled = true;
    payBtn.innerText = "Processing...";

    try {
    const res = await fetch("/api/payment/create-order/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        credentials:"include",
        body: JSON.stringify({
        order_id: localStorage.getItem("current_order_id"),
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.error || "Unable to start payment");
        resetBtn();
        return;
      }

      const options = {
        key: data.razorpay_key,
        amount: data.amount * 100,
        currency: "INR",
        name: "Nykaa Beauty",
        description: "Order Payment",
        order_id: data.razorpay_order_id,

        handler: async function (response) {
          const verifyRes = await fetch("/api/payment/verify/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCSRFToken(),
            },
            credentials:"include",
            body: JSON.stringify({
             razorpay_order_id: data.razorpay_order_id,
             razorpay_payment_id: response.razorpay_payment_id,
             razorpay_signature: response.razorpay_signature,
            }),
          });

          const verifyData = await verifyRes.json();

          if (verifyRes.ok && verifyData.status === "SUCCESS") {
            const orderId = localStorage.getItem("current_order_id");
            window.location.href = `/orders/success/?order_id=${orderId}`;
          } else {
            alert("Payment verification failed");
            resetBtn();
          }
        },

        theme: { color: "#e80071" },
      };

      new Razorpay(options).open();
    } catch (e) {
      alert("Payment failed");
      resetBtn();
    }
  });

  function resetBtn() {
    payBtn.disabled = false;
    payBtn.innerText = "Pay Now";
  }
});




