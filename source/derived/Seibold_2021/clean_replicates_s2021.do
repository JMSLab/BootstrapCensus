set more off
preliminaries

program main
	local indir "datastore/raw/bootstrap_census/Seibold_2021/orig"
	local temp  "temp"
	local outdir "output/derived/bootstrap_census"
	
	build_replicates, filename("table4_1") object("KinkSize") var("eps5") avg(".050") indir(`indir') temp(`temp') append(0)
	build_replicates, filename("table4_1") object("EarlyRetirementAge") var("coeff_era5") avg(".051") indir(`indir') temp(`temp') append(1)
	build_replicates, filename("table4_1") object("FullRetirementAge") var("coeff_nra5") avg(".072") indir(`indir') temp(`temp') append(1)
	build_replicates, filename("table4_1") object("NormalRetirementAge") var("coeff_sra5") avg(".218") indir(`indir') temp(`temp') append(1)
	
	use "`temp'/Seibold_2021_Replicates.dta"
	save_data "`outdir'/Seibold_2021_Replicates.csv", key(object replicate_number) outsheet ///
	log("`outdir'/Seibold_2021_Replicates.log") delim(",") log_replace replace

	clear
	build_estimates, outdir(`outdir')

end


program build_replicates
	syntax, filename(str) object(str) var(str) avg(str) indir(str) temp(str) append(int)
	
	use "`indir'/`filename'", clear
	
	keep `var'
	rename `var' replicate_value
	gen replicate_number = _n
	gen object = "`object'"
	su replicate_value
	local mean = `avg'
	local sd = `r(sd)'

	if `append' {
		matrix row = `mean' , `sd'
		matrix mat = mat \ row
		append using "`temp'/Seibold_2021_Replicates.dta"
	} 
	else{
		matrix mat = `mean' , `sd'
	}
	
	save "`temp'/Seibold_2021_Replicates.dta", replace

end

program build_estimates
	syntax, outdir(str)

	svmat mat
	generate str object = "KinkSize" in 1
	replace object = "EarlyRetirementAge" in 2
	replace object = "FullRetirementAge" in 3
	replace object = "NormalRetirementAge" in 4
	rename (mat1 mat2) (estimate std_err)
	save_data "`outdir'/Seibold_2021_Estimates.csv", key(object) outsheet ///
	log("`outdir'/Seibold_2021_Estimates.log") delim(",") log_replace replace

end

*EXECUTE
main

