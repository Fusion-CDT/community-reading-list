"""
Contributors — a Python Markdown preprocessor extension.

Reads a `contributors` list from a Markdown page's YAML front matter and
appends a "Contributed by:" line at the bottom of the page at build time,
without modifying source (Markdown) files.

Each contributor entry is expected to have the form:
    {'name': 'Bailey Cook', 'github': 'baiway'}

The `github` field is optional; if absent, the contributor's name is rendered
as plain text rather than a hyperlink.

Zensical strips front matter before passing content to `md.convert()`, so it is
not available in the text the preprocessor receives. However, Zensical has
already parsed it into a `meta` local in its `render()` frame before calling
`md.convert()`. We read that variable directly via `inspect.stack()`, following
the same pattern as `doi_reference.py`.
"""

import inspect
from markdown import Extension
from markdown.preprocessors import Preprocessor


class ContributorsPreprocessor(Preprocessor):
    """Append a formatted 'Contributed by:' line for pages with frontmatter contributors."""

    def _contributors_from_render_frame(self):
        """Read contributors from Zensical's `render()` frame."""
        for frame_info in inspect.stack():
            func = frame_info.function
            name = frame_info.frame.f_globals.get("__name__")
            if (func == "render") and (name == "zensical.markdown"):
                meta = frame_info.frame.f_locals.get("meta", {})
                return meta.get("contributors")
        return None

    def _format_contributor(self, contributor):
        name = contributor.get("name", "")
        github = contributor.get("github", "")
        if github:
            return f"[{name}](https://github.com/{github})"
        return name

    def _format_contributor_list(self, contributors):
        formatted = [self._format_contributor(c) for c in contributors if c.get("name")]
        if not formatted:
            return None
        if len(formatted) == 1:
            return formatted[0]
        if len(formatted) == 2:
            return f"{formatted[0]} and {formatted[1]}"
        return ", ".join(formatted[:-1]) + f", and {formatted[-1]}"

    def run(self, lines):
        contributors = self._contributors_from_render_frame()
        if not contributors:
            return lines

        contributor_str = self._format_contributor_list(contributors)
        if not contributor_str:
            return lines

        return lines + [
            "",
            "---",
            "",
            f"<p class='ref-contributors'><em>Contributed by: {contributor_str}</em></p>",
            "",
        ]


class ContributorsExtension(Extension):
    """Python Markdown extension that wires up the contributors preprocessor.

    Registered in `zensical.toml` under `[project.markdown_extensions.contributors]`.
    A priority of 29 places it just below the doi_reference preprocessor (30),
    so the contributors line is appended after any DOI header has been prepended.
    """

    def extendMarkdown(self, md):
        md.preprocessors.register(
            ContributorsPreprocessor(md), "contributors", 29
        )


def makeExtension(**kwargs):
    """Entry point called by Python Markdown when loading the extension by name."""
    return ContributorsExtension(**kwargs)
