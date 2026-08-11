# Ligand-Specific Dissociation Pathways of preQ1 and SAM-III Riboswitches

**Simulation data and analysis workflow**

[![Study](https://img.shields.io/badge/study-RNA--ligand%20dissociation-4B8BBE.svg)](#)
[![MD](https://img.shields.io/badge/MD-GROMACS-1F6FEB.svg)](#)
[![Enhanced Sampling](https://img.shields.io/badge/enhanced%20sampling-PaCS--MD-7B2CBF.svg)](#)

## Overview

Riboswitches are structured RNA elements that directly recognize small metabolites and regulate gene expression.  
Although high-resolution structures provide detailed views of ligand-bound states, ligand release is a dynamic and comparatively underexplored process.

This repository supports the study:

> **Ligand-Specific Dissociation Pathways of preQ1 and SAM-III Riboswitches**

The project combines conventional all-atom molecular dynamics (MD), **parallel cascade selection molecular dynamics (PaCS-MD)**, Markov state model (MSM)-based free-energy analysis, three-dimensional pathway mapping, and ligand–RNA interaction analysis.

Two structurally distinct riboswitch systems were examined:

- **preQ1 riboswitch:** apo, preQ0-bound, and preQ1-bound states
- **SAM-III riboswitch:** apo, SAM-bound, SAH-bound, and EEM-bound states

The repository is intended to provide the inputs, processed data, analysis code, trajectory-derived observables, and figure-generation resources needed to reproduce the principal computational results of the manuscript.

## Graphical Workflow

```mermaid
flowchart LR
    A[PDB structures] --> B[System preparation]
    B --> C[Energy minimization]
    C --> D[NVT / NPT]
    D --> E[MD]
    D --> F[PaCS-MD]

    E --> G[RMSD / PCA / bound-state interactions]
    F --> H[20 independent dissociation trials]
    H --> I[MSM construction]
    I --> J[PMF and ΔG estimation]

    H --> K[3D pathway mapping]
    H --> L[Ligand-RNA interaction analysis]

    G --> M[Dynamic ligand discrimination]
    J --> M
    K --> M
    L --> M
```

## Molecular Systems

### preQ1 riboswitch

| System               | PDB ID | Ligand / PDB ligand code | Purpose                  |
| -------------------- | -----: | ------------------------ | ------------------------ |
| Apo preQ1 riboswitch | `6VUH` | —                        | Ligand-free reference    |
| preQ0-bound          | `3GCA` | preQ0                    | Related precursor ligand |
| preQ1-bound          | `3Q50` | preQ1                    | Native ligand            |


### SAM-III riboswitch

| System      |              PDB ID | Ligand | Purpose                     |
| ----------- | ------------------: | ------ | --------------------------- |
| Apo SAM-III | derived from `3E5C` | —      | Ligand-free reference       |
| SAM-bound   |              `3E5C` | SAM    | Native ligand               |
| SAH-bound   |              `3E5E` | SAH    | Demethylated related ligand |
| EEM-bound   |              `3E5F` | EEM    | SAM-related analogue        |

> **Note:** the SAM-III apo structure is a ligand-removed model derived from the SAM-bound experimental structure.

## Main Findings

### 1. preQ1 riboswitch

- Conventional MD indicated that ligand binding restricts the conformational space of the RNA relative to the apo state.
- preQ0 predominantly maintained one stable ligand pose, whereas preQ1 sampled two bound conformations associated with different hydrogen-bonding patterns.
- In 20 independent PaCS-MD trials:
  - **preQ0:** mean dissociation requirement = **52.5 cycles**
  - **preQ1:** mean dissociation requirement = **93.3 cycles**
- MSM-based estimates of standard binding free energy:
  - **preQ0:** **−26.3 ± 7.4 kJ mol⁻¹**
  - **preQ1:** **−32.8 ± 6.1 kJ mol⁻¹**
- Both ligands sampled two major spatial release routes, but their **dominant dissociation directions differed strongly**.
- The pathway preference was associated primarily with:
  - **π–π stacking:** U12 and A29
  - **van der Waals contacts:** C16 and C30

<p align="center">
  <img src="assets/preQ1.jpg" width="95%" alt="preQ1 riboswitch dissociation pathways and ligand-RNA interactions">
</p>


<p align="center"><em>Representative spatial dissociation pathways and interaction features for preQ0 and preQ1.</em></p>

### 2. SAM-III riboswitch

- SAM, SAH, and EEM displayed ligand-dependent retention and release behavior.
- In 20 independent PaCS-MD trials per ligand:
  - **SAM:** **47.9 cycles**
  - **SAH:** **36.1 cycles**
  - **EEM:** **39.3 cycles**
- MSM-based free-energy estimates:
  - **SAM:** **−30.5 ± 7.6 kJ mol⁻¹**
  - **SAH:** **−28.6 ± 15.4 kJ mol⁻¹**
  - **EEM:** **−31.5 ± 12.3 kJ mol⁻¹**
- Spatial pathway mapping showed:
  - **SAM and EEM:** two major lateral release pathways
  - **SAH:** a more localized frontal release pathway
- These differences were associated mainly with:
  - **hydrogen bonds:** A28 and A38
  - **van der Waals contacts:** A28 and G35
- π–π stacking was comparatively rare during SAM-III ligand dissociation.

<p align="center">
  <img src="assets/SAM-III.jpg" width="95%" alt="SAM-III riboswitch dissociation pathways and ligand-RNA interactions">
</p>


<p align="center"><em>Representative spatial dissociation behavior and interaction features for SAM, SAH, and EEM.</em></p>


## Computational Protocol

### System preparation

The simulations were prepared using an AMBER-based parameterization workflow and subsequently run in GROMACS.

| Component              | Setting             |
| ---------------------- | ------------------- |
| RNA force field        | AMBER RNA.OL3       |
| Ligand force field     | GAFF2               |
| Ligand charges         | RESP                |
| Solvent model          | OPC water           |
| Salt concentration     | 0.10 M KCl          |
| Temperature            | 303.15 K            |
| Pressure               | 1 bar               |
| preQ1 simulation box   | cubic, 7.8 nm edge  |
| SAM-III simulation box | cubic, 15.0 nm edge |

Ligand preparation involved Avogadro, Gaussian/RESP calculations, Antechamber, Parmchk2, and LEaP before conversion to GROMACS-compatible topology files.

## PaCS-MD Settings

The progress coordinate used for production PaCS-MD was the **ligand displacement from its initial bound position after fitting the RNA structure**.

The original ligand–pocket center-of-mass distance was tested but was unsuitable because the U-shaped RNA binding pocket allowed the ligand to increase this distance without necessarily escaping into bulk solvent.

```yaml
PaCS-MD:
  replicas_per_cycle: 64
  segment_length_ps: 100
  independent_trials_per_ligand: 20
  progress_coordinate:
    type: ligand_displacement_from_initial_bound_position
    alignment: fit_RNA_before_measurement
  dissociation_threshold_nm: 5.0
  maximum_cycles: 200
```

## MSM and Free-Energy Analysis

Ligand dissociation trajectories were represented primarily using the ligand–RNA distance coordinate and clustered by K-means. MSMs were estimated using reversible maximum likelihood.

```yaml
MSM:
  clustering:
    method: k_means
    tested_n_clusters: [100, 80, 60, 40, 20]

  preQ1:
    final_n_clusters: 20
    lag_frames: 20
    lag_time_ps: 10

  SAM-III:
    final_n_clusters: 20
    lag_frames: 40
    lag_time_ps: 20

  diagnostics:
    - implied_timescales

  free_energy:
    observable: PMF
    source: stationary_distribution
    standard_state_correction: volume_correction
```

The standard-state binding free-energy estimate includes a translational volume correction based on the accessible unbound ligand volume.


## Ligand–RNA Interaction Definitions

Three classes of interactions were analyzed along the dissociation coordinate.

```python
interaction_definition = {
    "hydrogen_bond": {
        "algorithm": "Baker-Hubbard",
        "donor_acceptor_cutoff_nm": 0.30,
        "angle_cutoff_deg": 120
    },
    "van_der_Waals_contact": {
        "interatomic_distance_cutoff_nm": 0.30
    },
    "pi_pi_stacking": {
        "aromatic_center_distance_cutoff_nm": 0.50
    }
}
```

Interaction counts were normalized by the number of frames within each ligand–RNA distance bin so that contact persistence could be compared as dissociation progressed.


## Software Used

The computational workflow used the following tools:

- **GROMACS** — molecular dynamics
- **AMBER / AmberTools**
  - Antechamber
  - Parmchk2
  - LEaP
- **GAFF2** — ligand force-field parameters
- **Gaussian** — electrostatic calculations for RESP fitting
- **Avogadro** — ligand preparation / geometry handling
- **Python**
- **deeptime** — Markov state model construction
- **scikit-learn** — K-means clustering
- **MDTraj** — trajectory and hydrogen-bond analysis
- **MDAnalysis** — trajectory processing and ligand COM extraction
- **ChimeraX** — three-dimensional pathway visualization

> Exact software versions should be recorded in `environment/versions.txt` or an equivalent environment file before archival release.



## Reproducing the Analysis

### 1. Clone the repository

```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/<REPOSITORY_NAME>.git
cd <REPOSITORY_NAME>
```

### 2. Create the analysis environment

If a Conda environment file is provided:

```bash
conda env create -f environment/environment.yml
conda activate riboswitch-pacsmd
```

or, using `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r environment/requirements.txt
```


## Data Availability

Simulation input files, analysis scripts, and figure-source data supporting the findings of this study are publicly available in this GitHub repository. Large raw molecular-dynamics and PaCS-MD trajectory files are available upon reasonable request from the corresponding author.

## Contact

**Yilan Bai** Graduate School of Life Science and Technology, Institute of Science Tokyo bai.y.2355@m.isct.ac.jp

For questions about the repository, please use the GitHub **Issues** page or contact the corresponding author listed in the manuscript.

## Acknowledgments

This repository supports computational research performed in the **Kitao Laboratory, Institute of Science Tokyo** under the supervision of **Prof. Akio Kitao**.
