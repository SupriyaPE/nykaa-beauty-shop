document.addEventListener("DOMContentLoaded", () => {

  function authHeaders() {
    const token = localStorage.getItem("access_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  const addBtn = document.getElementById("pd-add-btn");
  if (!addBtn || addBtn.dataset.bound === "true") return;
  addBtn.dataset.bound = "true";

  const variants = document.querySelectorAll(".variant-box");
  const priceEl = document.getElementById("price");
  const resultEl = document.getElementById("pincode-result");

  let lastAddedVariant = null;
  let isAdding = false;

  // 🔑 DELIVERY STATE (FIX)
  let deliveryChecked = false;
  let deliveryAllowed = false;
  let checkedVariantId = null;

  /* ===============================
     VARIANT SELECTION
  =============================== */
  variants.forEach(v => {
    v.addEventListener("click", () => {

      variants.forEach(x => x.classList.remove("active"));
      v.classList.add("active");

      const vid = v.dataset.variant;
      priceEl.innerText = "₹" + v.dataset.price;
      addBtn.dataset.variant = vid;

      // 🔥 RESET DELIVERY STATE ON VARIANT CHANGE
      deliveryChecked = false;
      deliveryAllowed = false;
      checkedVariantId = null;

      if (resultEl) resultEl.innerText = "";

      if (vid !== lastAddedVariant) {
        addBtn.innerText = "ADD TO BAG";
        addBtn.classList.remove("added");
        addBtn.disabled = false;
      } else {
        addBtn.innerText = "ADDED";
        addBtn.classList.add("added");
        addBtn.disabled = true;
      }
    });
  });

  /* ===============================
     ADD TO BAG (STRICT)
  =============================== */
  addBtn.addEventListener("click", () => {

    const variantId = addBtn.dataset.variant;
    if (!variantId) return;

    // 🚫 PINCODE NOT CHECKED
    if (!deliveryChecked || checkedVariantId !== variantId) {
      resultEl.innerText = "Please check delivery pincode";
      resultEl.style.color = "red";
      return;
    }

    // 🚫 NOT DELIVERABLE
    if (!deliveryAllowed) {
      resultEl.innerText = "❌ This product is not shipped to this location";
      resultEl.style.color = "red";
      return;
    }

    if (isAdding) return;

    isAdding = true;
    addBtn.disabled = true;
    addBtn.innerText = "ADDING...";

    fetch("/api/cart/add/", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
        ...authHeaders()
      },
      body: JSON.stringify({ variant_id: variantId })
    })
      .then(res => res.json())
      .then(() => {
        lastAddedVariant = variantId;
        addBtn.innerText = "ADDED";
        addBtn.classList.add("added");
        addBtn.disabled = true;
        updateBagCount();
      })
      .finally(() => {
        isAdding = false;
      });
  });

  /* ===============================
     PINCODE CHECK
  =============================== */
  document.getElementById("check-btn")?.addEventListener("click", async () => {
    const pin = document.getElementById("pincode").value.trim();
    const variantId = addBtn.dataset.variant;

    if (!variantId) {
      resultEl.innerText = "Please select a variant";
      resultEl.style.color = "red";
      return;
    }

    if (!/^\d{6}$/.test(pin)) {
      resultEl.innerText = "Please enter a valid 6-digit pincode";
      resultEl.style.color = "red";
      return;
    }

    resultEl.innerText = "Checking delivery...";
    resultEl.style.color = "#555";

    try {
      const res = await fetch("/api/products/check-delivery/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
          variant_id: variantId,
          pincode: pin
        })
      });

      const data = await res.json();

      // ✅ SET STATE CORRECTLY
      deliveryChecked = true;
      checkedVariantId = variantId;

      if (data.deliverable) {
        deliveryAllowed = true;
        resultEl.innerText = `🚚 Delivery available • ETA ${data.eta_days} days`;
        resultEl.style.color = "green";
      } else {
        deliveryAllowed = false;
        resultEl.innerText = "❌ This product is not shipped to this location";
        resultEl.style.color = "red";
      }

    } catch {
      deliveryChecked = false;
      deliveryAllowed = false;
      checkedVariantId = null;
      resultEl.innerText = "Unable to check delivery";
      resultEl.style.color = "red";
    }
  });

});

/* ===============================
   HELPERS
=============================== */
function getCSRFToken() {
  return document.cookie
    .split("; ")
    .find(c => c.startsWith("csrftoken="))
    ?.split("=")[1];
}

function updateBagCount() {
  fetch("/api/cart/", {
    credentials: "include"
  })
    .then(res => res.json())
    .then(data => {
      const el = document.getElementById("global-bag-count");
      let qty = 0;
      data.items?.forEach(i => qty += i.quantity);

      if (qty > 0) {
        el.innerText = qty;
        el.classList.remove("hidden");
      } else {
        el.classList.add("hidden");
      }
    });
}




