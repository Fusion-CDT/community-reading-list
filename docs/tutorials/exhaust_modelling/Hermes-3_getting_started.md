---
tags:
  - MCF
  - Fluid code
  - Exhaust modelling
contributors:
  - name: "John Lloyd Baker"
    github: "PoloidalLloyd"
comments: true
---

# Hermes-3 getting started

Hermes-3 is a plasma simulation model built on [BOUT++](http://boutproject.github.io/), developed mainly for simulating the edge of magnetically confined plasmas such as tokamaks. The source code is [available on Github](https://github.com/boutproject/hermes-3). The main aim of this model is multi-species simulation of fusion reactors, where the plasma will contain a mixture of deuterium, tritium, helium and other species. 

Hermes-3 is multi-fidelity, allowing the simulation of 1D, 2D and 3D tokamak plasmas both in steady-state and unsteady / turbulent regimes.

It is designed to be modular and organised into reusable components, which can be tested individually and then configured at run-time.

Please see below for other useful Hermes-3 resources, there is also a Hermes-3 [Zulip](https://zulip.com/) channel, a slack-like service where significant amounts of Hermes-3 support can be accessed. Please contact John.Lloyd.baker@york.ac.uk if you would like to be added to this.

## Examples of Hermes-3 literature

B.Dudson, M.Kryjak, H.Muhammed, P.Hill, J,Omotani [Hermes-3: Multi-component plasma simulations with BOUT++](https://doi.org/10.1016/j.cpc.2023.108991) Comp. Phys. Comm. 2023 108991. doi: [10.1016/j.cpc.2023.108991](https://doi.org/10.1016/j.cpc.2023.108991). Preprint: [arXiv.2303.12131](https://doi.org/10.48550/arXiv.2303.12131).

G.K. Holt, A. Keats, S. Pamela, M. Kryjak, A. Agnello, N.C. Amorisco, B.D. Dudson and M. Smyrnakis [Tokamak divertor plasma emulation with machine learning](https://doi.org/10.1088/1741-4326/ad4f9e) 2024 Nucl. Fusion 64 086009 doi: [10.1088/1741-4326/ad4f9e](https://doi.org/10.1088/1741-4326/ad4f9e)

Thomas Body, Thomas Eich, Adam Kuang, Tom Looby, Mike Kryjak, Ben Dudson, Matthew Reinke [Detachment scalings derived from 1D scrape-off-layer simulations](https://doi.org/10.1016/j.nme.2024.101819) Nucl. Mat. Energy 2024 101819 doi: [10.1016/j.nme.2024.101819](https://doi.org/10.1016/j.nme.2024.101819)

Huayi Chang, Ben Dudson, Jizhong Sun, Mike Kryjak, Yang Ye, Mao Li, Weikang Wang [Hermes-3 simulation of the low-n X-point mode driven by impurity in tokamak edge plasmas](https://doi.org/10.1016/j.nme.2025.101913) Nucl. Mat. Energy 2025 101913 doi: [10.1016/j.nme.2025.101913](https://doi.org/10.1016/j.nme.2025.101913) 

John Lloyd Baker, Mike Kryjak, Michael Wigram, Stefan Mijin, Dominic Power, Benjamin Dudson and Christopher Ridgers, [The impact of non-local fluid models on 1D impurity driven detachment in an ITER-like SOL](https://doi.org/10.1088/1361-6587/ae56b4), Plasma Phys. Control. Fusion 2026 doi [10.1088/1361-6587/ae56b4](https://doi.org/10.1088/1361-6587/ae56b4)

## Documentation and analysis tools
[BOUT++ ReadTheDocs](https://bout-dev.readthedocs.io/en/stable/)

[Hermes-3 ReadTheDocs](https://hermes3.readthedocs.io/en/latest/) (The main Hermes-3 documentation, It really is worth getting familiar with this as it will give you a users understanding of how the code works in a relatively succinct way)

[Hermes-3 xhermes ](https://github.com/boutproject/xhermes)(Hermes-3 python3 analysis library based on Xarray)

[Hermes-3 SDTOOLS](https://github.com/mikekryjak/sdtools) (A large number of additional tools for Hermes-3 analysis can be found here in Mike Kryjak's repo, basically treat it as an extension to xhermes)

## Getting started 

I appreciate that's quite a lot of different links, but I'll give you a brief run down of how I would get started, the Hermes-3 ReadTheDocs also has detailed instructions on how to run some example cases. The approach I would take would be:

1. Build Hermes-3 on the platform of your choosing (now this should be straightforward if you're operating on a linux device using SPACK, the instructions for this are found [here)](https://hermes3.readthedocs.io/en/latest/installation.html#install-spack). 

2. Once this is done, have a go at running the 1D example found [here](https://github.com/boutproject/hermes-3/tree/master/examples/tokamak-1D/1D-threshold). How to run this can be found [here](https://hermes3.readthedocs.io/en/latest/examples.html). after this you may wish to move onto 2D and 3D examples depending on your use case.

3. Analyse the results, an example of how to use the Hermes-3 python analysis library ([xhermes](https://github.com/boutproject/xhermes/blob/main/examples/1d-postprocessing.ipynb)) can be found [here](https://github.com/boutproject/xhermes/blob/main/examples/1d-postprocessing.ipynb).
