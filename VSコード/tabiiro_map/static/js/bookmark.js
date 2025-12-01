document.addEventListener("click", async (e) => {

    // ===== ブックマーク一覧の削除ボタンは JS 無視 =====
    if (e.target.classList.contains("bookmark-delete-btn")) {
        return;  // フォーム送信に任せる
    }

    // ===== ここから下は宿泊検索などのブックマーク用 =====
    if (!e.target.classList.contains("bookmark-btn")) return;

    e.stopImmediatePropagation();   // 多重発火防止

    const btn = e.target;
    const type = btn.dataset.type;
    const id = btn.dataset.id;
    const title = btn.dataset.title;
    const thumb = btn.dataset.thumb;

    const currentText = btn.textContent.trim();

    // 追加（☆）
    if (currentText === "☆ ブックマーク") {
        let res = await fetch("/bookmark/add", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `type=${encodeURIComponent(type)}&id=${encodeURIComponent(id)}&title=${encodeURIComponent(title)}&thumb=${encodeURIComponent(thumb)}`
        });
        let data = await res.json();
        if (data.ok) btn.textContent = "★ 登録済み";
    }

    // 削除（★）
    else if (currentText === "★ 登録済み") {
        let res = await fetch("/bookmark/remove", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `type=${encodeURIComponent(type)}&id=${encodeURIComponent(id)}`
        });
        let data = await res.json();
        if (data.ok) btn.textContent = "☆ ブックマーク";
    }
});
