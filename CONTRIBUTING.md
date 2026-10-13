# Contributing

## How do I contribute new literature?

New literature notes can be contributed by [creating a GitHub Issue](https://github.com/Fusion-CDT/community-reading-list/issues/new/choose) and choosing the template that matches what you're suggesting:

- **Suggest literature: paper** — journal articles and preprints. Give the **DOI**, and the title, authors and journal are filled in automatically on the site.
- **Suggest literature: textbook** — give the **title**, **authors**, **ISBN**, optionally where the book is **available** (e.g. "YPI library"), and any links.
- **Suggest literature: lecture notes or slides** — give the **title**, **authors** (if known) and links to the notes.

All three also ask for:

- **Location and filename** — a folder under `literature/` and a filename following the [filename convention](#filename-convention-for-literature-notes) below (e.g. `plasma/MCF/gyrokinetics/howes2006astro-gyrokinetics`)
- **Tags** — comma-separated tags to aid discoverability (e.g. `Gyrokinetics, MCF`). See [Choosing tags](#choosing-tags).
- **Content** — a brief description of why the resource is useful, written in Markdown (see this [Markdown cheat sheet](https://www.markdownguide.org/cheat-sheet/)). You can add [images](#adding-images) too.
- **Your name** (optional) — you'll be credited as a contributor at the bottom of the page, by your GitHub username or, if you give it, your name.

Once you submit the issue, a pull request will be automatically created and a maintainer will review it.

### Filename convention for literature notes

We use a [Better BibTeX](https://retorque.re/zotero-better-bibtex/)-style naming convention: `<firstauthor><year><shorttitle>.md`

- `<firstauthor>` — surname of the first author, lowercase (e.g. `howes`, `abel`)
- `<year>` — four-digit publication year (e.g. `2006`, `2013`)
- `<shorttitle>` — a short, descriptive kebab-case or snake-case label for the work (e.g. `astro-gyrokinetics`, `multiscale-gyrokinetics`)

Examples from the repository:

| File | Author | Year | Short title |
|------|--------|------|-------------|
| `howes2006astro-gyrokinetics.md` | Howes | 2006 | astro-gyrokinetics |
| `abel2013multiscale-gyrokinetics.md` | Abel | 2013 | multiscale-gyrokinetics |
| `highcock2012zero-turbulence.md` | Highcock | 2012 | zero-turbulence |
| `kotschenreuther1995gs2.md` | Kotschenreuther | 1995 | gs2 |

### Choosing tags

Tags help readers find related notes, so a few well-chosen tags are better than many generic ones.

- **Reuse existing tags where possible.** The [Tags page](https://fusion-cdt.github.io/community-reading-list/tags/) lists every tag in use, with the pages that use it.
- **Use sentence case with spaces**, e.g. `Zonal flows`, not `zonal-flows` or `Zonal Flows`.
- **Keep the official spelling of acronyms and code names**, e.g. `MCF`, `GS2`, `CGYRO`, `stella`.
- **Avoid tags that apply to almost everything**, such as `Theory`, `Simulation` or `Plasma physics`.

New tags are welcome when none of the existing ones fit; a maintainer will check them when reviewing your pull request.

## How do I contribute new tutorials?

New tutorial notes can be contributed by [creating a GitHub Issue](https://github.com/Fusion-CDT/community-reading-list/issues/new/choose) and selecting the **"Suggest tutorial"** template. Fill in as many fields as you can:

- **Location and filename** — where in the reading list it should live and what to call it (e.g. `docs/tutorials/gyrokinetic-theory.md`)
- **Tags** — comma-separated tags to aid discoverability (e.g. `Gyrokinetics, MCF`). See [Choosing tags](#choosing-tags).
- **Content** — the body of your tutorial, written in Markdown (see this [Markdown cheat sheet](https://www.markdownguide.org/cheat-sheet/)). You can add [images](#adding-images) too.
- **Your name** (optional) — as for literature notes, you'll be credited by your GitHub username or, if you give it, your name.

Once you submit the issue, a pull request will be automatically created and a maintainer will review it.

## How do I edit an existing literature or tutorial note?

### Using the edit button (recommended)

1. Navigate to the page you want to edit on the [reading list site](https://fusion-cdt.github.io/community-reading-list/).
2. Click the **edit** button at the top of the page (pencil icon).
3. This opens the edit form for that kind of page (paper, textbook, lecture notes or tutorial) on GitHub. It's filled in with the page's current details, such as its tags, title and links, and its text in the **"Proposed content"** field. (Very long pages can't have their text filled in; the form explains what to do.)
4. Describe what needs changing in the **"What needs changing?"** field.
5. Make your changes to the details and to the **"Proposed content"** field, then submit the issue.

A pull request with your changes will be automatically created and a maintainer will review it. You'll be added to the page's contributors, by your GitHub username or, if you give it, your name.

### Using Git directly

If you are comfortable with Git and want to contribute changes directly:

1. Clone the repository:
   ```sh
   git clone https://github.com/Fusion-CDT/community-reading-list.git
   ```
2. Create a new branch for your changes:
   ```sh
   git switch -c <your-branch-name>
   ```
3. Make your edits. To add a new file, create it in the appropriate subfolder under `docs/` following the [filename convention](#filename-convention-for-literature-notes), starting with [frontmatter](#writing-frontmatter-by-hand).
4. Put the frontmatter in the standard layout (you'll need [uv](https://docs.astral.sh/uv/)):
   ```sh
   uv run scripts/format_notes.py
   ```
   The build check on your pull request fails if any frontmatter isn't in this layout.
5. Stage and commit your changes:
   ```sh
   git add <file>
   git commit -m "<short description of your change>"
   ```
6. Push the branch to GitHub:
   ```sh
   git push -u origin <your-branch-name>
   ```
7. Open a pull request on GitHub from your branch into `main`.

### Writing frontmatter by hand

Each note starts with frontmatter: details about the note, between two `---` lines. For a paper:

```yaml
---
doi: "10.1063/1.2178779"
tags:
  - "MCF"
  - "Zonal flows"
contributors:
  - {"name": "Ada Lovelace", "github": "ada"}
comments: true
---
```

The title, authors and journal are filled in on the site from the DOI. For a textbook or lecture notes, which don't have one, give `title` and `authors` instead, plus `isbn` (or `"N/A"` if it has none) and, optionally, `availability` for a textbook, and any links as a list under `url`, with the text to show for each under `url_name`.

You don't need to get the layout exactly right: `uv run scripts/format_notes.py` puts the keys in order and the values in quotes.

## Adding images

### In an issue form

Upload your images in the **Images** field, then refer to each one by its filename in your text:

```markdown
![Diagram of the gyrokinetic geometry](gyrokinetic-geometry.png)
```

You can also paste or drag an image straight into the text box.

Either way, a copy of each image is stored in the repository next to the page, so it doesn't depend on GitHub keeping the attachment. Images are renamed to start with the page's filename (e.g. `howes2006astro-gyrokinetics-gyrokinetic-geometry.png`) so that pages in the same folder can't overwrite each other's images; links in your text are updated to match.

### Using Git

Commit images in the same directory as the Markdown page that uses them. Use a descriptive filename with no spaces, starting with the page's filename, for example `howes2006astro-gyrokinetics-geometry.png`.

Reference the image using its filename relative to the Markdown page:

```markdown
![Diagram of the gyrokinetic geometry](howes2006astro-gyrokinetics-geometry.png)
```

Check that the filename in the Markdown matches the committed file exactly, including its capitalisation, and that the image renders in the built site before opening the pull request.

Please only add images you have the right to share, and say where they come from.
