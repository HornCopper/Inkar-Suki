window.onload = function () {
    var elements = document.querySelectorAll("#context");
    elements.forEach(function (element) {
        var text = element.innerText;
        var newText = "";
        for (var i = 0; i < text.length; i += 60) {
            newText += text.slice(i, i + 60) + "\n";
        }
        element.innerText = newText;
    });
};  