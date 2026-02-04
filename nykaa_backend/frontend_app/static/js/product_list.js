/* ================================
   PRODUCT LIST – INLINE PREVIEW
================================ */
function authHeaders() {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}


function togglePreview(productId) {
    const panel = document.getElementById('preview-' + productId);
    if (!panel) return;

    panel.classList.toggle('active');
}

function selectVariant(element, productId) {
    const card = document.getElementById('card-' + productId);
    if (!card) return;

    // Remove selection from all chips
    card.querySelectorAll('.chip').forEach(chip => {
        chip.classList.remove('selected');
    });

    // Mark selected
    element.classList.add('selected');

    // Update hidden variant input
    const variantId = element.getAttribute('data-id');
    const hiddenInput = card.querySelector('.hid-variant-id');
    if (hiddenInput) {
        hiddenInput.value = variantId;
    }

    // Update price dynamically
    const price = element.getAttribute('data-price');
    const priceEl = card.querySelector('.sp');
    if (priceEl) {
        priceEl.innerText = "₹" + price;
    }
}

// Auto-select first variant on load
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.pl-card').forEach(card => {
        const firstChip = card.querySelector('.chip');
        const input = card.querySelector('.hid-variant-id');

        if (firstChip && input && !input.value) {
            input.value = firstChip.getAttribute('data-id');
        }
    });
});



function addToBag(btn) {
  if (btn.dataset.loading === "true") return;
  btn.dataset.loading = "true";

  const variantId = btn.dataset.variant;
  const originalText = btn.innerText;

  btn.innerText = "ADDED";
  btn.classList.add("added");

  fetch("/api/cart/add/", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
      ...authHeaders() // 🔥 FIX
    },
    body: JSON.stringify({
      variant_id: variantId,
      quantity: 1
    })
  })
    .then(res => res.json())
    .then(() => {
      if (typeof loadBagData === "function") {
        loadBagData();
      }

      setTimeout(() => {
        btn.innerText = originalText;
        btn.classList.remove("added");
        btn.dataset.loading = "false";
      }, 1200);
    })
    .catch(() => {
      btn.innerText = originalText;
      btn.classList.remove("added");
      btn.dataset.loading = "false";
    });
}


function getCSRFToken() {
  return document.cookie
    .split("; ")
    .find(row => row.startsWith("csrftoken="))
    ?.split("=")[1];
}




document.addEventListener("DOMContentLoaded", markWishlistHearts);

async function markWishlistHearts() {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    const res = await fetch("/api/wishlist/ids/", {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!res.ok) return;

    const ids = await res.json();

    document.querySelectorAll(".wishlist-btn").forEach(btn => {
        if (ids.includes(parseInt(btn.dataset.variant))) {
          btn.classList.add("active");
          btn.innerText = "♥";
      } else {
          btn.classList.remove("active");
          btn.innerText = "♡";
      }
    });
}

async function toggleWishlist(btn) {
    const variantId = btn.dataset.variant;
    const token = localStorage.getItem("access_token");

    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch("/api/wishlist/toggle/", {
        method: "POST",
        headers,
        body: JSON.stringify({ variant_id: variantId })
    });

    if (res.status === 401) {
        alert("Please login to use wishlist");
        return;
    }

    const data = await res.json();

    btn.classList.toggle("active", data.added);
    btn.innerText = data.added ? "♥" : "♡";   // 🔥 THIS LINE
}





document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".rating[data-product-id]").forEach(async el => {
    const productId = el.dataset.productId;

    try {
      const res = await fetch(`/api/products/${productId}/reviews/`);
      const data = await res.json();

      const avg = data.average_rating || 0;
      const count = data.total_reviews || 0;

      el.innerHTML = `
        ⭐ ${avg}
        <span>(${count})</span>
      `;
    } catch {
      el.innerHTML = `⭐ 0.0 <span>(0)</span>`;
    }
  });
});