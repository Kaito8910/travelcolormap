// ============================
// 日本地図 色塗り + クリック処理
// ============================

document.addEventListener("DOMContentLoaded", () => {

    function getColor(count) {
        if (count === 0) return "#EEEEEE";
        if (count === 1) return "#A8DADC";
        if (count === 2) return "#74B3C6";
        if (count === 3) return "#457B9D";
        return "#1D3557";
    }

    const totalCount = {};

    const mapObj = document.getElementById("japan-map");

    if (!mapObj) {
        console.error("SVG map object が見つかりません");
        return;
    }

    mapObj.addEventListener("load", async () => {
        const svgDoc = mapObj.contentDocument;

        // API から訪問回数を取得
        let prefVisited = {};
        try {
            const response = await fetch("/api/pref_counts");
            prefVisited = await response.json();
        } catch (e) {
            console.error("API /api/pref_counts の取得に失敗", e);
        }

        // 初期値を投入
        Object.keys(prefVisited).forEach(pref => {
            totalCount[pref] = prefVisited[pref];
        });

        const clickCount = {};

        const prefectures = svgDoc.querySelectorAll("g.prefecture");

        prefectures.forEach(pref => {
            const titleTag = pref.querySelector("title");
            if (!titleTag) return;

            const fullTitle = titleTag.textContent.trim();
            const prefName = fullTitle.split("/")[0].trim();

            if (!(prefName in totalCount)) totalCount[prefName] = 0;
            clickCount[prefName] = 0;

            // 初期色
            const initial = totalCount[prefName];
            pref.querySelectorAll("polygon, path").forEach(elem => {
                elem.style.fill = getColor(initial);
            });

            // クリック時の色変化
            pref.addEventListener("click", () => {
                clickCount[prefName] += 1;
                const sum = totalCount[prefName] + clickCount[prefName];

                pref.querySelectorAll("polygon, path").forEach(elem => {
                    elem.style.fill = getColor(sum);
                });

                console.log(
                    `${prefName}: 初期=${initial} / クリック=${clickCount[prefName]} / 合計=${sum}`
                );
            });
        });
    });
});
