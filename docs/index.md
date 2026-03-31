---
icon: lucide/home
comments: false
---

# Get started

## What is this?
A collection of useful resources related to plasma physics, material science and fusion power created by students on the [EPSRC CDT in Fusion Power](https://fusion-cdt.ac.uk/). 

!!! warning
    
    This is very much a work-in-progress.

## Project structure
The repository currently has the following hierarchical structure:
```
fusion-cdt-community-reading-list/docs
├── index.md
├── literature
│   ├── materials
│   └── plasma
│       ├── ICF
│       ├── LTP
│       └── MCF
│           ├── gyrokinetics
│           │   ├── abel2013multiscale-gyrokinetics.md
│           │   ├── highcock2012zero-turbulence.md
│           │   ├── howes2006astro-gyrokinetics.md
│           │   └── kotschenreuther1995gs2.md
│           └── zonal-flows
│               └── itoh2006zona-flows.md
└── tutorials
    ├── gyrokinetic-codes.md
    └── gyrokinetic-theory.md
```

The idea is that all literature notes will go in the [`literature`](./literature) folder under the relevant sub-folder. A disadvantage of this approach is that one paper may belong in several places, but we can only put it in one folder. We can ensure that papers are still easily discoverable via tags though (e.g. `gyrokinetics`, `zonal-flows`, etc.). Longer 'tutorial'-style notes will be stored in the [`tutorials`](./tutorials) folder. These will contain curated notes that aim to guide students through a topic (e.g. read pages 10-50 of paper X, then read chapter 2 of thesis Y, etc.).

## How do I contribute?
See [`CONTRIBUTING.md`](https://github.com/Fusion-CDT/community-reading-list/blob/main/CONTRIBUTING.md)
