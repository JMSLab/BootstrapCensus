clear
global clear
clear matrix
set more off

global indir "temp/ACO2021/code/matlab/results"
global temp "temp"
global outdir "output/derived/bootstrap_census"

set matsize 4500
set seed 1878499

*window manage forward results 
local rawdir "datastore/raw/bootstrap_census/Abebe_Caria_Ortiz-Ospina_2021/orig"
copy "`rawdir'/ACO2021.zip" "${temp}/ACO2021.zip", replace
cd ${temp}
unzipfile "ACO2021.zip", replace
cd ..

***************
*** Table 4 ***
***************

global count = 1

foreach m in 1 {

	insheet using "${indir}/Model1Version`m'_Parameters.csv"

	destring v6, replace force
	su v6 if _n==1
	global main_fit${count} = `r(mean)'


	rename v1 parameter
	keep parameter
	ge id = 1
	egen no =seq()
	reshape wide parameter, i(id) j(no)

	forvalues v =1(1)14{
		capture destring parameter`v', replace
	}

	replace parameter12 = parameter12 / (parameter6*parameter10)
	replace parameter13 = parameter13 / (parameter7*parameter11)

	forvalues v =1(1)14 {
		capture su parameter`v' 
		capture global m_${count}_`v'  = `r(mean)'
		//capture global m_${count}_`v' : di %4.3f ${m_${count}_`v'}
	}	
	clear
}

****ADDED****
global MeanApplicationCostLowB = $m_1_8
global MeanApplicationCostHighB = $m_1_9
global CorrApplCostAbilityLowB = $m_1_12
global CorrApplCostAbilityHighB = $m_1_13

clear
insheet using "${indir}/Model1Version1_Bootstrap.csv"


forvalues v=1(1)18 {
	rename v`v' parameter`v'	
}
keep parameter*
replace parameter12 = parameter12 / (parameter6*parameter10)
replace parameter13 = parameter13 / (parameter7*parameter11)
drop if parameter16 ==0
ge id = 1

****ADDED****
mkmat parameter8, matrix(MeanApplicationCostLowB_repl)
mkmat parameter9, matrix(MeanApplicationCostHighB_repl)
mkmat parameter12, matrix(CorrApplCostAbilityLowB_repl)
mkmat parameter13, matrix(CorrApplCostAbilityHighB_repl)

collapse (sd) parameter*, by(id)
drop id
forvalues v =1(1)13 {
	su parameter`v' 
	global s1_`v' = `r(mean)'
	//local `p' : di %4.2f `r(mean)'
	//global s1_`v'  = "\raisebox{.7ex}[1pt]{\footnotesize (`p')}"
}
clear

****ADDED****
global MeanApplicationCostLowB_s = $s1_8
global MeanApplicationCostHighB_s = $s1_9
global CorrApplCostAbilityLowB_s = $s1_12
global CorrApplCostAbilityHighB_s = $s1_13

***************
*** Table 5 ***
***************

clear

insheet using "${indir}/Model1Version1_Bootstrap.csv"

ge sim = _n
keep sim v15
rename v15 fit
tempfile file1
save `file1', replace

clear
insheet using "${indir}/BootIRR.csv"

drop if _n ==1

****ADDED****
replace v1 = v1 * 100
replace v3 = v3 * 100
mkmat v1, matrix(IRRallApplicants_repl)
mkmat v3, matrix(IRRallHires_repl)

foreach v in 1 3 {
	//replace v`v' = v`v' * 100
	capture su v`v' ,d
	local r5c`v'st_error = `r(sd)'
	//capture local r5c`v'st_error : di %4.1f `r(sd)'
}

***ADDED****
global IRRallApplicants_s = `r5c1st_error'
global IRRallHires_s = `r5c3st_error'

clear

insheet using "${indir}/CBA_main.csv"

foreach v in 1 2 3  {
	destring v`v', replace force
	foreach w in 1 2 3 4    {
		capture su v`v' if _n == `w'
		capture local r`w'c`v' = `r(mean)'
		//capture local r`w'c`v' : di %4.0f `r`w'c`v''
	}
	
	foreach w in  5  {
		capture su v`v' if _n == `w'
		capture local r`w'c`v' = `r(mean)'*100
		//capture local r`w'c`v' : di %4.1f `r`w'c`v''
	}
	
}

***ADDED****
global IRRallApplicants = `r5c1'
global IRRallHires = `r5c3'


* confidence intervals IRR
local r5c1ub = `r5c1' + (1.64 * `r5c1st_error')
//local r5c1ub : di %4.1f `r5c1ub'
local r5c1lb = `r5c1' - (1.64 * `r5c1st_error')
//local r5c1lb : di %4.1f `r5c1lb'

local r5c3ub = `r5c3' + (1.96 * `r5c3st_error')
//local r5c3ub : di %4.1f `r5c3ub'
local r5c3lb = `r5c3' - (1.96 * `r5c3st_error')
//local r5c3lb : di %4.1f `r5c3lb'

***ADDED****
global IRRallApplicants_lb = `r5c1lb'
global IRRallApplicants_ub = `r5c1ub'
global IRRallHires_lb = `r5c3lb'
global IRRallHires_ub = `r5c3ub'



clear
insheet using "${indir}/BootIRR_female.csv"
drop if _n ==1

***ADDED****
replace v1 = v1 * 100
mkmat v1, matrix(IRRfemale_repl)

