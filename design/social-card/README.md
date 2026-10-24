# Social preview card

`docs/images/social-card.png` is the image LinkedIn, Slack, Teams etc. show when someone shares a link to the site. This folder holds what it's made from:

| File | What it is |
| --- | --- |
| `social-card.svg` | The card's layout: background, logo, text and colours. Edit this. |
| `make_card.py` | Renders the SVG to `docs/images/social-card.png`. |

The logo comes straight from `docs/images/fusion-cdt-logo-white.svg`, so a new logo there appears on the card the next time it's rendered. The text is in Figtree, the site's font, which the SVG loads from Google Fonts just as the site does.

None of this is published: only the finished PNG in `docs/images/` is.

## Changing the card

1. Edit `social-card.svg`. Each line of text is its own `<text>` element, so a longer line won't wrap: check that it still fits in the render.
2. From the root of the repository, run:

   ```sh
   uv run design/social-card/make_card.py
   ```

   It uses your installed Chrome to draw the card, so it looks the same on any machine. It needs an internet connection to fetch the font, and stops with an error rather than use a different font if it can't. If you don't have Chrome, run `uv run --with playwright playwright install chromium` once first.

   To try out a change without replacing the real card, use `-o preview.png`.
3. Commit the SVG and the new PNG together.
4. After the site has deployed, paste the site's URL into LinkedIn's [Post Inspector](https://www.linkedin.com/post-inspector/). Otherwise LinkedIn keeps showing the old image for about a week.

Keep the card at 1200×630, the size LinkedIn and others expect. `overrides/main.html` tells them that size.
