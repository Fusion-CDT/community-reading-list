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
- **Your name** (optional) — you'll be credited as a contributor at the bottom of the page.

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

Once you submit the issue, a pull request will be automatically created and a maintainer will review it.

## How do I suggest other resources?

For tools, code, datasets or anything else that isn't a paper, textbook, set of lecture notes or tutorial, [open a blank issue](https://github.com/Fusion-CDT/community-reading-list/issues/new) with a link and a sentence or two on why it's useful, and a maintainer will add it to the [Resources](https://fusion-cdt.github.io/community-reading-list/resources/) section. Or, if you're comfortable with Git, add a page under `docs/resources/` yourself.

## How do I edit an existing literature or tutorial note?

### Using the edit button (recommended)

1. Navigate to the page you want to edit on the [reading list site](https://fusion-cdt.github.io/community-reading-list/).
2. Click the **edit** button at the top of the page (pencil icon).
3. This will open the **"Edit existing literature entry"** (or equivalent) issue template on GitHub, with the **"Proposed content"** field pre-filled with the page's current text. (Very long pages can't be pre-filled; the form explains what to do.)
4. Describe what needs changing in the **"What needs changing?"** field.
5. Make your edits in the **"Proposed content"** field and submit the issue.

A pull request with your changes will be automatically created and a maintainer will review it.

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
3. Make your edits. To add a new file, create it in the appropriate subfolder under `docs/` following the [filename convention](#filename-convention-for-literature-notes).
4. Stage and commit your changes:
   ```sh
   git add <file>
   git commit -m "<short description of your change>"
   ```
5. Push the branch to GitHub:
   ```sh
   git push -u origin <your-branch-name>
   ```
6. Open a pull request on GitHub from your branch into `main`.

## Adding images

- **In an issue form**, paste or drag an image into the **Content** (or **Proposed content**) box. GitHub uploads it and inserts a link like `![image](https://github.com/user-attachments/assets/...)`, which also displays on the site.
- **Using Git**, put the image in the same folder as the note and link to it by filename, e.g. `![Tokamak cross-section](tokamak-cross-section.png)`.

Please only add images you have the right to share, and say where they come from.