foreach v in 1  {
	//replace v`v' = v`v' * 100
	capture su v`v' ,d
	//capture local g5c`v'st_error : di %4.1f `r(sd)'
	local g5c`v'st_error = `r(sd)'
}

***ADDED****
global IRRfemale_s = `g5c1st_error'

clear
insheet using "${indir}/CBA_female.csv"

foreach v in 1 {
	destring v`v', replace force
	foreach w in 1 2 3 4   {
		capture su v`v' if _n == `w'
		capture local g`w'c`v' = `r(mean)'
		//capture local g`w'c`v' : di %4.0f `g`w'c`v''
	}
	
	foreach w in  5  {
		capture su v`v' if _n == `w'
		capture local g`w'c`v' = `r(mean)'*100
		//capture local g`w'c`v' : di %4.1f `g`w'c`v''
	}
	
}
***ADDED****
global IRRfemale = `g5c1'

* confidence intervals IRR
local g5c1ub = `g5c1' + (1.64 * `g5c1st_error')
//local g5c1ub : di %4.1f `g5c1ub'
local g5c1lb = `g5c1' - (1.64 * `g5c1st_error')
//local g5c1lb : di %4.1f `g5c1lb'

***ADDED****
global IRRfemale_lb = `g5c1lb'
global IRRfemale_ub = `g5c1ub'


***********************
*** Generate output ***
***********************
*Estimates
clear
set obs 7
generate str object = "MeanApplicationCostLowB" in 1
replace object = "MeanApplicationCostHighB" in 2
replace object = "CorrApplCostAbilityLowB" in 3
replace object = "CorrApplCostAbilityHighB" in 4
replace object = "IRRallApplicants" in 5
replace object = "IRRallHires" in 6
replace object = "IRRfemale" in 7

generate estimate = $MeanApplicationCostLowB in 1
replace estimate = $MeanApplicationCostHighB in 2
replace estimate = $CorrApplCostAbilityLowB in 3
replace estimate = $CorrApplCostAbilityHighB in 4
replace estimate = $IRRallApplicants in 5
replace estimate = $IRRallHires in 6
replace estimate = $IRRfemale in 7

generate std_err = $MeanApplicationCostLowB_s in 1
replace std_err = $MeanApplicationCostHighB_s in 2
replace std_err = $CorrApplCostAbilityLowB_s in 3
replace std_err = $CorrApplCostAbilityHighB_s in 4
replace std_err = $IRRallApplicants_s in 5
replace std_err = $IRRallHires_s in 6
replace std_err = $IRRfemale_s in 7

generate lower_bound = $IRRallApplicants_lb in 5
replace lower_bound = $IRRallHires_lb in 6
replace lower_bound = $IRRfemale_lb in 7

generate upper_bound = $IRRallApplicants_ub in 5
replace upper_bound = $IRRallHires_ub in 6
replace upper_bound = $IRRfemale_ub in 7

replace estimate = round(estimate,0.00000001)
replace std_err = round(std_err,0.00000001)
replace lower_bound = round(lower_bound,0.00000001)
replace upper_bound = round(upper_bound,0.00000001)
save_data "${outdir}/Abebe_Caria_Ortiz-Ospina_2021_Estimates.csv", key(object) outsheet ///
log("${outdir}/Abebe_Caria_Ortiz-Ospina_2021_Estimates.log") delim(",") log_replace replace

*Replicates
clear
svmat MeanApplicationCostLowB_repl, names(replicate_value)
rename replicate_value1 replicate_value
gen replicate_number = _n
gen object = "MeanApplicationCostLowB"
save "${temp}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.dta",replace

clear
svmat MeanApplicationCostHighB_repl, names(replicate_value)
rename replicate_value1 replicate_value
gen replicate_number = _n
gen object = "MeanApplicationCostHighB"
append using "${temp}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.dta"
save "${temp}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.dta",replace

clear
svmat CorrApplCostAbilityLowB_repl, names(replicate_value)
rename replicate_value1 replicate_value
gen replicate_number = _n
gen object = "CorrApplCostAbilityLowB"
append using "${temp}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.dta"
save "${temp}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.dta",replace

clear
svmat CorrApplCostAbilityHighB_repl, names(replicate_value)
rename replicate_value1 replicate_value
gen replicate_number = _n
gen object = "CorrApplCostAbilityHighB"
append using "${temp}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.dta"
save "${temp}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.dta",replace

clear
svmat IRRallApplicants_repl, names(replicate_value)
rename replicate_value1 replicate_value
gen replicate_number = _n
gen object = "IRRallApplicants"
append using "${temp}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.dta"
save "${temp}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.dta",replace

clear
svmat IRRallHires_repl, names(replicate_value)
rename replicate_value1 replicate_value
gen replicate_number = _n
gen object = "IRRallHires"
append using "${temp}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.dta"
save "${temp}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.dta",replace

clear
svmat IRRfemale_repl, names(replicate_value)
rename replicate_value1 replicate_value
gen replicate_number = _n
gen object = "IRRfemale"
append using "${temp}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.dta"
replace replicate_value = round(replicate_value,0.00000001)
save_data "${outdir}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.csv", key(object replicate_number) outsheet ///
log("${outdir}/Abebe_Caria_Ortiz-Ospina_2021_Replicates.log") delim(",") log_replace replace


clear
macro drop _all
