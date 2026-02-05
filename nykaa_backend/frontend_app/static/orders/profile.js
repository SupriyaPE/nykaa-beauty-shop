document.addEventListener("DOMContentLoaded", async () => {

    const token = localStorage.getItem("access_token");
    if (!token) return;

    const nameEl = document.getElementById("profileName");
    const emailEl = document.getElementById("profileEmail");
    const mobileEl = document.getElementById("profileMobile");
    const editBtn = document.querySelector(".edit-btn");
    const logoutBtn = document.getElementById("profile-logout-btn");

    let editMode = false;

    /* =============================
       LOAD PROFILE
    ============================= */
    async function loadProfile() {

        const res = await fetch("/api/auth/profile/", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) return;

        const data = await res.json();

        nameEl.innerText = data.full_name || "—";
        emailEl.innerText = data.email || "—";
        mobileEl.innerText = data.mobile || "—";
    }

    await loadProfile();


    /* =============================
       EDIT NAME
    ============================= */
    editBtn?.addEventListener("click", async () => {

        if (!editMode) {

            editMode = true;

            const currentName = nameEl.innerText;

            nameEl.innerHTML =
                `<input type="text" id="nameEditInput" value="${currentName}" />`;

            editBtn.innerText = "Save";
            return;
        }

        const newName = document.getElementById("nameEditInput").value.trim();

        if (!newName) {
            alert("Name required");
            return;
        }

        const res = await fetch("/api/auth/profile/", {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                full_name: newName
            })
        });

        if (!res.ok) {
            alert("Update failed");
            return;
        }

        editMode = false;
        editBtn.innerText = "Edit";

        await loadProfile();
    });


    /* =============================
       LOGOUT
    ============================= */
    logoutBtn?.addEventListener("click", async (e) => {

        e.preventDefault();

        try {
            await fetch("/api/auth/logout/", {
                method: "POST"
            });
        } catch (err) {
            console.log("Logout API failed");
        }

        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");

        if (typeof updateHeaderUser === "function") {
            updateHeaderUser();
        }

        window.location.href = "/";
    });

});