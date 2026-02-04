document.addEventListener("DOMContentLoaded", loadWishlist);

// ==============================
// LOAD WISHLIST
// ==============================
async function loadWishlist() {
    const token = localStorage.getItem("access_token");

    const res = await fetch("/api/wishlist/", {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const data = await res.json();

    const grid = document.getElementById("wishlistGrid");
    const empty = document.getElementById("wishlistEmpty");
    const count = document.getElementById("wishlistCount");

    grid.innerHTML = "";

    if (!data.length) {
        empty.classList.remove("hidden");
        count.innerText = 0;
        return;
    }

    empty.classList.add("hidden");
    count.innerText = data.length;

    data.forEach(item => {
        grid.innerHTML += `
            <div class="wishlist-card">
                <span class="remove-btn"
                    onclick="removeWishlist(${item.variant_id})">×</span>

                <img src="${item.image}" alt="${item.product_name}">

                <p class="product-name">${item.product_name}</p>

                <div class="product-price">
                    ₹${item.price}
                    <span class="mrp">₹${item.mrp}</span>
                </div>

                <div class="wishlist-actions">
                    <button class="btn-outline"
                        onclick="viewProduct('${item.slug}')">
                        VIEW PRODUCT
                    </button>

                    <button class="btn-pink"
                        onclick="moveToBag(${item.variant_id}, this)">
                        MOVE TO BAG
                    </button>
                </div>
            </div>
        `;
    });
}

// ==============================
// MOVE TO BAG (NYKAA STYLE)
// ==============================
async function moveToBag(variantId, btn) {
    if (btn.disabled) return;

    btn.innerText = "ADDING...";
    btn.disabled = true;

    const res = await fetch("/api/cart/add/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ variant_id: variantId })
    });

    if (!res.ok) {
        btn.innerText = "MOVE TO BAG";
        btn.disabled = false;
        alert("Unable to add to bag");
        return;
    }

    // remove from wishlist backend
    const token = localStorage.getItem("access_token");
    await fetch("/api/wishlist/toggle/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ variant_id: variantId })
    });

    // remove card from UI
    const card = btn.closest(".wishlist-card");
    card.style.opacity = "0";
    card.style.transform = "scale(0.95)";

    setTimeout(() => {
        card.remove();
        updateWishlistCount();
        checkWishlistEmpty();
    }, 250);
}

// ==============================
// REMOVE FROM WISHLIST
// ==============================
async function removeWishlist(variantId) {
    const token = localStorage.getItem("access_token");

    await fetch("/api/wishlist/toggle/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ variant_id: variantId })
    });

    loadWishlist();
}

// ==============================
// HELPERS
// ==============================
function updateWishlistCount() {
    const grid = document.getElementById("wishlistGrid");
    document.getElementById("wishlistCount").innerText = grid.children.length;
}

function checkWishlistEmpty() {
    const grid = document.getElementById("wishlistGrid");
    const empty = document.getElementById("wishlistEmpty");

    if (!grid.children.length) {
        empty.classList.remove("hidden");
    }
}

// ==============================
// VIEW PRODUCT
// ==============================
function viewProduct(slug) {
    window.location.href = `/product/${slug}/`;
}