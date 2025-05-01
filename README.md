## BootstrapCensus

This repository contains data from a census of papers published in the *American Economic Review* in 2021 that use a bootstrap, as described in Andrews and Shapiro (2025b).

For each paper, the directory [`output/derived`](./output/derived) includes two `CSV` files:
* `NAME_Estimates.csv` contains the authors' original point estimates, bootstrap standard errors and (where reported) confidence intervals for selected objects of interest
* `NAME_Replicates.csv` contains the bootstrap replicates for each object of interest

### Repository Structure

- [`datastore/raw`](https://drive.google.com/drive/u/1/folders/15cxte8q811VV3lv6Fz-zRUBdWrTshkul): original information (bootstrap replicates, replication archives, and correspondence) for each paper in census
- `source/`
  - `raw/`: metadata on papers and their objects of interest
  - `derived/`: code for each paper
- `output/`: estimates and replicates for each paper's objects of interest

The structure and requirements of the repository follow [JMSLab/Template](https://github.com/JMSLab/Template/tree/e1fccecbf3b9dfc1c2479912cf3315cb9e6f9fe5). If you wish to run the code in the repository, please see the documentation there.

### Citations

If using the census in published work, please cite the following:
* Andrews, Isaiah, and Jesse M. Shapiro. 2025a. "BootstrapCensus". Code and data repository at <https://github.com/JMSLab/BootstrapCensus>.
* Andrews, Isaiah, and Jesse M. Shapiro. 2025b. “Communicating Scientific Uncertainty via Approximate Posteriors.” NBER Working Paper Series No. 32038. https://doi.org/10.3386/w32038.

### Acknowledgments

We thank our dedicated research assistants for contributions to this project.
