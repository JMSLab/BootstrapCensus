## Overview

The files `objects_of_interest.csv` and `papers.csv` contain details about objects of interest in economics articles for which a bootstrap was performed.

In `objects_of_interest.csv`, each row corresponds to a paper-object of interest pair. We focus on primary objects of interest, which we define to be objects for which a quantitative or a qualitative description appears in the abstract or the introduction of paper. In cases where there are multiple estimates for a given object of interest, we focus on the main one, e.g., on the estimate from the baseline specification rather than the ones from additional specifications used in sensitivity analysis.

In `papers.csv`, each row corresponds to a paper.

The files are linked through the `citation` column which serves as the key in `papers` and a foreign key in `objects_of_interest`.

## Sampling Frame

We attempted to collect information from all economics articles published in the _American Economic Review_ in 2021. 

We identified these articles using a [Google scholar query](https://scholar.google.com/scholar?q=bootstrap+source%3AAmerican+source%3AEconomic+source%3AReview+&hl=en&as_sdt=0%2C10&as_ylo=2021&as_yhi=2021).

We excluded papers that are primarily methodological or that use a bootstrap only to calculate a p-value.

## Description of the columns of `objects_of_interest`

| Field | Description | Example |
| ----- | ----------- | ------- |
| citation | Short identifier for the paper containing the surnames of the authors and the year of publication. | ReimersWaldfogel2021 |
| shortname_object | A short name we use for identifying the object of interest. | PercentageIncreaseAfterNYTReview |
| description_object | A longer description of the object of interest. | The percentage increase in sales during the first five days following a NYT review |
| object_in_abstract | A binary indicator for whether the object appears in the paper's abstract. | 0 |
| page_obj_mentioned_intro | Page where the object of interest was mentioned in the introduction. | 1946 |
| estimate | Estimate for the object of interest. |  0.438 |
| estimate_page | Page where the estimate is given. | 1959 |
| estimate_table | Table where the estimate for the object appears. | 3 |
| estimate_figure | Figure where the estimate for the object appears. | |
| bootstrap_se | Bootstrap standard errors for the object of interest, if given. | 0.061 |
| bootstrap_se_page | Page where the bootstrap standard error is given. | 1959 | 
| other_bootstrapped_statistic | Description of the other bootstrapped (e.g. CI) statistic, if any. | |
| type_of_bootstrap | Type of bootstrap (parametric, Bayesian, etc.). | Parametric |
| description_of_statistic_bootstrapped | Description of the statistic bootstrapped if it is not the point estimate (e.g., t-statistic). | |
| model_type | Type of the model (e.g. linear or nonlinear). | nonlinear |
| model_page | Page where the model type is given. | 1958 |
| parameter_type | Type of the parameter (e.g. a (non)linear function of estimated parameters). | nonlinear function of estimated parameters |
| parameter_type_page | Page where the parameter type is given. | 1958 |
| domain_obj_interest | Domain of the object of interest (e.g. real line). | reals |
| why_bootstrap | Explanation given for the use of bootstrap. | |
| why_bootstrap_page | Page where the explanation for the use of bootstrap is given. | |
| n_replicates | Number of bootstrap replicates. | 500 |
| cluster_of_bootstrap | Over what unit bootstrap is clustered. | Firm |
| source_cluser | Page or program where clustering is indicated. | 3816 |
| location_within_archive | The location of the bootstrap estimates within the replication archive. | |
| can_produce_replicates | Whether the bootstrap replicates can be reproduced using the code and the data in the archive (Y = yes, N = no, R = no but obtained from authors, X = deliberately excluded) | Y |
| notes | Additional remarks. | To obtain the percentage estimate in the introduction (0.55), one needs to apply the transformation e^x - 1 where x is the estimate reported here. |

## Description of the columns of `papers`

| Field | Description | Example |
| ----- | ----------- | ------- |
| citation | Short identifier for the paper containing the surnames of the authors and the year of publication. | ReimersWaldfogel2021 |
| journal | Abbreviation of the academic journal where the paper was published. | AER |
| year | Year of publication. | 2021 |
| doi | DOI link. | https://doi.org/10.1257/aer.20200153 |
| title | Title of paper. | Digitization and Pre-Purchase Information |
| location_of_replication_archive | Where the replication archive can be found. | [OpenICPSR](https://www.openicpsr.org/openicpsr/project/130802/version/V1/view) |
| replicate_search_time | Time spent searching for/reproducing bootstrap replicates in hours | 3.5 |
| date_received | Date when authors sent replicates (blank if not asked, N if could not send, X if decided to exclude) | 04/26/2022
| why_excluded | Why excluded from census | Bootstrap used only in appendix material
