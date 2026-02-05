/*********************************
 * GLOBAL STATE
 *********************************/
let currentEmail = null;
let otpInProgress = false;

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

/*********************************
 * UPDATE HEADER AFTER LOGIN
 *********************************/
function updateHeaderUser() {
  const user = JSON.parse(localStorage.getItem("user"));
  if (!user) return;

  const signinBtn = document.getElementById("signin-btn");
  const userWrapper = document.getElementById("user-wrapper");
  const userNameEl = document.getElementById("user-name");

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
 * LOGOUT (NYKAA SAFE)
 *********************************/
document.getElementById("logout-btn")?.addEventListener("click", async () => {
  try {
    await fetch("/api/auth/logout/", {
      method: "POST",
      credentials: "include"
    });
  } catch {}

  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
  localStorage.removeItem("current_order_id");

  window.location.href = "/";
});

/*********************************
 * OTP FLOW (HEADER + ACCOUNT)
 *********************************/
document.addEventListener("DOMContentLoaded", () => {
  const sendOtpBtn = document.getElementById("send-otp-btn");
  const verifyOtpBtn = document.getElementById("verify-otp-btn");
  const completeSignupBtn = document.getElementById("complete-signup-btn");
  const otpSection = document.getElementById("otp-section");
  const signupNameInput = document.getElementById("signup-name");

  /* ============================
     SEND OTP
  ============================ */
  sendOtpBtn?.addEventListener("click", async () => {
    if (otpInProgress) return;
    otpInProgress = true;

    const emailInput = document.getElementById("login-email");
    const email = emailInput?.value.trim();

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
      body: JSON.stringify({ email })
    });

    if (!res.ok) {
      alert("Failed to send OTP");
      sendOtpBtn.disabled = false;
      sendOtpBtn.innerText = "Send OTP";
      otpInProgress = false;
      return;
    }

    currentEmail = email;
    otpSection?.classList.remove("hidden");
    sendOtpBtn.innerText = "OTP Sent";
    sendOtpBtn.disabled = false;
    otpInProgress = false;
  });

  /* ============================
     VERIFY OTP
  ============================ */
  verifyOtpBtn?.addEventListener("click", async () => {
    if (verifyOtpBtn.dataset.locked === "true") return;

    const otp = document.getElementById("otp-input")?.value.trim();

    if (!otp || otp.length !== 6) {
      alert("Enter valid 6-digit OTP");
      return;
    }

    if (!currentEmail) {
      alert("Email missing. Please resend OTP.");
      return;
    }

    verifyOtpBtn.dataset.locked = "true";
    verifyOtpBtn.disabled = true;
    verifyOtpBtn.innerText = "Verifying...";

    const res = await fetch("/api/auth/verify-otp/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: currentEmail, otp })
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "Invalid OTP");
      verifyOtpBtn.disabled = false;
      verifyOtpBtn.innerText = "Verify OTP";
      verifyOtpBtn.dataset.locked = "false";
      return;
    }

    // ✅ EXISTING USER → LOGIN
    if (data.is_new_user === false) {
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      localStorage.setItem("user", JSON.stringify(data.user));

      updateHeaderUser();

      const next = new URLSearchParams(window.location.search).get("next");
      window.location.href = next || "/";
      return;
    }

    // 🆕 NEW USER → ASK NAME
    signupNameInput?.classList.remove("hidden");
    completeSignupBtn?.classList.remove("hidden");
    verifyOtpBtn.classList.add("hidden");
  });

  /* ============================
     COMPLETE SIGNUP
  ============================ */
  completeSignupBtn?.addEventListener("click", async () => {
    const fullName = signupNameInput?.value.trim();

    if (!fullName) {
      alert("Please enter your name");
      return;
    }

    const res = await fetch("/api/auth/complete-signup/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: currentEmail,
        full_name: fullName
      })
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "Signup failed");
      return;
    }

    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
    localStorage.setItem("user", JSON.stringify(data.user));

    updateHeaderUser();

    const next = new URLSearchParams(window.location.search).get("next");
    window.location.href = next || "/";
  });
});