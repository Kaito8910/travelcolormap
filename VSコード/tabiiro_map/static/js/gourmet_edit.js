// static/js/gourmet_edit.js

document.addEventListener("click", async (e) => {
    if (!e.target.classList.contains("delete-photo-btn")) return;

    const photoId = e.target.dataset.photoId;
    if (!confirm("この写真を削除しますか？")) return;

    const res = await fetch(`/food/photo/${photoId}/delete`, {
        method: "POST"
    });

    if (res.ok) {
        location.reload();
    } else {
        alert("削除に失敗しました。");
    }
});
