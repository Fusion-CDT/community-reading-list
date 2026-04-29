"""
Title Reference — a Python Markdown preprocessor extension.

Reads `title`, `authors`, `isbn`, and `url` fields from a Markdown page's YAML
front matter and inserts a formatted reference header at build time without
modifying source (Markdown) files.

This extension handles pages that have a `title` field but no `doi` — i.e.
lecture notes, slides, and textbooks. Pages with a `doi` field are handled
by `doi_reference.py` instead; this extension skips them.

Follows the same stack-inspection pattern as `doi_reference.py` and
`contributors.py` to read frontmatter from Zensical's `render()` frame.
"""

import inspect
from itertools import zip_longest

from markdown import Extension
from markdown.preprocessors import Preprocessor


class TitleReferencePreprocessor(Preprocessor):
    """Inject a formatted reference header for pages with a frontmatter title but no doi."""

    def _meta_from_render_frame(self):
        """Read frontmatter meta dict from Zensical's `render()` frame."""
        for frame_info in inspect.stack():
            func = frame_info.function
            name = frame_info.frame.f_globals.get("__name__")
            if (func == "render") and (name == "zensical.markdown"):
                return frame_info.frame.f_locals.get("meta", {})
        return {}

    def run(self, lines):
        meta = self._meta_from_render_frame()

        # Defer to doi_reference.py for pages that have a DOI
        if meta.get("doi"):
            return lines

        title = meta.get("title")
        if not title:
            return lines

        authors = meta.get("authors")
        isbn = meta.get("isbn")
        url = meta.get("url")
        url_name = meta.get("url_name")

        header = [f"# {title}"]

        if authors:
            header.append(f"<p class='ref-authors'>{authors}</p>")

        if isbn:
            header.append(f"<p class='ref-isbn'><b>ISBN:</b> {isbn}</p>")

        url_frontmatter = []
        if url:
            urls = url if isinstance(url, list) else [url]
            if url_name:
                url_names = url_name if isinstance(url_name, list) else [url_name]
            elif url_name is None:
                url_names = []
            for u, u_name in zip_longest(urls, url_names):
                name = u_name if u_name is not None else u
                url_frontmatter.append(f"<a href='{u}'>{name}</a>")

        header.append(
            f"<p class='ref-url'><b>URL(s):</b> {', '.join(url_frontmatter)}</p>"
        )
        header += ["", "---", ""]

        return header + lines


class TitleReferenceExtension(Extension):
    """Python Markdown extension that wires up the title reference preprocessor.

    Registered in `zensical.toml` under `[project.markdown_extensions.title_reference]`.
    A priority of 30 matches `doi_reference`, which is safe since the two
    preprocessors are mutually exclusive (one checks for `doi`, the other for its
    absence).
    """

    def extendMarkdown(self, md):
        md.preprocessors.register(TitleReferencePreprocessor(md), "title_reference", 30)


def makeExtension(**kwargs):
    """Entry point called by Python Markdown when loading the extension by name."""
    return TitleReferenceExtension(**kwargs)
