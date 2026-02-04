/*********************************
 * AUTH STATE ON LOAD
 *********************************/
document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access_token");
  if (token) updateHeaderUser();
});

/*********************************
 * HEADER LOGIN DROPDOWN
 *********************************/
document.addEventListener("DOMContentLoaded", () => {
  const signinBtn = document.getElementById("signin-btn");
  const dropdown = document.getElementById("login-dropdown");

  if (signinBtn && dropdown) {
    signinBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      dropdown.classList.toggle("hidden");
    });
  }
});

document.addEventListener("click", (e) => {
  const dropdown = document.getElementById("login-dropdown");
  const signinBtn = document.getElementById("signin-btn");

  if (!dropdown || dropdown.classList.contains("hidden")) return;

  if (!dropdown.contains(e.target) && !signinBtn.contains(e.target)) {
    dropdown.classList.add("hidden");
  }
});



document.getElementById("login-submit-btn")?.addEventListener("click", async () => {
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  const res = await fetch("/api/auth/login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();

  if (!res.ok) {
    alert("Invalid credentials");
    return;
  }

  localStorage.setItem("access_token", data.access);
  localStorage.setItem("refresh_token", data.refresh);
  localStorage.setItem("user", JSON.stringify(data.user));

  document.getElementById("login-dropdown").classList.add("hidden");
  updateHeaderUser();
});

/*********************************
 * UPDATE HEADER AFTER LOGIN
 *********************************/
function updateHeaderUser() {
  const user = JSON.parse(localStorage.getItem("user"));
  if (!user) return;

  const signinBtn = document.getElementById("signin-btn");
  const userWrapper = document.getElementById("user-wrapper");
  const userNameEl = document.getElementById("user-name");

  // Header may not exist on checkout pages
  if (signinBtn) signinBtn.classList.add("hidden");
  if (userWrapper) userWrapper.classList.remove("hidden");

  if (userNameEl) {
    userNameEl.innerText = user.name || "My Account";
  }
}

/*********************************
 * USER DROPDOWN
 *********************************/
document.getElementById("user-btn")?.addEventListener("click", (e) => {
  e.stopPropagation();
  document.getElementById("user-dropdown")?.classList.toggle("hidden");
});

document.addEventListener("click", () => {
  document.getElementById("user-dropdown")?.classList.add("hidden");
});



/*********************************
 * LOGOUT (NYKAA-CORRECT)
 *********************************/
document.getElementById("logout-btn")?.addEventListener("click", async () => {
  try {
    await fetch("/api/auth/logout/", {
      method: "POST",
      credentials: "include", // 🔥 REQUIRED
    });
  } catch (e) {
    console.error("Logout API failed");
  }

  // 🔥 Clear frontend auth
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
  localStorage.removeItem("current_order_id");

  // 🔥 Reload = new guest session
  window.location.href = "/";
});


/*********************************
 * ACCOUNT PAGE UI STATE
 *********************************/
function hideAll() {
  document.getElementById("account-choice")?.classList.add("hidden");
  document.getElementById("login-box")?.classList.add("hidden");
  document.getElementById("signup-box")?.classList.add("hidden");
}

function showLogin() {
  hideAll();
  document.getElementById("login-box")?.classList.remove("hidden");
}

function showSignup() {
  hideAll();
  document.getElementById("signup-box")?.classList.remove("hidden");
}

/*********************************
 * LOGIN
 *********************************/
async function loginUser() {
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  const res = await fetch("/api/auth/login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();
  if (!res.ok) {
    alert(data?.non_field_errors?.[0] || "Login failed");
    return;
  }

  saveAndRedirect(data);

}

/*********************************
 * SIGNUP
 *********************************/
async function signupUser() {
  const full_name = document.getElementById("signup-name").value;
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;

  const res = await fetch("/api/auth/signup/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ full_name, email, password }),
  });

  const data = await res.json();
  if (!res.ok) {
    alert("Signup failed");
    return;
  }

  saveAndRedirect(data);
  
}



document.addEventListener("DOMContentLoaded", () => {
  const sendOtpBtn = document.getElementById("send-otp-btn");
  const verifyOtpBtn = document.getElementById("verify-otp-btn");
  const otpSection = document.getElementById("otp-section");

  let currentEmail = null;
  let otpInProgress = false;



  /* ============================
     SEND OTP
  ============================ */
  sendOtpBtn?.addEventListener("click", async () => {
    if (otpInProgress) return;
    otpInProgress = true;

    const email = document.getElementById("login-email").value.trim();

    if (!email) {
      alert("Enter email");
      otpInProgress = false;
      return;
    }

    sendOtpBtn.disabled = true;
    sendOtpBtn.innerText = "Sending...";

    const res = await fetch("/api/auth/send-otp/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    if (!res.ok) {
      alert("Failed to send OTP");
      sendOtpBtn.disabled = false;
      sendOtpBtn.innerText = "Send OTP";
      otpInProgress = false;
      return;
    }

    currentEmail = email;
    otpSection.classList.remove("hidden");
    sendOtpBtn.innerText = "OTP Sent";
  });


  
  /* ============================
     VERIFY OTP
  ============================ */
  verifyOtpBtn?.addEventListener("click", async () => {
  if (verifyOtpBtn.dataset.locked === "true") return;

  const otp = document.getElementById("otp-input").value.trim();

  if (!otp || otp.length !== 6) {
    alert("Enter valid 6-digit OTP");
    return;
  }

  if (!currentEmail) {
    alert("Email missing. Please resend OTP.");
    return;
  }

  // 🔒 HARD LOCK
  verifyOtpBtn.dataset.locked = "true";
  verifyOtpBtn.disabled = true;
  verifyOtpBtn.innerText = "Verifying...";

  const res = await fetch("/api/auth/verify-otp/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: currentEmail, otp }),
  });

  const data = await res.json();

  if (!res.ok) {
    alert(data.error || "Invalid OTP");
    verifyOtpBtn.disabled = false;
    verifyOtpBtn.innerText = "Verify OTP";
    verifyOtpBtn.dataset.locked = "false";
    return;
  }

 // ✅ SAVE AUTH FIRST (CRITICAL)
  localStorage.setItem("access_token", data.access);
  localStorage.setItem("refresh_token", data.refresh);
  localStorage.setItem("user", JSON.stringify(data.user));

  // ✅ UPDATE HEADER
  updateHeaderUser();

  // ✅ NYKAA FLOW → THEN REDIRECT
  window.location.href = "/checkout/address/";
    
  // ✅ UPDATE HEADER
  updateHeaderUser();

  // ✅ NYKAA FLOW

  const next = new URLSearchParams(window.location.search).get("next");
  window.location.href = next || "/";
 });

});