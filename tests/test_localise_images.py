import pytest

from localise_images import localise, safe_name

ASSETS = "https://github.com/user-attachments/assets/"
PNG = b"\x89PNG fake image"


class FakeFetch:
    """A stand-in for `download` that doesn't use the network.

    It serves `responses`, {url: (data, content type)}, or raises the
    exception given for a URL, and records each URL it's asked for in
    `calls`.
    """

    def __init__(self, responses: dict[str, tuple[bytes, str] | Exception]):
        self.responses = responses
        self.calls: list[str] = []

    def __call__(self, url: str) -> tuple[bytes, str]:
        self.calls.append(url)
        result = self.responses[url]
        if isinstance(result, Exception):
            raise result
        return result


@pytest.fixture
def note(tmp_path):
    """Return a function that writes a note with the given body.

    The note has some frontmatter, and is named like a real note, so the
    stored images are named e.g. howes2006astro-gyrokinetics-plot.png.
    """
    path = tmp_path / "howes2006astro-gyrokinetics.md"

    def write(body):
        path.write_text("---\ntags:\n  - MCF\n---\n\n" + body)
        return path

    return write


def test_uploads_are_stored_and_references_rewritten(note):
    """An upload is stored next to the note, and the note links to it."""
    path = note("![Flow](angular velocity.png)\n")
    fetch = FakeFetch({ASSETS + "a": (PNG, "image/png")})
    upload = {"name": "angular velocity.png", "url": ASSETS + "a"}
    localise(path, [upload], fetch)

    stored = path.parent / "howes2006astro-gyrokinetics-angular-velocity.png"
    assert stored.read_bytes() == PNG
    text = path.read_text()
    assert "![Flow](howes2006astro-gyrokinetics-angular-velocity.png)" in text


def test_pasted_images_become_markdown(note):
    """Pasted images, as <img> tags or Markdown, link to one stored copy."""
    path = note(
        f'<img width="709" alt="Cross sections" src="{ASSETS}b" />\n\n'
        f"![Again]({ASSETS}b)\n"
    )
    fetch = FakeFetch({ASSETS + "b": (PNG, "image/png")})
    localise(path, [], fetch)

    text = path.read_text()
    assert "![Cross sections](howes2006astro-gyrokinetics-image.png)" in text
    assert "![Again](howes2006astro-gyrokinetics-image.png)" in text
    assert fetch.calls == [ASSETS + "b"]  # downloaded once


def test_frontmatter_and_other_links_untouched(note):
    """A note with no GitHub images is left exactly as it was."""
    path = note("![Logo](https://example.com/logo.png)\n")
    localise(path, [], FakeFetch({}))
    assert path.read_text() == (
        "---\ntags:\n  - MCF\n---\n\n![Logo](https://example.com/logo.png)\n"
    )


def test_failed_or_non_image_downloads_keep_the_link(note, capsys):
    """An image that can't be stored keeps its GitHub link, with a warning.

    That covers a download that fails and a file that isn't an image.
    """
    path = note(f"![PDF]({ASSETS}pdf)\n\n![Gone]({ASSETS}gone)\n")
    fetch = FakeFetch({
        ASSETS + "pdf": (b"%PDF", "application/pdf"),
        ASSETS + "gone": OSError("404"),
    })
    assert localise(path, [], fetch) == []
    text = path.read_text()
    assert f"![PDF]({ASSETS}pdf)" in text
    assert f"![Gone]({ASSETS}gone)" in text
    assert capsys.readouterr().out.count("::warning::") == 2


def test_existing_images_are_not_overwritten(note):
    """If the image's filename is taken, it's stored under a new one."""
    path = note("![Plot](plot.png)\n")
    existing = path.parent / "howes2006astro-gyrokinetics-plot.png"
    existing.write_bytes(b"old")
    fetch = FakeFetch({ASSETS + "c": (PNG, "image/png")})
    localise(path, [{"name": "plot.png", "url": ASSETS + "c"}], fetch)

    assert existing.read_bytes() == b"old"
    text = path.read_text()
    assert "![Plot](howes2006astro-gyrokinetics-plot-2.png)" in text


def test_unused_upload_is_still_stored_with_a_warning(note, capsys):
    """An upload the note doesn't use is stored, with a warning."""
    path = note("No images referenced.\n")
    fetch = FakeFetch({ASSETS + "d": (PNG, "image/png")})
    upload = {"name": "spare.png", "url": ASSETS + "d"}
    written = localise(path, [upload], fetch)
    names = [p.name for p in written]
    assert names == ["howes2006astro-gyrokinetics-spare.png"]
    assert "isn't used" in capsys.readouterr().out


def test_only_github_attachments_are_downloaded(note, capsys):
    """An upload URL that isn't a GitHub attachment isn't downloaded."""
    path = note("![x](evil.png)\n")
    fetch = FakeFetch({})
    upload = {"name": "evil.png", "url": "https://example.com/evil.png"}
    localise(path, [upload], fetch)
    assert fetch.calls == []
    assert "only GitHub attachment links" in capsys.readouterr().out


def test_similar_links_are_kept_apart(note):
    """One attachment's link isn't rewritten inside a longer one's."""
    path = note(f"![A]({ASSETS}abc)\n\n![B]({ASSETS}abcdef)\n")
    fetch = FakeFetch({
        ASSETS + "abc": (PNG, "image/png"),
        ASSETS + "abcdef": (PNG, "image/png"),
    })
    localise(path, [], fetch)
    text = path.read_text()
    assert "![A](howes2006astro-gyrokinetics-image.png)" in text
    assert "![B](howes2006astro-gyrokinetics-image-2.png)" in text


def test_other_img_tags_are_left_alone(note):
    """An <img> tag that doesn't link to a GitHub attachment is kept."""
    path = note('<img alt="Logo" src="https://example.com/logo.png">\n')
    localise(path, [], FakeFetch({}))
    text = path.read_text()
    assert '<img alt="Logo" src="https://example.com/logo.png">' in text


def test_safe_name():
    """Filenames lose spaces, punctuation and any folders in front."""
    assert safe_name("My plot (1).png") == "My-plot-1.png"
    assert safe_name("../../secret.png") == "secret.png"


def test_upload_references_with_spaces(note):
    """A name with spaces is found URL-encoded (%20) or in <...> too."""
    path = note(
        "![A](angular%20velocity.png)\n\n![B](<angular velocity.png>)\n"
    )
    fetch = FakeFetch({ASSETS + "a": (PNG, "image/png")})
    upload = {"name": "angular velocity.png", "url": ASSETS + "a"}
    localise(path, [upload], fetch)
    text = path.read_text()
    assert "![A](howes2006astro-gyrokinetics-angular-velocity.png)" in text
    assert "![B](howes2006astro-gyrokinetics-angular-velocity.png)" in text
