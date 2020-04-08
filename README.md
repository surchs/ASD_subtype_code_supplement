# Code supplement to the ASD subtype paper
This repository contains the code used to process and analyse the data presented in the "Subtypes of functional connectivity associate robustly with ASD diagnosis" paper. 

## Installation
Requirements
- [NIAK](http://niak.simexp-lab.org/build/html/index.html)
- `asdfc` (included in this repository)

The analysis scripts included in this repository make use of a number of custom python functions included in the `asdfc` package. This package does not have to be installed but is locally referenced. The best way to obtain the a working python environment for this project is to pull [the project's container image](https://hub.docker.com/r/surchs/abide_subtype): 
`docker pull surchs/abide_subtype`

All data in this project were preprocessed using the [NIAK toolkit](http://niak.simexp-lab.org/build/html/index.html). The [easiest way to obtain and run NIAK](http://niak.simexp-lab.org/build/html/INSTALLATION.html) is to download the most recent container image here: https://hub.docker.com/repository/docker/simexp/niak-cog

## Data acquisition
The easiest way to obtain the [ABIDE 1 and 2 datasets](http://fcon_1000.projects.nitrc.org/indi/abide/) is to download them directly from their AWS bucket at `s3://fcp-indi/data/Projects`. The [AWS command line interface](https://aws.amazon.com/cli/) is an easy way to do so:

e.g. for ABIDE 1
```
aws s3 sync s3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/ /path/to/ABIDE/RAW/LOCATION --no-sign-request
```

An alternative way is to directly download the data from the fcon_1000 repository, e.g. for ABIDE 2:
```
wget -r -np -nd -A tar.gz http://fcon_1000.projects.nitrc.org/indi/abide2/release/imaging_data
```
The phenotypic information for both datasets are also available at these locations.

Data for the [HNU1 dataset](http://fcon_1000.projects.nitrc.org/indi/CoRR/html/hnu_1.html) can be similarly obtained from the fcon_1000 repository (http://dx.doi.org/10.15387/fcp_indi.corr.hnu1).

## Data processing
The appropriate NIAK preprocessing scripts can be generated with the python scripts under `scripts/preprocessing` and then be run directly on the raw data.

The raw phenotypic data has to undergo a number of preprocessing steps to harmonize differences in scan site naming and missing value declarations. This can be achieved by running the scripts in `scripts/pheno` in the following order (for ABIDE 1 and 2 respectively):

1. `scripts/pheno/abide_1_prepare_pheno.py` to fix issues with the raw phenotypic information.
2. `scripts/pheno/abide_1_combine_pheno_and_motion.py` to merge the phenotypic data and information on in-scanner head motion generated during preprocessing of the imaging data with NIAK.
3. `scripts/pheno/abide_1_pheno_and_qc_rating.py` to merge the phenotypic and quality control information (optional).
4. `scripts/pheno/abide_1_psm_matching.R` to compute the propensity matching scores that are needed in order to balance the clinical and control group across sites.

All subsequent processing steps can be run on the preprocessed data and phenotypic information using the python scripts in the `scripts` directory.

1. `scripts/processing/abide_1_nuisance_regression.py` to regress nuisance covariates estimated by NIAK during the preprocessing from the preprocessed fMRI time series data.
2. `scripts/processing/abide_1_seed_maps.py` to compute seed to voxel functional connectivity estimates based on the [MIST_20 atlas](https://mniopenresearch.org/articles/1-3/v2).
3. `scripts/stability/abide_1_subtype_map_stability.py` and `abide_1_subtype_stability_core.py` to compute the stability of subtype maps and individual assignments respectively.
4. `scripts/subtyping/abide_1_subtyping_core.py` and `abide_1_weights_core.py` to compute subtypes and continuous assignments respectively.
5. `scripts/association/abide_1_association_categorical.py` to compute the association of the previously computed continuous assignment scores with categorical covariates from the phenotypic information.
6. `scripts/association/abide_2_association_categorical.py` to replicate the association findings on the independent validation sample (ABIDE 2).