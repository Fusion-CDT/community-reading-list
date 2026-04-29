---
tags:
  - Laser-plasma
  - PIC
  - ### Introduction
  - [SMILEI](https://smileipic.github.io/Smilei/index.html) is a Particle-In-Cell (PIC) code
  - i.e. it works on the same core principle as EPOCH. It is also open-source. While EPOCH is written in Fortran
  - SMILEI is primarily written in C++ and accepts input decks written in Python. The two codes have broadly similar functionality
  - but when developing tools for use with PIC codes in general
  - it may be desirable to ensure compatibility with both EPOCH and SMILEI
  - for example.
  - ### Installation
  - SMILEI can be operated in any dimensionality from the same build
  - and thus requires only one installation. The source code be cloned using Git:
  - ```bash
  - git clone https://github.com/SmileiPIC/Smilei.git
  - ```
  - The modules to be loaded may vary by device
  - but for installation on Viking
  - a working installation can be made using the most recent compatible versions of GCC
  - OpenMPI
  - CMake
  - Python
  - HDF5
  - and SciPy-bundle. Use the `module load` command to load each of these modules.
  - The executable can then be made using the command `make`. the option `-j 8` can be used to speed up compilation by using more cores.
  - For large simulations
  - such as 3D laser-plasma interactions
  - it may be preferable to compile for GPU
  - which
  - for compilation on Viking is an ongoing issue and will be made available here once solved.
  - ### Links
  - Documentation can be found on the [website](https://smileipic.github.io/Smilei/use.html)
  - including [installation instructions](https://smileipic.github.io/Smilei/Use/installation.html)
  - [tutorials](https://smileipic.github.io/tutorials/)
  - and details on how the [namelist](https://smileipic.github.io/Smilei/Use/namelist.html) is written.
  - Source code is available from Github: <https://github.com/SmileiPIC/Smilei.git>
contributors:
  - name: "Chris Herdman"
    github: "Chrimspie"
comments: true
---


