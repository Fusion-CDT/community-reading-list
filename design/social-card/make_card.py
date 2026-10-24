# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.50"]
# ///
"""
Render social-card.svg to docs/images/social-card.png.

The card is drawn by Chrome, so it looks the same on every machine. The font
(Figtree, the site's font) comes from Google Fonts, so rendering needs an
internet connection, but nothing needs installing apart from Chrome itself.
If Chrome isn't installed, this falls back to Playwright's own Chromium, which
needs a one-off download first:

    uv run --with playwright playwright install chromium

Usage:

    uv run design/social-card/make_card.py                 # update the card
    uv run design/social-card/make_card.py -o preview.png  # write elsewhere
"""

import argparse
import re
import sys
from pathlib import Path

from playwright.sync_api import Browser, Error, Playwright, sync_playwright

HERE = Path(__file__).resolve().parent
SVG = HERE / "social-card.svg"
OUTPUT = HERE.parents[1] / "docs" / "images" / "social-card.png"
WIDTH, HEIGHT = 1200, 630


def font_weights(svg: Path) -> list[str]:
    """Return the font weights the SVG's text uses, e.g. ["400", "800"]."""
    return sorted(set(re.findall(r'font-weight="(\d+)"', svg.read_text())))


def check_images(svg: Path) -> None:
    """Exit with an error if an image the SVG uses doesn't exist.

    Chrome draws a missing image as nothing at all, so without this a moved
    or renamed logo would silently disappear from the card.
    """
    for href in re.findall(r'<image[^>]*\bhref="([^"]+)"', svg.read_text()):
        if not (svg.parent / href).is_file():
            sys.exit(f"error: {svg.name} uses {href}, which doesn't exist")


def launch(p: Playwright) -> Browser:
    """Start Chrome, or Playwright's Chromium if Chrome isn't installed."""
    try:
        return p.chromium.launch(channel="chrome")
    except Error:
        return p.chromium.launch()


def render(svg: Path, output: Path) -> None:
    """Screenshot the SVG at full size, after checking its font loaded.

    If the font can't be loaded (e.g. when offline), Chrome falls back to
    another font without complaint, so check every weight the text uses
    rather than write a card in the wrong font.
    """
    with sync_playwright() as p:
        browser = launch(p)
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
        page.goto(svg.as_uri())
        for weight in font_weights(svg):
            # Resolves to the font faces loaded, so an empty list means the
            # font isn't available in this weight.
            loaded = page.evaluate(
                "w => document.fonts.load(w + ' 16px Figtree')"
                ".then(faces => faces.length, () => 0)",
                weight,
            )
            if not loaded:
                sys.exit(f"error: couldn't load Figtree at weight {weight}")
        page.evaluate("document.fonts.ready.then(() => null)")
        page.screenshot(path=output)
        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render social-card.svg to a PNG."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUTPUT,
        help="where to write the PNG (default: docs/images/social-card.png)",
    )
    args = parser.parse_args()
    check_images(SVG)
    render(SVG, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
