"""
Store images from an issue in the repository, next to the note that uses them.

Images reach a note in two ways:

1. **Uploaded** through an issue form's upload field. The contributor refers to
   them by filename in their Markdown, e.g. `![Diagram](diagram.png)`.
2. **Pasted** into a text box. GitHub inserts a link to its own copy, either as
   HTML or as Markdown:

       <img width="709" height="561" alt="Plot" src="https://github.com/user-attachments/assets/d31a6968-...">
       ![Plot](https://github.com/user-attachments/assets/d31a6968-...)

Either way, the image is hosted by GitHub, outside the repository. This script
downloads each image next to the note, named `<note>-<name>` so notes in the
same folder can't overwrite each other's images, and rewrites the note's
Markdown to use the local copy. Pasted `<img>` tags are converted to Markdown
image syntax first, because relative paths in raw HTML don't work on the built
site.

Usage (in a workflow step):

    uv run --locked --only-group scripts scripts/localise_images.py <note.md> <uploads JSON>

where the uploads JSON is the `user_images` output of `issue_to_note.py` or
`apply_edit.py`, e.g. `[{"name": "diagram.png", "url": "https://..."}]`.
"""

import json
import re
import sys
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path

# Only download images hosted by GitHub for issues
ALLOWED_PREFIX = "https://github.com/user-attachments/assets/"

# A GitHub attachment link, e.g. https://github.com/user-attachments/assets/d31a6968-c638-...
ATTACHMENT_URL = re.compile(re.escape(ALLOWED_PREFIX) + r"[\w-]+")

# An HTML image tag, e.g. <img width="709" alt="Plot" src="https://..." />
IMG_TAG = re.compile(r"<img\s[^>]*>")

# GitHub's limit for images in issue forms
MAX_BYTES = 10 * 1024 * 1024

# The image types we store, and the extension each is saved with
EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
    "image/webp": ".webp",
}


def download(url: str) -> tuple[bytes, str]:
    """Return an image's contents and its type, e.g. (b"...", "image/png")."""
    # GitHub turns away requests that don't say what they are
    request = urllib.request.Request(url, headers={"User-Agent": "community-reading-list"})
    with urllib.request.urlopen(request, timeout=30) as response:
        content_type = response.headers.get_content_type()
        data = response.read(MAX_BYTES + 1)  # one byte more, to spot an oversized image
    if len(data) > MAX_BYTES:
        raise ValueError("image is larger than 10 MB")
    return data, content_type


def safe_name(name: str) -> str:
    """Make a filename that works in a Markdown link, e.g. "My plot (1).png" -> "My-plot-1.png"."""
    name = "-".join(Path(name).name.split())  # spaces become hyphens
    return "".join(c for c in name if c.isascii() and (c.isalnum() or c in "._-"))


def unique_path(directory: Path, stem: str, suffix: str) -> Path:
    """Return a path for a new file, e.g. plot.png, or plot-2.png if that exists."""
    path, n = directory / f"{stem}{suffix}", 2
    while path.exists():
        path = directory / f"{stem}-{n}{suffix}"
        n += 1
    return path


def attribute(tag: str, name: str) -> str:
    """Return an HTML attribute's value, e.g. attribute('<img alt="Plot">', "alt") -> "Plot"."""
    start = tag.find(f' {name}="')
    if start == -1:
        return ""
    start += len(name) + 3  # skip past ` name="`
    return tag[start : tag.index('"', start)]


def img_to_markdown(match: re.Match[str]) -> str:
    """Turn a pasted <img> tag into Markdown, e.g. ![Plot](https://...), keeping its link."""
    tag = match[0]
    src = attribute(tag, "src")
    if not src.startswith(ALLOWED_PREFIX):
        return tag  # not pasted into the issue, so leave it alone
    return f"![{attribute(tag, 'alt')}]({src})"


def localise(
    note_path: Path,
    uploads: list[dict[str, str]],
    fetch: Callable[[str], tuple[bytes, str]] = download,  # tests pass a fake
) -> list[Path]:
    """Download the note's images next to it and rewrite its links.

    Returns the image files written. An image that can't be stored keeps its
    link to GitHub's copy, with a warning on the workflow run's summary page.
    """
    directory = note_path.parent
    prefix = safe_name(note_path.stem)
    _, frontmatter, body = note_path.read_text(encoding="utf-8").split("---", 2)
    # Turn pasted <img> tags into Markdown, e.g. ![Plot](https://...), so the
    # rest of this function only has to deal with one kind of image link
    body = IMG_TAG.sub(img_to_markdown, body)

    written: list[Path] = []
    stored: dict[str, str] = {}  # attachment URL -> local filename

    # Download each image once: uploads first, named after the uploaded file,
    # then pasted images, which have no name of their own
    images = [(u["url"], u["name"]) for u in uploads]
    images += [(url, "image") for url in ATTACHMENT_URL.findall(body)]
    for url, name in images:
        if url in stored:
            continue
        if not url.startswith(ALLOWED_PREFIX):
            print(f"::warning::Not downloading {url}: only GitHub attachment links are stored.")
            continue
        try:
            data, content_type = fetch(url)
        except Exception as error:  # keep the link rather than fail the PR
            print(f"::warning::Couldn't download {url} ({error}); leaving the link as it is.")
            continue
        if content_type not in EXTENSIONS:
            print(f"::warning::Not storing {url}: it's {content_type}, not an image.")
            continue
        # e.g. howes2006astro-gyrokinetics-angular-velocity.png
        stem = f"{prefix}-{safe_name(Path(name).stem)}"
        path = unique_path(directory, stem, EXTENSIONS[content_type])
        with open(path, "wb") as f:
            f.write(data)
        written.append(path)
        stored[url] = path.name

    # Uploads: the contributor refers to each one by its original name, e.g.
    # ![Diagram](my diagram.png). Point those references at the stored file.
    for upload in uploads:
        if upload["url"] not in stored:
            continue  # it couldn't be stored, and a warning was printed above
        original, filename = upload["name"], stored[upload["url"]]

        # A name with spaces may be written as it is, URL-encoded, or in <...>
        # (Markdown's way of allowing spaces in a link). urllib.parse.quote
        # URL-encodes it: spaces become %20, and other characters that can't
        # appear in a link get the same treatment, e.g. "(" becomes %28.
        references = [
            f"]({original})",
            f"]({urllib.parse.quote(original)})",
            f"](<{original}>)",
        ]
        # Uploaded, but not used in the note (e.g. a typo in the name). The file
        # is still stored, so tell the reviewer how to add it.
        if not any(reference in body for reference in references):
            print(
                f"::warning::'{original}' was uploaded but isn't used. "
                f"Add it to the note with ![Description]({filename})."
            )
        for reference in references:
            body = body.replace(reference, f"]({filename})")

    # Pasted images: swap each stored attachment link for the local filename.
    # The `](` and `)` make sure one link can't match inside a longer one.
    for url, filename in stored.items():
        body = body.replace(f"]({url})", f"]({filename})")

    with open(note_path, "w", encoding="utf-8") as f:
        f.write(f"---{frontmatter}---{body}")
    return written


def main() -> None:
    note_path = Path(sys.argv[1])
    uploads = json.loads(sys.argv[2])
    for path in localise(note_path, uploads):
        print(f"Stored {path}")


if __name__ == "__main__":
    main()
