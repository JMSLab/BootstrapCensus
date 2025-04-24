## BootstrapCensus

This repository contains data from a census of papers published in the *American Economic Review* in 2021 that use a bootstrap. For each paper, we provide CSV files—sourced from replication packages or directly from authors—that include either full bootstrap replicates or reported summary statistics (point estimates and standard errors) for key empirical objects. The data allows for comparison between conventional reported summaries and the underlying bootstrap distributions.

This repository is based on [JMSLab/Template](https://github.com/JMSLab/Template/tree/e1fccecbf3b9dfc1c2479912cf3315cb9e6f9fe5), which contains documentation on prerequisites, repository structure, and procedure to rebuild objects. 

Before running `scons` in this repository, do `export PYTHONPATH=.`.

### Repository Structure

- `datastore/raw`: bootstrap replicates and replication archives for each paper in census
- `source/`
  - `raw/`: metadata on papers and their objects of interest
  - `lib/`: software requirements and helper functions
  - `derived/`: code for each paper
- `output/`: estimates and replicates for each paper's objects of interest

For details, see [JMSLab/Template](https://github.com/JMSLab/Template/tree/e1fccecbf3b9dfc1c2479912cf3315cb9e6f9fe5).

### Citations

* Andrews, Isaiah, and Jesse M. Shapiro. 2025. "BootstrapCensus". Code and data repository at <https://github.com/JMSLab/LaroplanOCR>.
* Andrews, Isaiah, and Jesse M. Shapiro. 2025. “Communicating Scientific Uncertainty via Approximate Posteriors.” NBER Working Paper Series No. 32038. National Bureau of Economic Research, January. https://doi.org/10.3386/w32038. Available at http://www.nber.org/papers/w32038

### Acknowledgments

We thank our dedicated research assistants for contributions to this project.
