<h1 align="center">
<img src="docs/images/Fusion_CDT_logo.png" width="400">
</h1><br>

<h1 align="center">
Community reading list
</h1>
<p align="center">
A collection of useful resources related to plasma physics, material science, fusion power and machine learning created by students on the <a href="https://fusion-cdt.ac.uk/">EPSRC CDT in Fusion Power</a>. 
</p>

> [!NOTE]
> This is a work-in-progress, any and all feedback is welcome.

## Accessing the live documentation

The documentation is available [here](https://fusion-cdt.github.io/community-reading-list/)

## Contributing to the documentation

This repository is a community-driven effort and is not actively maintained by a dedicated team. As such, some resources may become outdated. We warmly welcome contributions from the community to keep this list relevant! If you have resources to add or corrections to make, please feel free to do so. There are two ways you can contribute:
- Adding new papers/articles: Create a new [GitHub Issue](https://github.com/Fusion-CDT/community-reading-list/issues)
- Updating existing papers/articles or adding/updating tutorials: 
    - Use the edit button at the top of any page on the documentation and edit it on GitHub
    - Download the code and manually add the entries yourself

## Build locally
If you'd like to build the site locally, first clone the repository:
```sh
git clone https://github.com/Fusion-CDT/community-reading-list.git
```

Then change to the project directory:
```sh
cd community-reading-list
```

We recommend installing the dependencies using [`uv`](https://docs.astral.sh/uv/)
if you have it installed (needs `uv` version 0.8.0 or above):
```sh
uv sync && source .venv/bin/activate
```

Otherwise, using `pip` (you will need to have at least Python 3.10 installed for this to work):
```sh
python -m venv .venv && source .venv/bin/activate
pip install .
```

Finally build the site:
```sh
zensical serve
```

This should return an output that contains a URL at the end of the first line that you can open in a web browser. e.g.

```sh
$ zensical serve
Serving /Users/joel/Source/community-reading-list/site on http://localhost:8000
Build started
+ /tutorials/gyrokinetic-codes/
+ /literature/plasma/MCF/gyrokinetics/howes2006astro-gyrokinetics/
+ /literature/plasma/MCF/gyrokinetics/abel2013multiscale-gyrokinetics/
+ /
+ /literature/plasma/ICF/
+ /literature/
+ /tutorials/
+ /literature/plasma/MCF/gyrokinetics/kotschenreuther1995gs2/
+ /literature/plasma/
+ /literature/plasma/MCF/zonal-flows/itoh2006zona-flows/
+ /literature/plasma/MCF/
+ /literature/plasma/MCF/gyrokinetics/highcock2012zero-turbulence/
+ /literature/materials/
+ /tutorials/gyrokinetic-theory/
+ /literature/plasma/LTP/

```
