---
tags:
- MCF
- gyrokinetics
- GS2
- TGLF
- Gene
- Cgyro
- Stella
- Gkw
- Gx
contributors:
- name: Felix Watts
  github: FelixWattsYork
comments: true
---

# Pyrokinetics
A variety of gyrokinetic and quasi-linear codes exist for modelling turbulent fluxes in tokamaks. Each have a unique input and output structure and have a different set of unit normalisation. 

Pyrokinetics is a Python package that allows the user to easily create gyrokinetic input files and outputs files in a uniform format for a vast array of gyrokinetic codes (see supported codes [here](https://pyrokinetics.readthedocs.io/en/latest/)). Pyrokinetics handles unit conversions between gyrokinetic codes, avoiding common missing factors of $\pi$, $\sqrt{2}$, etc., allowing for easy comparisons and conversion between gyro-Bohm and SI units. It simplifies creation of parameter scans, adds diagnostitcs to gyrokinetic outputs, all in addition to many other features.

Documentation: [https://pyrokinetics.readthedocs.io/en/latest/](https://pyrokinetics.readthedocs.io/en/latest/)

GitHub repository: [https://github.com/pyro-kinetics/pyrokinetics](https://github.com/pyro-kinetics/pyrokinetics)

Pyrokinetics is in active development with new features and improvements added constantly. There is a monthly Pyrokinetics users and developers meeting where recommendations are taken, new features are demonstrated and design goals are discussed. Link to join:
[https://teams.microsoft.com/meet/34783083564582?p=DryIUXHKtk0Cxg63zi](https://teams.microsoft.com/meet/34783083564582?p=DryIUXHKtk0Cxg63zi)

The development of Pyrokinetics is actively supported by both the University of York and UKAEA, and we welcome new contributors.
