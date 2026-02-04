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

