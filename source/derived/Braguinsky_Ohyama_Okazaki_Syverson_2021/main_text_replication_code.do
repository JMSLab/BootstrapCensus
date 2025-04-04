clear
global clear
clear matrix
set more off

program main
	local indir "temp/BOOS2021"
    local temp "temp"
    local outdir "output/derived/bootstrap_census"
	local rawdir "datastore/raw/bootstrap_census/Braguinsky_Ohyama_Okazaki_Syverson_2021/orig"

    capture erase "`temp'/BOOS2021/replicates.dta"
    copy "`rawdir'/BOOS2021.zip" "`temp'/BOOS2021.zip", replace
    cd "`temp'"
    unzipfile "BOOS2021.zip", replace
    cd ..

    extract_data, filename("Final-data-and-programs/main_data.dta") indir(`indir') temp(`temp')

end

program extract_data
	syntax, filename(str) indir(str) temp(str)
    use "`indir'/`filename'", clear

    tsset firmID year_half_year

    *** Dropping observations without the data on machines

    drop if low_end_timeline==.
    drop if num_spindles_t==.

    *** Generating some more required variables:

    *** Firm capacity and its change

    gen log_capacity_total=ln(firm_capacity_total)
    by firmID: gen dlog_capacity_total=log_capacity_total-log_capacity_total[_n-1]


    *** Continuous high-end and low-end capacity change
    drop log_high_end_cap log_low_end_cap
    gen log_high_end_cap=ln(high_end_cap+sqrt(1+high_end_cap^2))
    gen log_low_end_cap=ln(low_end_cap+sqrt(1+low_end_cap^2))
    by firmID: gen dlog_high_end_cap=log_high_end_cap[_n+1]-log_high_end_cap
    by firmID: gen dlog_low_end_cap=log_low_end_cap[_n+1]-log_low_end_cap


    *** High-end and low-end product numbers

    foreach var of varlist right1_semi-gassed5_semi {
    replace `var'=. if `var'==0
    }

    egen num_low_prod=rownonmiss(right1_semi-right6_semi left1_semi-left6_semi doubled1_semi-doubled6_semi gassed1_semi)
    egen num_high_prod=rownonmiss(right7_semi-right10_semi left7_semi-left10_semi doubled7_semi-doubled10_semi gassed2_semi-gassed5_semi)

    *** Fraction of low-end (diversified) products in the total # of products
    gen fr_low_prod=num_low_prod/(num_low_prod + num_high_prod)

    *** Cumulative upgrade trials interacted with the fraction of low-end (diversified) products in the total # of products

    gen upgrade_exper_low_pr = num_exper_upgrades_st_cum*fr_low_prod


    *** Continuous measure of relative mandated output quotas (sotan) on low-end products 
    gen sotan_c=0
    replace sotan_c=4/30*(2/6) if year_half_year==19001
    replace sotan_c=4/30*(1/6)+0.4*(5/6) if year_half_year==19002
    replace sotan_c=0.4*(3/6) if year_half_year==19011

    replace sotan_c=5/30*(4/6)+0.275*(2/6) if year_half_year==19081
    replace sotan_c=0.275 if year_half_year==19082
    replace sotan_c=0.275 if year_half_year==19091
    replace sotan_c=0.275*(4/6)+0.2*(2/6) if year_half_year==19092
    replace sotan_c=0.2*(4/6) if year_half_year==19101
    
    replace sotan_c=0.075*(3/6) if year_half_year==19102

    replace sotan_c=0.075 if year_half_year==19111
        replace sotan_c=0.075*(3/6)+0.175*(3/6) if year_half_year==19112

        replace sotan_c=0.175*(3/6) if year_half_year==19121

        *** Repeating panel regression and generating the estimation sample 
    quietly: xtreg dlog_firm_total   num_exper_upgrades_st_cum  fr_low_prod  upgrade_exper_low_pr u_eng_dummy  merchant_d  dlog_high_end_cap dlog_low_end_cap log_firm_total  firm_age i.year_half_year  if ind~=1 & last1_obs==0&last_obs==0&year_half_year>=18932 & gap==0, fe robust
    gen est_inc=e(sample)

        **************************************
    **** &&&& Table 5, column (4) **** &&&&
    *** Note: output file generated in Excel by outreg2 command

    *** Constructing the IV: predicted cumulative upgrade trials from the first-stage regression

    quietly: poisson num_exper_upgrades_st  c.sotan_c#c.dlog_high_end_cap fr_low_prod u_eng_dummy merchant_d   dlog_high_end_cap dlog_low_end_cap log_firm_total firm_age i.year_half_year  if  est_inc==1 , robust cluster(firmID) nolog

    predict num_exper_upgrades_st_hat if e(sample)
    by firmID: gen num_exper_upgrades_st_cum_hat=sum(num_exper_upgrades_st_hat)

    *** Instrumented interaction term: Predicted cumulative upgrade trials interacted with the fraction of low-end (diversified) products in the total # of products
    gen upgrade_exper_low_hat = num_exper_upgrades_st_cum_hat*fr_low_prod

    * Second stage regression
    reg dlog_firm_total num_exper_upgrades_st_cum_hat   fr_low_prod upgrade_exper_low_hat u_eng_dummy  merchant_d   dlog_high_end_cap dlog_low_end_cap   log_firm_total  firm_age i.year_half_year  if  est_inc==1, mse1
    gen se_inc=e(sample)
    local R2_2 : display %5.3f `e(r2)'
    local N_2 : display %5.0f `e(N)'

    **** bootstrapping standard errors *******
    xtset, clear
    xtset firmID
    gen  newid = firmID
    tsset newid year_half_year
    keep if est_inc

    *** NOTE: depending on your computer it may take some time (20 minutes or more) to complete the following command
    adopath ++ source/derived/bootstrap_census/Braguinsky_Ohyama_Okazaki_Syverson_2021
    set rmsg on

*** using modified ADO file to correct error in original replication code

    bootstrap _b _se, saving("`indir'/replicates.dta") reps(1000) seed(197406) nodots cluster(firmID) idcluster(newid) nowarn: boos_2sls_2_modified
    set rmsg off

    display "R_squared = " `R2_2' _newline "Observations = " `N_2'

    outreg2  using "`indir'/estimates.xls" ///
    ,keep ( num_exper_upgrades_st_cum_hat   fr_low_prod upgrade_exper_low_hat  dlog_high_end_cap dlog_low_end_cap  u_eng_dummy  merchant_d   log_firm_total  firm_age ) ///
    se nolabel bdec(3) rdec(3) ctitle(4) alpha(0.01, 0.05, 0.1) symbol(***, **, *) addtext("Semiannual time dummies", "Included", "Observations", `N_2', "R_squared", `R2_2',  "Estimation", "IV") noobs onecol replace

    estat bootstrap
	matrix ci_bc = e(ci_bc)
	matrix ll = ci_bc["ll","b:upgrade_exper_low_hat"]
	matrix ul = ci_bc["ul","b:upgrade_exper_low_hat"]
	svmat ll
	svmat ul
	outsheet ll ul using `temp'/boos_ci_bc.csv, replace comma
end

*EXECUTE
main
