document.addEventListener("DOMContentLoaded", async () => {

    // ① SVGファイルを取得して inline 化
    const res = await fetch("/static/svg/map-full.svg");
    const svgText = await res.text();
    const container = document.getElementById("japan-map-container");
    container.innerHTML = svgText;

    console.log("SVG INSERTED!");

    // ★ ここで SVG 要素を取得してサイズを強制フィット（巨大化バグを防ぐ）
    const svg = container.querySelector("svg");
    if (svg) {
        svg.setAttribute("id", "japan-map");
        svg.style.width = "90%";
        svg.style.height = "auto";
        svg.style.maxHeight = "90%";    // 黒枠内に収まる
        svg.style.objectFit = "contain";
        svg.style.display = "block";    // 余白防止
    }

    const svgDoc = container;

    // ② 都道府県ごとの訪問回数を API から取得
    const prefRes = await fetch("/api/pref_counts");
    const prefData = await prefRes.json();
    console.log("PREF DATA:", prefData);

    // ③ 色スケール
    function getColor(count) {
        if (count === 0) return "#EEEEEE";
        if (count === 1) return "#A8DADC";
        if (count === 2) return "#74B3C6";
        if (count === 3) return "#457B9D";
        return "#1D3557"; // 4以上
    }

    // ④ SVG 内の都道府県要素取得
    const prefectures = svgDoc.querySelectorAll("g.prefecture");
    console.log("FOUND PREF:", prefectures.length);

    prefectures.forEach(pref => {
        const titleTag = pref.querySelector("title");
        if (!titleTag) return;

        const fullTitle = titleTag.textContent.trim(); // "北海道 / Hokkaido"
        const prefName = fullTitle.split("/")[0].trim(); // "北海道"

        const count = prefData[prefName] || 0;

        // 色を反映
        pref.querySelectorAll("polygon, path").forEach(elem => {
            elem.style.fill = getColor(count);
        });

        // クリックで詳細表示
        pref.addEventListener("click", () => {
            alert(`${prefName}：${count}回訪問`);
        });
    });
});
