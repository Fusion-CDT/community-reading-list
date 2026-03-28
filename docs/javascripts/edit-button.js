document.addEventListener("click", async function (event) {
    const link = event.target.closest("a[rel='edit'][data-raw-url]");
    if (!link) return;

    event.preventDefault();

    const rawUrl = link.dataset.rawUrl;
    let href = link.href;

    try {
        const response = await fetch(rawUrl);
        if (response.ok) {
            const text = await response.text();
            // Strip YAML frontmatter block (--- ... ---)
            const body = text.replace(/^---\s*\n[\s\S]*?\n---\s*\n?/, "").trimStart();
            href += "&proposed_content=" + encodeURIComponent(body);
        }
    } catch (_) {
        // Fall back to navigating without proposed_content
    }

    window.location.href = href;
});
