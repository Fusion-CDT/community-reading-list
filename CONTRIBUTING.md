# Contributing

## How do I contribute new literature?

New literature notes can be contributed by [creating a GitHub Issue](https://github.com/Fusion-CDT/community-reading-list/issues/new/choose) and selecting the **"Suggest literature"** template. Fill in as many fields as you can:

- **DOI** — the DOI of the paper or resource, if available (e.g. `10.1063/1.2178779`)
- **Location and filename** — where in the reading list it should live and what to call it, following the [filename convention](#filename-convention-for-literature-notes) above (e.g. `plasma/MCF/gyrokinetics/howes2006astro-gyrokinetics`)
- **Tags** — comma-separated tags to aid discoverability (e.g. `gyrokinetics, MCF`)
- **Content** — a brief description of why the resource is useful, written in Markdown

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

## How do I contribute new tutorials?
> [!NOTE]
> Contributing new tutorial notes is not currently supported via the issue workflow. This section will be updated once a process is in place.

## How do I edit an existing literature or tutorial note?

### Using the edit button (recommended)

1. Navigate to the page you want to edit on the [reading list site](https://fusion-cdt.github.io/community-reading-list/).
2. Click the **edit** button at the top of the page (pencil icon).
3. This will open the **"Edit existing literature entry"** (or equivalent) issue template on GitHub, pre-populated with the current page content.
4. Describe what needs changing in the **"What needs changing?"** field.
5. Make your edits in the **"Proposed content"** field and submit the issue.

A maintainer will review the proposed changes and open a pull request on your behalf.

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
