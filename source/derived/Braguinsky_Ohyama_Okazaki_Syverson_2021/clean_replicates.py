import pandas as pd
import numpy as np
from source.lib.SaveData import SaveData

def main():
    paper = 'Braguinsky_Ohyama_Okazaki_Syverson_2021'
    indir = 'temp/BOOS2021'
    indir_objects_of_int = 'source/raw/orig'
    outdir = 'output/derived'
    indir_precision = 'source/derived'

    n_digits = pd.read_csv(f'{indir_precision}/digits_after_comma_precision.txt',
                           header = None)[0][0]
    df_OOI = pd.read_csv(f'{indir_objects_of_int}/objects_of_interest.csv')
    df_OOI = df_OOI[df_OOI['citation'] == paper]

    df_replicates = PrepareReplicatesDf(indir, n_digits)
    df_estimates = PrepareEstimatesDf(indir)
    IntegrityCheck(df_OOI, df_replicates, df_estimates)

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
        The director where the raw replicates are stored
    n: int
        Number of digits to round the replicates to
    
    Returns
    -------
    df_replicates: dataframe
        Replicates dataframe in the form:
        object      replicate_number        replicate_value
        name        #                       ####
    '''
    df_raw = pd.read_stata(f'{indir}/replicates.dta')
    df_replicates = pd.DataFrame(np.empty((0, 3)), columns = ['object', 'replicate_number', 'replicate_value'])
    objects_dir = {'UpgradesCum': '_b_num_exper_upgrades_st_cum_hat',
                   'UpgradesCumFracLow': '_b_upgrade_exper_low_hat'}
    
    for object in objects_dir:
        df_object = pd.DataFrame(np.empty((0, 3)), columns = ['object', 'replicate_number', 'replicate_value'])
        num_replicates = df_raw.shape[0]
        df_object['replicate_value'] = df_raw[objects_dir[object]].values
        df_object['replicate_number'] = np.linspace(1, num_replicates, num_replicates)
        df_object['object'] = [object for replicate in range(num_replicates)]
        df_replicates = pd.concat([df_replicates, df_object], ignore_index = True)

    df_replicates['replicate_number'] = df_replicates['replicate_number'].astype(int)
    df_replicates['replicate_value'] = np.around(df_replicates['replicate_value'].values, n)
    return df_replicates
    
def PrepareEstimatesDf(indir):
    '''
    takes the mean and standard deviation of each
    object in df_replicates

    Parameters
    ----------
    indir: str
        The director where the raw estimates are stored
    
    Returns
    -------
    df_estimates: dataframe
        Replicates dataframe in the form:
        object      estimate        std_err
        name        #               ####
    '''
    df_raw = pd.read_csv(f'{indir}/estimates.txt', sep = "\t", names = ['Statistic', 'Object', '(4)'])
    df_estimates = pd.DataFrame(np.empty((0, 3)), columns = ['object', 'estimate', 'std_err'])
    objects_dir = {'UpgradesCum': 'num_exper_upgrades_st_cum_hat',
                   'UpgradesCumFracLow': 'upgrade_exper_low_hat'}
    for object in objects_dir:
        df_object = pd.DataFrame(np.empty((0, 3)), columns = ['object', 'estimate', 'std_err'])
        estimate_index = df_raw.index[df_raw['Object'] == objects_dir[object]].values[0]
        se_index = estimate_index + 1
        df_object['estimate'] = [float(df_raw.loc[estimate_index, '(4)'].strip('***'))]
        df_object['std_err'] = [float(df_raw.loc[se_index, '(4)'].strip('()'))]
        df_object['object'] = [object]
        df_estimates = pd.concat([df_estimates, df_object], ignore_index = True)
    
    return df_estimates

def IntegrityCheck(df_OOI, df_replicates, df_estimates):
    '''
    asserts that the derived estimates are
    equal to those given in the table

    Parameters
    ----------
    df_OOI: dataframe
        Dataframe containing table values from 
        objects_of_interest.csv
    df_replicates: dataframe
        A dataframe storing each object and its replicate
        values
    df_estimates: dataframe
        Dataframe or proposed estimates
    '''
    # Fetch reported estimates from df_OOI and compare to derived estimates
    for object in df_OOI['shortname_object'].values:
        rep_estimate = df_OOI.loc[df_OOI['shortname_object'] == object, 'estimate'].values[0]
        rep_std_err = df_OOI.loc[df_OOI['shortname_object'] == object, 'bootstrap_se'].values[0]

        estimate = df_estimates.loc[df_estimates['object'] == object, 'estimate'].values[0]
        std_err = df_estimates.loc[df_estimates['object'] == object, 'std_err'].values[0]
        assert [estimate, std_err] == [rep_estimate, rep_std_err]
    
    # Check standard error of replicates matches reported standard error
    for object in df_OOI['shortname_object'].values:
        rep_std_err = df_estimates.loc[df_estimates['object'] == object, 'std_err'].values[0]
        replicates = df_replicates.loc[df_replicates['object'] == object, 'replicate_value'].values
        std_err = np.std(replicates, ddof = 1)

        assert abs(std_err - rep_std_err) < 0.001

if __name__ == "__main__":
    main()
