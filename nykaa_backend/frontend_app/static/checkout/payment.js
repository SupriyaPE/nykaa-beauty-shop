document.addEventListener("DOMContentLoaded", () => {
  const orderId = localStorage.getItem("current_order_id");
  if (!orderId) return;

  fetch(`/api/orders/order-summary/${orderId}/`, {
    credentials: "include",
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) return;

      // Right-side bag
      document.getElementById("item-count").innerText = data.items_count;
      document.getElementById("total-mrp").innerText = `₹${data.total_mrp}`;
      document.getElementById("you-save").innerText = `₹${data.savings}`;
      document.querySelectorAll("#grand-total").forEach(el => {
        el.innerText = data.total_pay;
      });

      // Pay button amount
      const payBtn = document.getElementById("pay-btn");
      if (payBtn) {
        payBtn.innerHTML = `Scan & Pay ₹<span>${data.total_pay}</span>`;
      }
    })
    .catch(() => {
      console.error("Failed to load order summary");
    });
});