/* ===============================
   IMAGE ZOOM
=============================== */
const mainImg = document.getElementById("main-img");
const lens = document.getElementById("zoom-lens");
const result = document.getElementById("zoom-result");
const container = document.getElementById("img-container");

if (container && mainImg && lens && result) {

  document.querySelectorAll(".thumb").forEach(thumb => {
    thumb.addEventListener("mouseenter", () => {
      document.querySelectorAll(".thumb").forEach(t => t.classList.remove("active"));
      thumb.classList.add("active");
      mainImg.src = thumb.dataset.img;
      result.style.backgroundImage = `url('${mainImg.src}')`;
    });
  });

  container.addEventListener("mouseenter", () => {
    lens.style.display = "block";
    result.style.display = "block";
  });

  container.addEventListener("mouseleave", () => {
    lens.style.display = "none";
    result.style.display = "none";
  });

  container.addEventListener("mousemove", e => {
    const rect = container.getBoundingClientRect();
    let x = e.clientX - rect.left - lens.offsetWidth / 2;
    let y = e.clientY - rect.top - lens.offsetHeight / 2;

    x = Math.max(0, Math.min(x, container.offsetWidth - lens.offsetWidth));
    y = Math.max(0, Math.min(y, container.offsetHeight - lens.offsetHeight));

    lens.style.left = x + "px";
    lens.style.top = y + "px";

    const cx = result.offsetWidth / lens.offsetWidth;
    const cy = result.offsetHeight / lens.offsetHeight;

    result.style.backgroundSize =
      container.offsetWidth * cx + "px " +
      container.offsetHeight * cy + "px";

    result.style.backgroundPosition = `-${x * cx}px -${y * cy}px`;
  });
}





/* ===============================
   LOAD PRODUCT REVIEWS (PDP)
=============================== */
document.addEventListener("DOMContentLoaded", async () => {
  const ratingRow = document.getElementById("rating-summary");
  const reviewsDiv = document.getElementById("reviews-section");

  if (!ratingRow || !reviewsDiv) return;

  // product_id must be available in template
  const productId = ratingRow.dataset.productId;
  if (!productId) {
    ratingRow.innerText = "No ratings";
    return;
  }

  try {
    const res = await fetch(`/api/products/${productId}/reviews/`);
    const data = await res.json();

    ratingRow.innerHTML = `
      ⭐ <strong>${data.average_rating}</strong> / 5
      <span>(${data.total_reviews} reviews)</span>
    `;

    if (!data.reviews.length) {
      reviewsDiv.innerHTML = "<p>No reviews yet</p>";
      return;
    }

    reviewsDiv.innerHTML = data.reviews.map(r => `
      <div class="review-card">
        <div class="review-user">${r.user}</div>
        <div class="review-rating">⭐ ${r.rating} / 5</div>
        <div class="review-comment">${r.comment || ""}</div>
        <div class="review-date">
          ${new Date(r.created_at).toLocaleDateString()}
        </div>
      </div>
    `).join("");

  } catch (err) {
    ratingRow.innerText = "Unable to load ratings";
  }
});

/* ===============================
   PDP TOP RATING (STARS + COUNT)
=============================== */
document.addEventListener("DOMContentLoaded", async () => {
  const ratingEl = document.getElementById("pdp-rating");
  if (!ratingEl) return;

  const productId = ratingEl.dataset.productId;

  try {
    const res = await fetch(`/api/products/${productId}/reviews/`);
    const data = await res.json();

    const avg = data.average_rating || 0;
    const count = data.total_reviews || 0;

    const full = Math.floor(avg);
    const half = avg % 1 >= 0.5;

    let html = "";

    for (let i = 1; i <= 5; i++) {
      if (i <= full) {
        html += `<span class="star filled">★</span>`;
      } else if (i === full + 1 && half) {
        html += `<span class="star half">★</span>`;
      } else {
        html += `<span class="star">★</span>`;
      }
    }

    html += ` <span>(${count})</span>`;
    ratingEl.innerHTML = html;

  } catch {
    ratingEl.innerHTML = `
      <span class="star">★</span>
      <span class="star">★</span>
      <span class="star">★</span>
      <span class="star">★</span>
      <span class="star">★</span>
      <span>(0)</span>
    `;
  }
});



/* ===============================
   PDP TABS SWITCH
=============================== */
document.addEventListener("DOMContentLoaded", () => {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {

      // reset buttons
      tabButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const target = btn.dataset.tab;

      // reset contents
      tabContents.forEach(c => c.classList.remove("active"));
      document.getElementById(`tab-${target}`)?.classList.add("active");
    });
  });
});