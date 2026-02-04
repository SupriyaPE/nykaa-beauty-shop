let selectedRating = 0;
let activeOrderId = null;
let activeVariantId = null;

// ===============================
// LOAD ORDERS
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("ordersContainer");
  const token = localStorage.getItem("access_token");

  if (!token) {
    container.innerHTML = "<p>Please login to view orders</p>";
    return;
  }

  fetch("/api/orders/my-orders/", {
    headers: {
      "Authorization": "Bearer " + token
    }
  })
    .then(res => {
      if (!res.ok) throw new Error();
      return res.json();
    })
    .then(data => {
      if (!data.length) {
        document.getElementById("emptyState").classList.remove("hidden");
        return;
      }

      container.innerHTML = "";

      data.forEach(order => {
        let itemsHtml = "";

        order.items.forEach(item => {
          if (order.order_status === "DELIVERED") {
            if (item.reviewed) {
              const stars =
                "★".repeat(item.rating) +
                "☆".repeat(5 - item.rating);

              itemsHtml += `
                <div class="order-item">
                  <div>
                    ${item.product_name} (${item.variant_name})
                    <div class="rating-stars">${stars}</div>
                  </div>
                  <span class="reviewed">Reviewed</span>
                </div>
              `;
            } else {
              itemsHtml += `
                <div class="order-item">
                  ${item.product_name} (${item.variant_name})
                  <button class="review-btn"
                    onclick="openReviewModal(${order.id}, ${item.variant_id})">
                    Write Review
                  </button>
                </div>
              `;
            }
          } else {
            itemsHtml += `
              <div class="order-item">
                ${item.product_name} (${item.variant_name})
              </div>
            `;
          }
        });

        container.innerHTML += `
          <div class="order-card">
            <div class="order-meta">
              <div><strong>Order ID:</strong> ${order.id}</div>
              <div><strong>Total:</strong> ₹${order.total_amount}</div>
              <div><strong>Status:</strong> ${order.order_status}</div>
              <div><strong>Payment:</strong> ${order.payment_status}</div>
              ${order.order_status === "DELIVERED"
                ? `<div class="delivered-label">
                    ✅ Delivered on ${new Date(order.created_at).toLocaleDateString()}
                  </div>`
                : `<div>
                    🚚 Expected delivery: ${order.expected_delivery_days} days
                  </div>`
              }
            </div>

            <div class="order-date">
              ${new Date(order.created_at).toLocaleString()}
            </div>

            <div class="order-items">
              ${itemsHtml}
            </div>
          </div>
        `;
      });
    })
    .catch(() => {
      container.innerHTML = "<p>Error loading orders</p>";
    });
});

// ===============================
// OPEN REVIEW MODAL
// ===============================
function openReviewModal(orderId, variantId) {
  activeOrderId = orderId;
  activeVariantId = variantId;
  selectedRating = 0;

  document.getElementById("reviewComment").value = "";
  resetStars();

  document.getElementById("reviewModal").classList.remove("hidden");
}

// ===============================
// CLOSE MODAL
// ===============================
function closeReview() {
  document.getElementById("reviewModal").classList.add("hidden");
}

// ===============================
// STAR SELECTION
// ===============================
function selectStar(rating) {
  selectedRating = rating;
  const stars = document.querySelectorAll(".stars span");

  stars.forEach((star, index) => {
    star.classList.toggle("active", index < rating);
  });
}

function resetStars() {
  document.querySelectorAll(".stars span").forEach(star => {
    star.classList.remove("active");
  });
}

// ===============================
// SUBMIT REVIEW
// ===============================
function submitReview() {
  if (!selectedRating) {
    showReviewError("Please select a rating");
    return;
  }

  const comment = document.getElementById("reviewComment").value;
  const submitBtn = document.getElementById("submitReviewBtn");

  submitBtn.innerText = "Submitting...";
  submitBtn.disabled = true;

  fetch("/api/products/reviews/submit/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + localStorage.getItem("access_token")
    },
    body: JSON.stringify({
      order_id: activeOrderId,
      variant_id: activeVariantId,
      rating: selectedRating,
      comment: comment
    })
  })
    .then(res => {
      if (!res.ok) throw new Error();
      return res.json();
    })
    .then(() => {
      closeReview();          // ✅ close modal
      location.reload();      // ✅ show Reviewed ✅
    })
    .catch(() => {
      showReviewError("Failed to submit review");
      submitBtn.innerText = "Submit Review";
      submitBtn.disabled = false;
    });
}

function showReviewError(msg) {
  const errorEl = document.getElementById("reviewError");
  errorEl.innerText = msg;
  errorEl.classList.remove("hidden");
}