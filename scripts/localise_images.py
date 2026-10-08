"""
Store images from an issue in the repository, next to the note that uses them.

Images reach a note in two ways:

1. **Uploaded** through an issue form's upload field. The contributor refers to
   them by filename in their Markdown, e.g. `![Diagram](diagram.png)`.
2. **Pasted** into a text box. GitHub inserts a link to its copy, either as
   `<img ... src="https://github.com/user-attachments/assets/...">` or as
   `![...](https://github.com/user-attachments/assets/...)`.

Either way the image is hosted by GitHub, outside the repository. This script
downloads each image next to the note, named `<note>-<name>` so notes in the
same folder can't overwrite each other's images, and rewrites the note's
Markdown to use the local copy. Pasted `<img>` tags are converted to Markdown
image syntax, because relative paths in raw HTML don't work on the built site.

Usage:

    python3 scripts/localise_images.py <note.md> [uploads JSON]

where the uploads JSON is the `parsed_<upload field id>` output of
`parse_issue.py`. If the GITHUB_TOKEN variable is set it's sent to GitHub
(never to the storage server it redirects to), which is only needed for
images from private repositories.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Only download images hosted by GitHub for issues
ALLOWED_PREFIX = "https://github.com/user-attachments/assets/"

# GitHub's limit for images in issue forms
MAX_BYTES = 10 * 1024 * 1024

EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
    "image/webp": ".webp",
}

PASTED_HTML = re.compile(
    r"<img\b[^>]*?\bsrc=[\"'](?P<url>" + re.escape(ALLOWED_PREFIX) + r"[^\"']+)[\"'][^>]*>",
    re.IGNORECASE,
)
PASTED_MARKDOWN = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\((?P<url>" + re.escape(ALLOWED_PREFIX) + r"[^)\s]+)\)"
)
ALT_ATTRIBUTE = re.compile(r"\balt=[\"'](?P<alt>[^\"']*)[\"']", re.IGNORECASE)


def warn(message):
    """Print a warning that GitHub Actions shows in the run summary."""
    print(f"::warning::{message}")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def download(url, token=None):
    """Return (bytes, content type) for an image URL.

    GitHub redirects attachment URLs to a temporary storage link. The token,
    if any, is only sent to GitHub, so the redirect is followed by hand.
    """
    request = urllib.request.Request(url, headers={"User-Agent": "community-reading-list"})
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        response = opener.open(request, timeout=30)
    except urllib.error.HTTPError as error:
        if error.code not in (301, 302, 303, 307, 308):
            raise
        location = error.headers["Location"]
        response = urllib.request.urlopen(
            urllib.request.Request(location, headers={"User-Agent": "community-reading-list"}),
            timeout=30,
        )
    with response:
        content_type = response.headers.get_content_type()
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("image is larger than 10 MB")
    return data, content_type


def safe_name(name):
    """Make a filename that works in a Markdown link: no spaces or slashes."""
    name = Path(name).name
    name = re.sub(r"\s+", "-", name.strip())
    return re.sub(r"[^A-Za-z0-9._-]", "", name)


def unique_path(directory, name, taken):
    """Return a path in `directory` for `name` that isn't already used."""
    stem, suffix = Path(name).stem, Path(name).suffix
    candidate, n = name, 2
    while candidate in taken or (directory / candidate).exists():
        candidate = f"{stem}-{n}{suffix}"
        n += 1
    taken.add(candidate)
    return directory / candidate


FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def split_frontmatter(text):
    """Return (frontmatter, body) so only the body is rewritten."""
    match = FRONTMATTER.match(text)
    return (match[0], text[match.end() :]) if match else ("", text)


def localise(note_path, uploads=(), fetch=download):
    """Download the note's images next to it and rewrite its links.

    Returns the list of image files written.
    """
    note_path = Path(note_path)
    directory = note_path.parent
    prefix = safe_name(note_path.stem)
    frontmatter, body = split_frontmatter(note_path.read_text(encoding="utf-8"))
    taken, written, saved = set(), [], {}

    def save(url, name_hint):
        """Download `url` once and return the saved filename, or None."""
        if url in saved:
            return saved[url]
        if not url.startswith(ALLOWED_PREFIX):
            warn(f"Not downloading {url}: only GitHub attachment links are stored.")
            saved[url] = None
            return None
        try:
            data, content_type = fetch(url)
        except Exception as error:  # keep the link rather than fail the PR
            warn(f"Couldn't download {url} ({error}); leaving the link as it is.")
            saved[url] = None
            return None
        extension = EXTENSIONS.get(content_type)
        if extension is None:
            warn(f"Not storing {url}: it's {content_type}, not an image.")
            saved[url] = None
            return None
        name = f"{prefix}-{safe_name(Path(name_hint).stem)}{extension}"
        path = unique_path(directory, name, taken)
        path.write_bytes(data)
        written.append(path)
        saved[url] = path.name
        return path.name

    # 1. Uploaded files: save each, then point references to its new name
    for upload in uploads:
        original = upload["name"]
        filename = save(upload["url"], original)
        if filename is None:
            continue
        variants = {original, urllib.parse.quote(original), f"<{original}>"}
        pattern = re.compile(
            r"(!\[[^\]]*\]\()(" + "|".join(re.escape(v) for v in variants) + r")(\))"
        )
        body, count = pattern.subn(lambda m: m[1] + filename + m[3], body)
        if count == 0:
            warn(
                f"'{original}' was uploaded but isn't used. Add it to the note with "
                f"![Description]({filename})."
            )

    # 2. Images pasted into the text: convert <img> tags, then Markdown links
    def replace_html(match):
        alt = ALT_ATTRIBUTE.search(match[0])
        alt = alt["alt"] if alt else ""
        filename = save(match["url"], "image")
        return f"![{alt}]({filename})" if filename else match[0]

    def replace_markdown(match):
        filename = save(match["url"], "image")
        return f"![{match['alt']}]({filename})" if filename else match[0]

    body = PASTED_HTML.sub(replace_html, body)
    body = PASTED_MARKDOWN.sub(replace_markdown, body)

    note_path.write_text(frontmatter + body, encoding="utf-8")
    for path in written:
        print(f"Stored {path}")
    return written


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__)
        return 2
    uploads = json.loads(argv[2]) if len(argv) == 3 and argv[2].strip() else []
    token = os.environ.get("GITHUB_TOKEN") or None
    localise(argv[1], uploads, fetch=lambda url: download(url, token))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
