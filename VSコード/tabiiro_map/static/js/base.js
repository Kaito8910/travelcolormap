document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('menu-sidebar');
    const toggleButton = document.getElementById('menu-toggle-button');
    const currentPage = sidebar.dataset.currentPage;

    function updateSidebarState() {
        const isMobile = window.innerWidth < 900;

        if (isMobile) {
            // 📱 スマホは常に閉じる
            sidebar.classList.add('is-closed');
        } else {
            // 💻 PCなら home のときだけ開く
            if (currentPage === "home") {
                sidebar.classList.remove('is-closed');
            } else {
                sidebar.classList.add('is-closed');
            }
        }
    }

    updateSidebarState();

    window.addEventListener('resize', updateSidebarState);

    toggleButton.addEventListener('click', () => {
        sidebar.classList.toggle('is-closed');
    });
});
