// GitHub rejects issue URLs longer than about 8,000 characters (HTTP 414),
// so very long pages open the form without their content pre-filled.
const MAX_URL_LENGTH = 6000;

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
            const prefilled = href + "&proposed_content=" + encodeURIComponent(body);
            if (prefilled.length <= MAX_URL_LENGTH) {
                href = prefilled;
            }
        }
    } catch (_) {
        // Fall back to navigating without proposed_content
    }

    window.location.href = href;
});
