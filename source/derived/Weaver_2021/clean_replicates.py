import pandas as pd
import numpy as np
import sys
sys.path.append('source/lib/JMSLab')
from SaveData import SaveData

def main():
    paper = 'Weaver_2021'
    indir = f'datastore/raw/bootstrap_census/{paper}/orig'
    indir_objects_of_int = 'source/raw/bootstrap_census/orig'
    outdir = 'output/derived/bootstrap_census'
    indir_precision = 'source/derived/bootstrap_census'

    n_digits = pd.read_csv(f'{indir_precision}/digits_after_comma_precision.txt',
                           header = None)[0][0]
    df_OOI = pd.read_csv(f'{indir_objects_of_int}/objects_of_interest.csv')
    df_OOI = df_OOI[df_OOI['citation'] == paper]
    
    df_replicates = PrepareReplicatesDf(indir, n_digits)
    df_estimates = PrepareEstimatesDf(df_OOI, df_replicates, n_digits)

    IntegrityCheck(df_replicates, df_OOI)

    SaveData(df_replicates,
             keys     = ['object', 'replicate_number'],
             out_file = f'{outdir}/{paper}_Replicates.csv',
             log_file = f'{outdir}/{paper}_Replicates.log')
    
    SaveData(df_estimates,
             keys     = ['object'],
             out_file = f'{outdir}/{paper}_Estimates.csv',
             log_file = f'{outdir}/{paper}_Estimates.log')
    
def PrepareReplicatesDf(indir, n):
    '''
    opens the raw replicate files stored in indir
    and outputs the replicates for the objects
    of interest

    Parameters
    ----------
    indir: str
        The director where bootstraps_table#.csv
        is stored
    n: int
        Number of digits to round the replicates to
    
    Returns
    -------
    df_replicates: dataframe
        Replicates dataframe in the form:
        object      replicate_number        replicate_value
        name        #                       ####
    '''
    df_replicates = pd.DataFrame(np.empty((0, 3)), columns = ['object', 'replicate_number', 'replicate_value'])
    df_figure3_raw = pd.read_excel(f'{indir}/bootstrap_coefs.xlsx', 'figure3')
    df_table4_raw = pd.read_excel(f'{indir}/bootstrap_coefs.xlsx', 'table4')
    figure3_objects = {'HealthObsAppUB': 'ub1', 'HealthAllAppUB': 'ub2', 'HealthEndogInUB': 'ub3', 
                      'HealthStatedUB': 'ub4', 'GvmntObsAppUB': 'ub5', 'GvmntAllAppUB': 'ub6', 'GvmntEndogAppUB': 'ub7'}
    table4_objects = {'WealthSPI': 'column1', 'WealthFunc': 'column2', 'WealthInstDeliv': 'column3',
                      'WealthNewCheck': 'column4', 'WealthNutCoun': 'column5', 'WealthDots': 'column6'}

    for object in figure3_objects:
        df_object = pd.DataFrame(np.empty((0, 3)), columns = ['object', 'replicate_number', 'replicate_value'])
        raw_vals = df_figure3_raw[figure3_objects[object]].values
        replicate_vals = raw_vals[~np.isnan(raw_vals)]
        num_replicates = replicate_vals.size
        
        df_object['replicate_value'] = replicate_vals
        df_object['object'] = np.array([object for replicate in range(num_replicates)])
        df_object['replicate_number'] = np.linspace(1, num_replicates, num_replicates)
        df_replicates = pd.concat([df_replicates, df_object], ignore_index = True)

    for object in table4_objects:
        df_object = pd.DataFrame(np.empty((0, 3)), columns = ['object', 'replicate_number', 'replicate_value'])
        raw_vals = df_table4_raw[table4_objects[object]].values
        replicate_vals = raw_vals[~np.isnan(raw_vals)]
        num_replicates = replicate_vals.size

        df_object['replicate_value'] = replicate_vals
        df_object['object'] = np.array([object for replicate in range(num_replicates)])
        df_object['replicate_number'] = np.linspace(1, num_replicates, num_replicates)
        df_replicates = pd.concat([df_replicates, df_object], ignore_index = True)

    df_replicates['replicate_number'] = np.int32(df_replicates['replicate_number'])
    df_replicates['replicate_value'] = np.around(df_replicates['replicate_value'].values, n)

    return df_replicates

def PrepareEstimatesDf(df_OOI, df_replicates, n):
    '''
    takes the mean and standard deviation of each
    object in df_replicates

    Parameters
    ----------
    df_OOI: dataframe
        Dataframe containing table values from 
        objects_of_interest.csv
    df_replicates: dataframe
        Dataframe containing the replicates for
        each object to calculate std_err
    n: int
        Number of digits to round the std_err to
    
    Returns
    -------
    df_estimates: dataframe
        Replicates dataframe in the form:
        object      estimate        std_err
        name        #               ####
    '''
    df_estimates = pd.DataFrame(np.empty((0, 3)), columns = ['object', 'estimate', 'std_err'])
    
    for object in df_OOI['shortname_object'].values:
        df_object = pd.DataFrame(np.empty((0, 3)), columns = ['object', 'estimate', 'std_err'])
        replicates = df_replicates.loc[df_replicates['object'] == object, 'replicate_value'].values
        df_object['object'] = [object]
        df_object['estimate'] = df_OOI.loc[df_OOI['shortname_object'] == object, 'estimate'].values
        df_object['std_err'] = np.std(replicates, ddof = 1)
        df_estimates = pd.concat([df_estimates, df_object], ignore_index = True)

    df_estimates['std_err'] = np.around(df_estimates['std_err'].values, n)
    return df_estimates
    
def IntegrityCheck(df_replicates, df_OOI):
    '''
    asserts that the derived estimates are
    equal to those given in the table

    Parameters
    ----------
    df_replicates: dataframe
        A dataframe storing each object and its replicate
        values
    df_OOI: dataframe
        Dataframe containing table values from 
        objects_of_interest.csv
    '''
    table4_objects = ('WealthSPI', 'WealthFunc', 'WealthInstDeliv',
                      'WealthNewCheck', 'WealthNutCoun', 'WealthDots')
    # 97.5 quantile collected with WebPlotDigitizer
    figure3_CI = {'HealthObsAppUB': 0.892, 'HealthAllAppUB': 0.891, 'HealthEndogInUB': 0.901, 
                      'HealthStatedUB': 0.869, 'GvmntObsAppUB': 0.934, 'GvmntAllAppUB': 0.942, 'GvmntEndogAppUB': 0.937}
    
    # Check 97.5th quantile for figure 3 are close to reported quantile
    for object in figure3_CI:
        replicates = df_replicates.loc[df_replicates['object'] == object, 'replicate_value']
        quantile_975 = np.quantile(replicates, 0.975, method = 'higher')
        reported_975 = figure3_CI[object]
        assert abs(quantile_975 - reported_975) < 0.01
    
    # Check standard errors for table 4 match replicate errors
    for object in table4_objects:
        replicates = df_replicates.loc[df_replicates['object'] == object, 'replicate_value']
        replicate_std_err = np.std(replicates, ddof = 1)
        report_std_err = df_OOI.loc[df_OOI['shortname_object'] == object, 'bootstrap_se'].values
        assert abs(replicate_std_err - report_std_err) < 0.01

main()
