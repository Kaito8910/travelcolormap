document.addEventListener("DOMContentLoaded", async () => {

    // SVG を inline で読み込み
    const res = await fetch("/static/svg/map-full.svg");
    const svgText = await res.text();

    const container = document.getElementById("japan-map-container");
    container.innerHTML = svgText;

    const svg = container.querySelector("svg");
    if (svg) {
        svg.style.width = "100%";
        svg.style.height = "auto";
        svg.style.display = "block";
    }

    // ① API から都道府県別訪問回数を取得
    const prefRes = await fetch("/api/pref-counts");
    const prefData = await prefRes.json();
    console.log("prefData", prefData); // ← 必ず出るか確認

    // ② 色決定ロジック
    function getColor(count) {
        if (count === 0) return "#EEEEEE";
        if (count === 1) return "#A8DADC";
        if (count === 2) return "#74B3C6";
        if (count === 3) return "#457B9D";
        return "#1D3557";
    }

    // ③ SVG の県を取得
    const prefectures = container.querySelectorAll("g.prefecture");
    console.log("FOUND PREF:", prefectures.length); // ← 47 なら OK

    // ④ 色を反映
    prefectures.forEach(pref => {
        const titleTag = pref.querySelector("title");
        if (!titleTag) return;

        const fullTitle = titleTag.textContent.trim(); 
        const prefName = fullTitle.split("/")[0].trim(); // "北海道"

        const count = prefData[prefName] || 0;

        console.log(prefName, "→", count); // ← 色判定ログ

        pref.querySelectorAll("polygon, path").forEach(elem => {
            elem.style.fill = getColor(count);
        });
    });
});
