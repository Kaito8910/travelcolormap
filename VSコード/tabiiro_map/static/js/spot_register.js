document.addEventListener("DOMContentLoaded", () => {
    const photoList = document.getElementById("photo-list");
    const addBtn = document.getElementById("add-photo-btn");
    const tpl = document.getElementById("photo-item-template");

    if (!photoList || !addBtn || !tpl) return;

        function addPhotoItem(autoOpen = true) {
            const node = tpl.content.cloneNode(true);
            const item = node.querySelector(".photo-item");
            const input = node.querySelector(".photo-input");
            const img = node.querySelector(".photo-preview");
            const removeBtn = node.querySelector(".remove-photo-btn");
            const previewWrap = node.querySelector(".photo-preview-wrap");

            previewWrap.style.display = "none";
            img.removeAttribute("src");

            input.addEventListener("change", () => {
                const file = input.files && input.files[0];
            if (!file) return;

                const url = URL.createObjectURL(file);
                img.src = url;
                previewWrap.style.display = "block";

                img.onload = () => URL.revokeObjectURL(url);
            });

            removeBtn.addEventListener("click", () => {
                item.remove();
            });

            photoList.appendChild(item);

            // ★ 追加された瞬間にファイル選択を開く
            if (autoOpen) {
                    input.click();
                }
            }

            addBtn.addEventListener("click", () => addPhotoItem(true));

        // 初期1枠（自動で開きたくない場合）
            //addPhotoItem(false);
    });
