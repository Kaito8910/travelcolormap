document.addEventListener("DOMContentLoaded", async function() {
const svgObject = document.getElementById("japan-map");

svgObject.addEventListener("load", async function() {
    const svgDoc = svgObject.contentDocument;
    const paths = svgDoc.querySelectorAll("path");

    // APIからデータ取得
    const res = await fetch("/api/visit_data");
    const visitData = await res.json();

    // 最大値を取得して色スケールを決める
    const values = Object.values(visitData);
    const maxCount = Math.max(...values);

    function getColor(count) {
      if (count === 0) return "#eee"; // 未訪問
      const intensity = Math.min(255, Math.floor((count / maxCount) * 255));
      // 緑→赤のグラデーション
    return `rgb(${255 - intensity}, ${intensity}, 100)`;
    }

    paths.forEach(path => {
    const pref = path.getAttribute("data-name");
    const count = visitData[pref] || 0;

    path.style.fill = getColor(count);

      // クリックイベント
    path.addEventListener("click", () => {
        document.getElementById("info").innerText = `${pref}：${count}回訪問`;
    });
    });
});
});
