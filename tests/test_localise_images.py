import pytest

from localise_images import localise

ASSETS = "https://github.com/user-attachments/assets/"
PNG = b"\x89PNG fake image"


def fake_fetch(responses):
    """Return a fetch function serving `responses` and recording calls."""
    calls = []

    def fetch(url):
        calls.append(url)
        result = responses[url]
        if isinstance(result, Exception):
            raise result
        return result

    fetch.calls = calls
    return fetch


@pytest.fixture
def note(tmp_path):
    path = tmp_path / "howes2006astro-gyrokinetics.md"

    def write(body):
        path.write_text("---\ntags:\n  - MCF\n---\n\n" + body)
        return path

    return write


def test_uploads_are_stored_and_references_rewritten(note):
    path = note("![Flow](angular velocity.png)\n")
    fetch = fake_fetch({ASSETS + "a": (PNG, "image/png")})
    localise(path, [{"name": "angular velocity.png", "url": ASSETS + "a"}], fetch)

    stored = path.parent / "howes2006astro-gyrokinetics-angular-velocity.png"
    assert stored.read_bytes() == PNG
    assert "![Flow](howes2006astro-gyrokinetics-angular-velocity.png)" in path.read_text()


def test_pasted_images_become_markdown(note):
    path = note(
        f'<img width="709" alt="Cross sections" src="{ASSETS}b" />\n\n'
        f"![Again]({ASSETS}b)\n"
    )
    fetch = fake_fetch({ASSETS + "b": (PNG, "image/png")})
    localise(path, [], fetch)

    text = path.read_text()
    assert "![Cross sections](howes2006astro-gyrokinetics-image.png)" in text
    assert "![Again](howes2006astro-gyrokinetics-image.png)" in text
    assert fetch.calls == [ASSETS + "b"]  # downloaded once


def test_frontmatter_and_other_links_untouched(note):
    path = note("![Logo](https://example.com/logo.png)\n")
    localise(path, [], fake_fetch({}))
    assert path.read_text() == "---\ntags:\n  - MCF\n---\n\n![Logo](https://example.com/logo.png)\n"


def test_failed_or_non_image_downloads_keep_the_link(note, capsys):
    path = note(f"![PDF]({ASSETS}pdf)\n\n![Gone]({ASSETS}gone)\n")
    fetch = fake_fetch({
        ASSETS + "pdf": (b"%PDF", "application/pdf"),
        ASSETS + "gone": OSError("404"),
    })
    assert localise(path, [], fetch) == []
    assert f"![PDF]({ASSETS}pdf)" in path.read_text()
    assert f"![Gone]({ASSETS}gone)" in path.read_text()
    assert capsys.readouterr().out.count("::warning::") == 2


def test_existing_images_are_not_overwritten(note):
    path = note("![Plot](plot.png)\n")
    existing = path.parent / "howes2006astro-gyrokinetics-plot.png"
    existing.write_bytes(b"old")
    fetch = fake_fetch({ASSETS + "c": (PNG, "image/png")})
    localise(path, [{"name": "plot.png", "url": ASSETS + "c"}], fetch)

    assert existing.read_bytes() == b"old"
    assert "![Plot](howes2006astro-gyrokinetics-plot-2.png)" in path.read_text()


def test_unused_upload_is_still_stored_with_a_warning(note, capsys):
    path = note("No images referenced.\n")
    fetch = fake_fetch({ASSETS + "d": (PNG, "image/png")})
    written = localise(path, [{"name": "spare.png", "url": ASSETS + "d"}], fetch)
    assert [p.name for p in written] == ["howes2006astro-gyrokinetics-spare.png"]
    assert "isn't used" in capsys.readouterr().out


def test_only_github_attachments_are_downloaded(note, capsys):
    path = note("![x](evil.png)\n")
    fetch = fake_fetch({})
    localise(path, [{"name": "evil.png", "url": "https://example.com/evil.png"}], fetch)
    assert fetch.calls == []
    assert "only GitHub attachment links" in capsys.readouterr().out
