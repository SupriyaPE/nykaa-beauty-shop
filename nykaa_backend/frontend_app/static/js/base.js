document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/cart/")
    .then(res => res.json())
    .then(data => {
      const count = data.items.reduce((t, i) => t + i.quantity, 0);
      const el = document.getElementById("global-bag-count");

      if (!el) return;

      if (count > 0) {
        el.innerText = count;
        el.classList.remove("hidden");
      } else {
        el.classList.add("hidden");
      }
    });
});


function filterBrands(value) {

    value = value.toLowerCase();

    document.querySelectorAll(".brand-name").forEach(el => {
        el.style.display = el.dataset.name.includes(value)
            ? "block"
            : "none";
    });

    document.querySelectorAll(".brand-logo-card").forEach(el => {
        el.style.display = el.dataset.name.includes(value)
            ? "flex"
            : "none";
    });
}