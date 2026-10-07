---
tags:
  - MCF
  - Heat flux
  - Exhaust modelling
contributors:
  - name: "Michael I. Battye"
    github: "mbattye"
comments: true
---

# Heat flux Engineering Analysis Toolkit (HEAT)

## Introduction

HEAT is the [Heat flux Engineering Analysis Toolkit](https://github.com/plasmapotential/HEAT), developed by Tom Looby and collaborators for tokamak plasma-facing component (PFC) heat-load analysis. It brings magnetic equilibria, CAD or STL geometry, ray tracing, optical heat-flux models, ion gyro-orbit tracing, 3D magnetic perturbations, photon tracing, and thermal solvers such as OpenFOAM/Elmer into one workflow.

The motivation is practical: given a magnetic configuration and a PFC geometry, engineers and physicists need to know where heat lands, what is shadowed, what gets too hot, and how sensitive the answer is to geometry, strike point, power, and scrape-off-layer assumptions. HEAT has been used for SPARC PFC design and scenario planning, NSTX-U ion gyro-orbit heat-load studies, ST40 IR comparison, ASDEX Upgrade validation, and 3D RMP/error-field heat-flux calculations.

Use this page as a starting checklist. The official HEAT documentation is still the reference for the full set of input options and up-to-date Docker commands.

## Examples of HEAT literature

- T. Looby et al., [A software package for plasma-facing component analysis and design: the Heat flux Engineering Analysis Toolkit (HEAT)](https://doi.org/10.1080/15361055.2021.1951532), Fusion Science and Technology, 2021.
- T. Looby et al., [3D ion gyro-orbit heat load predictions for NSTX-U](https://doi.org/10.1088/1741-4326/ac8a05), Nuclear Fusion, 2022.
- E. J. C. Tinacba et al., [HEAT simulation and IR data comparison for ST40 plasma-facing components](https://doi.org/10.1016/j.nme.2024.101791), Nuclear Materials and Energy, 2024.
- A. Redl et al., [The Experimental Validation of HEAT on the ASDEX Upgrade Tokamak](https://doi.org/10.1080/15361055.2025.2478720), Fusion Science and Technology, 2025.
- A. Wingen et al., [Development and validation of non-axisymmetric heat flux simulations with 3D fields using the HEAT code](https://doi.org/10.1088/1741-4326/adeff1), Nuclear Fusion, 2025.
- M. D'Abusco et al., [3D modeling of n = 1 RMP driven heat fluxes on the SPARC tokamak PFCs using HEAT](https://iopscience.iop.org/article/10.1088/1741-4326/adf760/meta), Nuclear Fusion, 2025.
- D. Corona et al., [Shadow masks predictions in SPARC tokamak plasma-facing components using HEAT code and machine learning methods](https://doi.org/10.1016/j.fusengdes.2025.115010), Fusion Engineering and Design, 2025.

## Documentation and analysis tools

- [HEAT GitHub repository](https://github.com/plasmapotential/HEAT): source code, integration tests, Docker files, examples, issue tracker, and the current README.
- [HEAT Read the Docs](https://heat-flux-engineering-analysis-toolkit-heat.readthedocs.io/en/latest/): the main documentation. Start with the Docker, GUI, TUI, and Input File Reference pages.
- [HEAT Docker Hub image](https://hub.docker.com/r/plasmapotential/heat): the recommended way to run HEAT unless you are developing HEAT itself.
- [HEATtools](https://github.com/plasmapotential/HEATtools): companion pre/post-processing utilities.
- [ParaView](https://www.paraview.org/): the easiest way to inspect `.vtp`/VTK-style HEAT outputs, time traces, heat-flux point clouds, and temperature fields.
- [MAFOT documentation](https://github.com/ORNL-Fusion/MAFOT/tree/master/doc): relevant when using HEAT's 3D field/RMP workflows.
- [divertor-diagnostic-designer `scan_design_factory.py`](https://github.com/mbattye/divertor-diagnostic-designer/blob/main/create_data/scan_design_factory.py): a useful pattern for generating HEAT inputs and batch files for larger parameter sweeps, especially over `lqCN`, `S`, power, equilibrium, and component slices.

## Getting started

HEAT can be used through the GUI or the terminal interface (TUI), but Docker is the recommended setup route for both. The official [Docker instructions](https://heat-flux-engineering-analysis-toolkit-heat.readthedocs.io/en/latest/docker.html), [GUI tutorial](https://heat-flux-engineering-analysis-toolkit-heat.readthedocs.io/en/latest/GUItutorial.html), and [TUI tutorial](https://heat-flux-engineering-analysis-toolkit-heat.readthedocs.io/en/latest/TUItutorial.html) are the source of truth, and Tom Looby's tutorial videos/presentations linked from the HEAT docs/repo are worth watching before doing serious runs.

The minimum "shopping list" for a normal optical heat-flux run is:

1. A magnetic equilibrium, usually a GEQDSK/g-file, with the time you want to model.
2. Geometry for the PFCs and shadowing objects. Historically this meant STEP/CAD, but current HEAT also supports STL-based "Bring Your Own Mesh" workflows.
3. A PFC CSV describing which objects to analyse, their mesh resolution, timesteps, shadowing intersections, and exclusions.
4. An `X_input.csv` file defining the HEAT physics/settings, for example `hfmode`, `lqCN`, `S`, `P`, output flags, `traceLength`, `dpinit`, and optional OpenFOAM settings.
5. A `batchFile.dat` for terminal mode, telling HEAT which machine flag, tag, shot, timestep, equilibrium, CAD/PFC/input files, and outputs to run.
6. Enough disk space for `.csv`, `.vtp`, OpenFOAM/Elmer, and ParaView output, especially for scans.

A typical first pass is:

1. Install Docker and Docker Compose, then pull the HEAT image from Docker Hub. Use the current version tag from the HEAT docs/repo, for example:

   ```bash
   docker pull plasmapotential/heat:<version>
   ```

2. Clone the HEAT repo so you have the Docker compose files and integration tests:

   ```bash
   git clone https://github.com/plasmapotential/HEAT.git
   ```

3. Run an official integration test before setting up your own case. In the container, the tests live under `/root/source/HEAT/tests/integrationTests`; the TUI docs show optical, Elmer, and 3D-field examples.

4. Create a small terminal-mode case by copying an integration test structure. Keep the first run simple: one equilibrium, one component, optical heat flux only, `csvOut=True`, `vtpMeshOut=True`, and `vtpPCOut=True`.

5. Bind-mount your case directory into the container as `/root/terminal`, then run HEAT in terminal mode with a `batchFile.dat`, as described in the official TUI tutorial.

6. Open the HEAT output in ParaView. Start by checking geometry orientation, mesh units, shadow masks, field-line landing points, heat-flux point clouds, and only then temperature. If the geometry view looks wrong, the heat-flux answer is probably wrong too.

For bigger studies, avoid hand-writing large numbers of input files. A good scan workflow is to template `X_input.csv` and the PFC CSV, then generate one batch row per `(equilibrium, component, lqCN, S, P, time)` combination. The `scan_design_factory.py` pattern above uses Latin-hypercube/MaxEnt-style sampling and writes both HEAT input CSVs and `batchFile.dat` files for parameter sweeps.

## Key gotchas

- **STEP vs STL/BYOM:** STEP/CAD workflows are convenient when HEAT can mesh and identify named parts cleanly. STL/BYOM is often better when you already have a controlled mesh or need exact exported surfaces. With STL, check `STLscale` and units carefully; millimetre/metre mistakes are easy to miss.
- **Named components and shadowing:** The PFC CSV is not just a list of targets. It also controls what each target intersects with and excludes. If shadowing looks impossible, check `intersectName` and `excludeName` before changing physics.
- **`traceLength` and `dpinit`:** These define how far and how finely HEAT traces field lines. If `traceLength * dpinit` is too short, heat can skip legitimate intersections. If `dpinit` is too coarse, field lines can step over thin components or land on the back side of a surface. Increase the trace distance and reduce `dpinit` until the answer stops changing, then record those values.
- **Back-side loading:** If heat appears on the wrong side of a tile, suspect surface normals, mesh orientation, missing occluders, too-coarse trace stepping, or an overly permissive shadowing setup. Visualise field-line intersections and surface normals, not just final heat flux.
- **Time appears in several places:** The batch-file `TimeStep` selects the equilibrium/time slice for a run. `tmin` and `tmax` in `X_input.csv` describe the MHD equilibrium time range HEAT should consider. PFC CSV `timesteps` describe which geometry/PFC entries apply at which times. `OFtMin`, `OFtMax`, `deltaT`, and `writeDeltaT` are OpenFOAM thermal-simulation controls; in the current docs `writeDeltaT` should match `deltaT`.
- **Batch start/end times:** For time-dependent cases, it is common to generate batch rows at the start and end of the interval you want HEAT to interpolate across. These rows must share the same `Tag`; if the tags differ, HEAT treats them as independent runs rather than two time points of the same case. Keep the batch `TimeStep`, input `tmin/tmax`, PFC `timesteps`, and OpenFOAM times consistent, otherwise you can accidentally run the right geometry with the wrong equilibrium or thermal window.
- **Output volume:** `.vtp` and point-cloud outputs are invaluable while debugging, but large scans can produce huge directories. Turn on rich outputs for pilot cases, then reduce output volume once the workflow is trusted.
- **Git LFS for 3D-field examples:** The 3D fields test case uses large files. If you clone HEAT and want those tests, run `git lfs install` and `git lfs pull` as described in the HEAT README.
- **Do one visual sanity check per new machine/configuration:** Before launching a large scan, run a tiny case and inspect the equilibrium, CAD/STL, PFC surfaces, shadowing, field-line traces, and heat-flux pattern in ParaView. Most wasted HEAT time comes from batch-running a geometry or time selection mistake.
