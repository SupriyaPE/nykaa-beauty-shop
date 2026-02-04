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
    .forEach(async row => {
      const productId = row.dataset.productId;

      try {
        const res = await fetch(`/api/products/${productId}/reviews/`);
        const data = await res.json();

        const rating = parseFloat(data.average_rating || 0);
        const count = data.total_reviews || 0;

        row.querySelector(".stars").innerHTML = renderStars(rating);
        row.querySelector(".rating-count").innerText = `(${count})`;
      } catch {
        row.querySelector(".stars").innerHTML = renderStars(0);
        row.querySelector(".rating-count").innerText = "(0)";
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