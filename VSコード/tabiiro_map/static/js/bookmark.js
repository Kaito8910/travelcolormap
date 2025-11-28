// ================================
//  ⭐ ブックマーク共通 JS
//  add/remove & toggle ☆ ⇄ ★
// ================================

document.addEventListener("click", async (e) => {
    const btn = e.target.closest(".bookmark-btn");
    if (!btn) return;

    const type = btn.dataset.type;
    const id = btn.dataset.id;
    const title = btn.dataset.title;
    const thumb = btn.dataset.thumb || "";

    // ★ なら削除
    if (btn.classList.contains("active")) {
        const fd = new FormData();
        fd.append("type", type);
        fd.append("id", id);

        const res = await fetch("/bookmark/remove", {
            method: "POST",
            body: fd
        });
        const json = await res.json();

        if (json.ok) {
            btn.classList.remove("active");
            btn.innerHTML = "☆ ブックマーク";
        }
        return;
    }

    // ☆ なら追加
    const fd = new FormData();
    fd.append("type", type);
    fd.append("id", id);
    fd.append("title", title);
    fd.append("thumb", thumb);

    const res = await fetch("/bookmark/add", {
        method: "POST",
        body: fd
    });
    const json = await res.json();

    if (json.ok) {
        btn.classList.add("active");
        btn.innerHTML = "★ 登録済み";
    }
});
