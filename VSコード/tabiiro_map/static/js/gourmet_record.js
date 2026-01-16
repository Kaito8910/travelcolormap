document.addEventListener("DOMContentLoaded", () => {
    const stars = document.querySelectorAll(".star-rating span");
    const evaluationInput = document.getElementById("evaluation");

    let currentValue = parseInt(evaluationInput.value);

    highlightStars(currentValue);

    stars.forEach(star => {
        star.addEventListener("mouseenter", () => {
            const val = parseInt(star.dataset.value);
            highlightStars(val);
        });

        star.addEventListener("click", () => {
            currentValue = parseInt(star.dataset.value);
            evaluationInput.value = currentValue;
            highlightStars(currentValue);
        });
    });

    document.querySelector(".star-rating").addEventListener("mouseleave", () => {
        highlightStars(currentValue);
    });

    function highlightStars(val) {
        stars.forEach(s => {
            const starVal = parseInt(s.dataset.value);
            if (starVal <= val) {
                s.classList.add("selected");
            } else {
                s.classList.remove("selected");
            }
        });
    }
});
