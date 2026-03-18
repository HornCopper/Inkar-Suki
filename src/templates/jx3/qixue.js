window.onload = function () {
    var elements = document.querySelectorAll(".short-column");
    elements.forEach(function (element) {
        var childNodes = element.childNodes;
        childNodes.forEach(function (node) {
            if (node.nodeType === Node.TEXT_NODE) {
                var text = node.textContent;
                var lines = [];
                for (var i = 0; i < text.length; i += 25) {
                    lines.push(text.slice(i, i + 25));
                }
                
                var fragment = document.createDocumentFragment();
                lines.forEach(function(line, index) {
                    fragment.appendChild(document.createTextNode(line));
                    if (index < lines.length - 1) {
                        fragment.appendChild(document.createElement('br'));
                    }
                });
                
                node.replaceWith(fragment);
            }
        });
    });
};