---
tags:
  - TGLF
  - gyrokinetics
  - gyrofluid
contributors:
  - name: "Felix Watts"
    github: "FelixWattsYork"
comments: true
---

# TGLF

## Introduction
TGLF is a Gyrofluid qausilinear model of turbulent fluxes. It exists in a class of "reduced models" that aim to replicate the flux predictions of Gyrokinetic models at a fraction of the computational cost. However, unlike surrogate models, it is still physics based, being built on a eigenvalue solver for the linear gyrofluid equations, meaning TGLF is not limited to a strict parameter space. As a result TGLF is often used in integrated models, (models used to evolve a plasma profile), such as JETTO. TGLF is the successor to the code GLF, and will be replaced with the yet to be released code GFTM (TGLF with the new linear solver GFS). 

## Useful Links

Documentation:

- <https://gafusion.github.io/doc/tglf.html>
- <https://gacode.io/>

Github: <https://github.com/gafusion/gacode/>


## Physics background

TGLF is a quasilinear model, meaning it is constructed from a linear model for plasma turbulence, and a saturation rule. The linear model predicts the growth rate of the most unstable turbulent mode, as well as its associated frequency. The saturation rule uses the linear growth rate to predict the final amplitude of the perturbed fields, based on physics based arguments and numerical fitting. The maximum field amplitude is combined with a flux weight derived from the instability frequency, in order to calculate the turbulent flux of the mode. 

The growth rate is calculated via constructing the linearized gyrofluid equations in matrix form, via prescribing the moments of the gyrofluid equations as a sum of hermitian basis functions. The eigenvalues of this matrix equations give the growth rate and frequency of the mode, and the eigenfunction can be used to identify the mode type. The Gyrofluid equations are derived via taking moments of the linear Gyrokinetic equations. The formulation of these moments is an area of active research with the distinction of gyrofluid codes being in how the gyrofluid equations are derived. In TGLF the trapped and passing particle are treated as independent species, giving TGLF its full name as the Trapped Gyro landau Fluid model

There are 3 Saturation rules in use in TGLF, with more in development. They work independently of the linear solver, although their validity does depend on the linear solvers accuracy. The Saturation rules used in TGLF will be carried over to its successor GFTM

The best source on workings of TGLF can be found in its original papers: <https://pubs.aip.org/aip/pop/article/14/5/055909/929642/A-theory-based-transport-model-with-comprehensive>
with this second paper having the best explanation of the effects of numerical parameters of TGLF results <https://pubs.aip.org/aip/pop/article/12/10/102508/316815/Gyro-Landau-fluid-equations-for-trapped-and>

However it's shortfalls are best high lighted in the paper on its sequel GFS, which explicitly points out its failures in high beta regions; <https://pubs.aip.org/aip/pop/article/30/10/102501/2914182/A-flexible-gyro-fluid-system-of-equations>

 For its saturation rules, the best introduction to both the theory of saturation rules and their specific implementation is Harry Dudding's thesis, specifically chapter 4. This thesis also contains the methodology for the development of the latest saturation rule for TGLF, sat 3

<https://etheses.whiterose.ac.uk/id/eprint/32664/>

However, For a more in depth explanation of methodology behind the original saturation rule development, here are the original papers for Sat 1 and Sat 2. The original Sat 0 paper is also useful as an introduction to the mixing length approximation 

Sat 1: <https://iopscience.iop.org/article/10.1088/0029-5515/53/11/113017>

Sat 2: <https://iopscience.iop.org/article/10.1088/1741-4326/ac243a/pdf>

Sat 0: <https://pubs.aip.org/aip/pop/article/15/5/055908/1015727/The-first-transport-code-simulations-using-the>

## Running TGLF

TGLF can be downloaded from the GA code GitHub repository. For a specific machine an environment file will need to be specified before the code can be compiled and run. TGLF inputs and outputs are well documented on the gacode website, however it is recommended to use the python package Pyrokinetics (see associated tutorial), for reading outputs.
