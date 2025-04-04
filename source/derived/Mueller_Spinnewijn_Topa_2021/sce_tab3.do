clear
global clear
clear matrix

global indir "temp/MST2021/MST/EMPIRICAL_ANALYSIS/Codes_and_Data/SCE"
global temp "temp"
global outdir "output/derived"

***************
*** Table 3 ***
***************

clear
clear matrix
set matsize 5000
set more off

* load data file
use "${indir}/sce_datafile.dta", clear
keep if age>=20 & age<=65
keep if in_sample_2==1

* convert 12-month proability into a 3-month proability
generate imputed_findjob_3mon = 1 - ((1-find_job_12mon)^.25)
replace find_job_12mon=imputed_findjob_3mon

* define unemployment duration bins
tab udur_bins, gen(ud_)
drop ud_1 

* define controls
gen agesq=age*age
global controls female hispanic black r_asoth other_race age agesq hhinc_2-hhinc_4 education_2-education_6

* set random seed
set seed 1

preserve

* moments for lower bounds
quietly corr UE_trans_3mon find_job_3mon [aw=weight], c
local varz=r(Var_2)
local covzt=r(cov_12)
quietly corr UE_trans_3mon find_job_12mon [aw=weight] if !mi(find_job_3mon), c
local covz12t=r(cov_12)
quietly corr find_job_3mon find_job_12mon [aw=weight] if !mi(find_job_3mon), c
local covzz12=r(cov_12)

quietly regress UE_trans_3mon $controls  [pw=weight] if !mi(find_job_3mon), robust
quietly predict UE_trans_3mon_pred1, xb
quietly corr UE_trans_3mon UE_trans_3mon_pred1 [aw=weight] if !mi(find_job_3mon), c
local varz_pred1=r(Var_2)

quietly regress UE_trans_3mon find_job_3mon find_job_12mon $controls  [pw=weight] if !mi(find_job_3mon), robust
quietly predict UE_trans_3mon_pred2, xb
quietly corr UE_trans_3mon UE_trans_3mon_pred2 [aw=weight] if !mi(find_job_3mon), c
local varz_pred2=r(Var_2)

* lower bounds 
local LB_z1  = (`covzt'^2)/`varz'
local LB_z12 = (`covz12t'*`covzt')/`covzz12'
local LB_pred1 = `varz_pred1'
local LB_pred2 = `varz_pred2'

mat RES = (0,`LB_z1',`LB_z12',`LB_pred1',`LB_pred2')
mat list RES
restore

****ADDED****
global LowerBoundVarJobFindingProb = RES[1,2]

* bootstrap for standard errors
forvalues bsi=1(1)2000 {
preserve
bsample, cluster(userid)
if round(`bsi'/100)==`bsi'/100 {
display "Bootstrap: `bsi'"
}
* moments for lower bounds
quietly corr UE_trans_3mon find_job_3mon [aw=weight], c
local varz=r(Var_2)
local covzt=r(cov_12)
quietly corr UE_trans_3mon find_job_12mon [aw=weight] if !mi(find_job_3mon), c
local covz12t=r(cov_12)
quietly corr find_job_3mon find_job_12mon [aw=weight] if !mi(find_job_3mon), c
local covzz12=r(cov_12)

quietly regress UE_trans_3mon $controls  [pw=weight] if !mi(find_job_3mon), robust
quietly predict UE_trans_3mon_pred1, xb
quietly corr UE_trans_3mon UE_trans_3mon_pred1 [aw=weight] if !mi(find_job_3mon), c
local varz_pred1=r(Var_2)

quietly regress UE_trans_3mon find_job_3mon find_job_12mon $controls  [pw=weight] if !mi(find_job_3mon), robust
quietly predict UE_trans_3mon_pred2, xb
quietly corr UE_trans_3mon UE_trans_3mon_pred2 [aw=weight] if !mi(find_job_3mon), c
local varz_pred2=r(Var_2)

* lower bounds 
local LB_z1  = (`covzt'^2)/`varz'
local LB_z12 = (`covz12t'*`covzt')/`covzz12'
local LB_pred1 = `varz_pred1'
local LB_pred2 = `varz_pred2'

mat RES = (RES\ `bsi',`LB_z1',`LB_z12',`LB_pred1',`LB_pred2')

restore
}

****ADDED****
mat LowerBoundVarJobFindingProb_repl = RES[2...,2]

clear
svmat LowerBoundVarJobFindingProb_repl, names(replicate_value)
rename replicate_value1 replicate_value
su replicate_value
global LowerBoundVarJobFindingProb_s = `r(sd)'
gen replicate_number = _n
gen object = "LowerBoundVarJobFindingProb"
save "${temp}/Mueller_Spinnewijn_Topa_2021_Replicates.dta",replace

clear
set obs 1
generate str object = "LowerBoundVarJobFindingProb" in 1

generate estimate = $LowerBoundVarJobFindingProb in 1

generate std_err = $LowerBoundVarJobFindingProb_s in 1

save "${temp}/Mueller_Spinnewijn_Topa_2021_Estimates.dta",replace

clear matrix

************************************
*** Combine with Matlab datasets ***
************************************
import delimited "${temp}/est_mat_MST2021.csv", clear 
rename (v1 v2 v3) (object estimate std_err)
append using "${temp}/Mueller_Spinnewijn_Topa_2021_Estimates.dta"
replace estimate = round(estimate,0.00000001)
replace std_err = round(std_err,0.00000001)
save_data "${outdir}/Mueller_Spinnewijn_Topa_2021_Estimates.csv", key(object) outsheet ///
log("${outdir}/Mueller_Spinnewijn_Topa_2021_Estimates.log") delim(",") log_replace replace

import delimited "${temp}/repl_mat_MST2021.csv", clear 
rename (v1 v2 v3) (object replicate_value replicate_number)
append using "${temp}/Mueller_Spinnewijn_Topa_2021_Replicates.dta"
replace replicate_value = round(replicate_value,0.00000001)
save_data "${outdir}/Mueller_Spinnewijn_Topa_2021_Replicates.csv", key(object replicate_number) outsheet ///
log("${outdir}/Mueller_Spinnewijn_Topa_2021_Replicates.log") delim(",") log_replace replace



