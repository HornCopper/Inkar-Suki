document.addEventListener("DOMContentLoaded", function () {
    const progressBars = document.querySelectorAll(".progress-bar .progress");
    progressBars.forEach(function (bar) {
        const width = parseFloat(bar.style.width);
        let color = "#5ebfd7";

        if (width >= 75) {
            color = "#ff2929";
        } else if (width >= 50) {
            color = "#ff8929";
        } else if (width >= 25) {
            color = "#ece44a";
        } else {
            color = "#4caf50";
        }
        bar.style.backgroundColor = color;
    });
});