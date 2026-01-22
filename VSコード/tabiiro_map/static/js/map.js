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
    console.log("prefData", prefData);

  // ② 色決定ロジック
    function getColor(count) {
        if (count === 0) return "#EEEEEE";
        if (count === 1) return "#A8DADC";
        if (count === 2) return "#74B3C6";
        if (count === 3) return "#457B9D";
        return "#1D3557";
    }

  // ★ クリック用：短縮名 → フル表記（PREF_LISTが「○○県」前提）
    function toFullPrefName(prefJa) {
        if (prefJa === "北海道") return "北海道";
        if (prefJa === "東京") return "東京都";
        if (prefJa === "大阪") return "大阪府";
        if (prefJa === "京都") return "京都府";
        return `${prefJa}県`;
    }

  // ③ SVG の県を取得
    const prefectures = container.querySelectorAll("g.prefecture");
    console.log("FOUND PREF:", prefectures.length);

  // ④ 色反映 + クリック追加
    prefectures.forEach(pref => {
        const titleTag = pref.querySelector("title");
        if (!titleTag) return;

        const fullTitle = titleTag.textContent.trim();
        const prefName = fullTitle.split("/")[0].trim(); // "埼玉" や "北海道"

        const count = prefData[prefName] || 0;
        console.log(prefName, "→", count);

    // 色を塗る
        pref.querySelectorAll("polygon, path").forEach(elem => {
            elem.style.fill = getColor(count);
        });

    // クリックできるようにする
        pref.style.cursor = "pointer";

    // クリック時の遷移（登録あり→list、なし→search は Flask /spot/pref/<...> が判定）
        const prefFull = toFullPrefName(prefName);
        const go = () => {
            window.location.href = `/spot/pref/${encodeURIComponent(prefFull)}`;
        };

    // g に付ける（効かない環境があるので）
        pref.addEventListener("click", go);

    // polygon/path にも付けて確実にする
        pref.querySelectorAll("polygon, path").forEach(elem => {
            elem.style.cursor = "pointer";
            elem.addEventListener("click", (e) => {
                e.stopPropagation();
                go();
            });
        });
    });
});
