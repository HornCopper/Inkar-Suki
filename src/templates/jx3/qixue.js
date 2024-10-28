window.onload = function () {
    var elements = document.querySelectorAll(".short-column");
    elements.forEach(function (element) {
        var childNodes = element.childNodes;
        childNodes.forEach(function (node) {
            if (node.nodeType === Node.TEXT_NODE) {
                var text = node.textContent;
                var newText = "";
                for (var i = 0; i < text.length; i += 25) {
                    newText += text.slice(i, i + 25) + "<br>";
                }
                var newNode = document.createElement('span');
                newNode.innerHTML = newText;
                node.replaceWith(newNode);
            }
        });
    });
};
