// code-links.js — Makes Markdown links clickable in code blocks
document.addEventListener("DOMContentLoaded", function() {
    var codeBlocks = document.querySelectorAll("pre code, code.highlight");
    
    codeBlocks.forEach(function(block) {
        var content = block.innerHTML;
        if (content.includes('class="code-link"')) return;

        // Regex: [TEXT](URL.md) → <a href="URL" class="code-link">TEXT</a>
        content = content.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function(match, text, url) {
                return '<a href="' + url.slice(0, -3) + '" class="code-link">' + text + '</a>';
            }
        );

        block.innerHTML = content;
    });
});
