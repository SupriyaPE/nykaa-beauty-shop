const track = document.querySelector(".hero-track");
const items = document.querySelectorAll(".hero-item");

if (track && items.length > 3) {
  let index = 0;
  const visible = 3;
  const total = items.length;

  setInterval(() => {
    index++;

    if (index > total - visible) {
      index = 0;
    }

    const slideWidth = items[0].offsetWidth + 20; // card + gap
    track.style.transform = `translateX(-${index * slideWidth}px)`;
  }, 3500);
}

document.addEventListener("DOMContentLoaded", () => {
  document
    .querySelectorAll(".rating-row[data-product-id]")
    .forEach(async (row) => {
      const productId = row.dataset.productId;

      try {
        const res = await fetch(`/api/products/${productId}/reviews/`);
        const data = await res.json();

        const rating = parseFloat(data.average_rating || 0);
        const count = data.total_reviews || 0;

        // ✅ SAFE ACCESS (🔥 FIX)
        const starsEl = row.querySelector(".stars");
        const countEl = row.querySelector(".rating-count");

        if (starsEl) starsEl.innerHTML = renderStars(rating);
        if (countEl) countEl.innerText = `(${count})`;

      } catch {
        const starsEl = row.querySelector(".stars");
        const countEl = row.querySelector(".rating-count");

        if (starsEl) starsEl.innerHTML = renderStars(0);
        if (countEl) countEl.innerText = "(0)";
      }
    });
});

function renderStars(rating) {
  let html = "";
  for (let i = 1; i <= 5; i++) {
    if (rating >= i) {
      html += `<span class="star filled">★</span>`;
    } else if (rating >= i - 0.5) {
      html += `<span class="star half">★</span>`;
    } else {
      html += `<span class="star">★</span>`;
    }
  }
  return html;
}