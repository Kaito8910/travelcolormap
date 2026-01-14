document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("menu-sidebar");
    const toggleButton = document.getElementById("menu-toggle-button");
    if (!sidebar || !toggleButton) return;

    const currentPage = sidebar.dataset.currentPage;

    // ===============================
    // 表示状態を決める関数
    // ===============================
    function updateSidebarState(forceClose = false) {
        const isMobile = window.innerWidth < 900;

        if (isMobile) {
            // 📱 スマホ：基本は閉じる
            if (forceClose) {
                sidebar.classList.remove("is-open");
                sidebar.classList.add("is-closed");
            }
        } else {
            // 💻 PC：home のときだけ表示
            if (currentPage === "home") {
                sidebar.classList.remove("is-closed");
                sidebar.classList.remove("is-open");
            } else {
                sidebar.classList.add("is-closed");
                sidebar.classList.remove("is-open");
            }
        }
    }

    // 初期状態
    updateSidebarState(true);

    // リサイズ対応
    window.addEventListener("resize", () => {
        updateSidebarState(true);
    });

    // ===============================
    // ハンバーガークリック
    // ===============================
    toggleButton.addEventListener("click", (e) => {
        e.stopPropagation(); // 外側クリックと干渉防止
        const isMobile = window.innerWidth < 900;

        if (isMobile) {
            // 📱 スマホ：スライド開閉
            sidebar.classList.toggle("is-open");
            sidebar.classList.toggle("is-closed");
        } else {
            // 💻 PC：手動トグル（home以外でも一時的に開ける）
            sidebar.classList.toggle("is-closed");
        }
    });

    // ===============================
    // スマホ：外をタップしたら閉じる
    // ===============================
    document.addEventListener("click", (e) => {
        const isMobile = window.innerWidth < 900;
        if (!isMobile) return;
        if (!sidebar.classList.contains("is-open")) return;

        const clickedInsideSidebar = sidebar.contains(e.target);
        const clickedHamburger = toggleButton.contains(e.target);

        if (!clickedInsideSidebar && !clickedHamburger) {
            sidebar.classList.remove("is-open");
            sidebar.classList.add("is-closed");
        }
    });
});
