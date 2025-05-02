import pandas as pd
import numpy as np
from source.lib.SaveData import SaveData

def main():
    paper = 'Bourreau_Sun_Verboven_2021'
    indir = f'datastore/raw/{paper}/data'
    indir_objects_of_int = 'source/raw/orig'
    outdir = 'output/derived'
    indir_precision = 'source/derived'

    n_digits = pd.read_csv(f'{indir_precision}/digits_after_comma_precision.txt',
                           header = None)[0][0]
    df_OOI = pd.read_csv(f'{indir_objects_of_int}/objects_of_interest.csv')
    df_OOI = df_OOI[df_OOI['citation'] == paper]
    
    df_replicates = PrepareReplicatesDf(indir, n_digits)
    df_estimates = PrepareEstimatesDf(df_OOI)

    IntegrityCheck(df_replicates, df_estimates)
        
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
    df_table7 = pd.read_csv(f'{indir}/bootstraps_table7.csv')
    df_table8 = pd.read_csv(f'{indir}/bootstraps_table8.csv')
    df_table9 = pd.read_csv(f'{indir}/bootstraps_table9.csv')
    table7, table8, table9 = {}, {}, {}
    
    # Add Table 7 replicates
    table7['OrangeDeviationNoFB'] = df_table7['x34'].values - df_table7['x46'].values
    table7['OrangeDeviationFB'] = df_table7['x13'].values - df_table7['x1'].values
    table7['SFRDeviationNoFB'] = df_table7['x23'].values - df_table7['x47'].values
    table7['SFRDeviationFB'] = df_table7['x26'].values - df_table7['x2'].values
    table7['BouyguesDeviationNoFB'] = df_table7['x45'].values - df_table7['x48'].values
    table7['BouyguesDeviationFB'] = df_table7['x6'].values - df_table7['x3'].values

    # Add table 8 replicates
    table8['OrangeCostsPreEntry'] = df_table8['x4'].values - df_table8['x1'].values
    table8['OrangeCostsPostEntry'] = df_table8['x7'].values - df_table8['x1'].values
    table8['SFRCostsPreEntry'] = df_table8['x5'].values - df_table8['x2'].values
    table8['SFRCostsPostEntry'] = df_table8['x8'].values - df_table8['x2'].values
    table8['BouyguesCostsPreEntry'] = df_table8['x6'].values - df_table8['x3'].values
    table8['BouyguesCostsPostEntry'] = df_table8['x9'].values - df_table8['x3'].values

    # Add table 9 replicates
    table9['TotalWelfare'] = df_table9['x15'].values
    table9['TotalConsumerWelfare'] = df_table9['x5'].values
    table9['FightBrandsTotalSurplus'] = df_table9['x14'].values
    table9['FightBrandsConsumerSurplus'] = df_table9['x4'].values
    table9['PriceTotalSurplus'] = df_table9['x13'].values
    table9['PriceConsumerSurplus'] = df_table9['x3'].values
    table9['VarietyTotalSurplus'] = df_table9['x12'].values
    table9['VarietyConsumerSurplus'] = df_table9['x2'].values
    
    tables = (table7, table8, table9)

    for table in tables:
        for object in table:
            num_replicates = table[object].size
            df_object = pd.DataFrame(np.empty((0, 3)), columns = ['object', 'replicate_number', 'replicate_value'])
            df_object['object'] = np.array([object for replicate in range(num_replicates)])
            df_object['replicate_value'] = table[object]
            df_object['replicate_number'] = np.linspace(1, num_replicates, num_replicates)
            df_replicates = pd.concat([df_replicates, df_object], ignore_index = True)

    df_replicates['replicate_number'] = np.int32(df_replicates['replicate_number'])
    df_replicates['replicate_value'] = np.around(df_replicates['replicate_value'].values, n)

    return df_replicates

def PrepareEstimatesDf(df_OOI):
    '''
    takes the mean and standard deviation of each
    object in df_replicates

    Parameters
    ----------
    df_OOI: dataframe
        Dataframe containing table values from 
        objects_of_interest.csv
    
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
        df_object['object'] = [object]
        df_object['estimate'] = df_OOI.loc[df_OOI['shortname_object'] == object, 'estimate'].values
        df_object['std_err'] = df_OOI.loc[df_OOI['shortname_object'] == object, 'bootstrap_se'].values
        df_estimates = pd.concat([df_estimates, df_object], ignore_index = True)

    df_estimates = df_estimates.astype({'estimate':'int'})
    df_estimates = df_estimates.astype({'std_err':'int'})

    return df_estimates
    
def IntegrityCheck(df_replicates, df_estimates):
    '''
    asserts that the derived estimates are
    equal to those given in the table

    Parameters
    ----------
    df_replicates: dataframe
        A dataframe storing each object and its replicate
        values
    df_estimates: dataframe
        Dataframe or proposed estimates
    '''
    # Build estimates from replicates
    df_comp_est = pd.DataFrame(np.empty((0, 3)), columns = ['object', 'estimate', 'std_err'])
    for object in df_replicates['object'].unique():
        replicates = df_replicates.loc[df_replicates['object'] == object, 'replicate_value']
        df_object = pd.DataFrame(np.empty((0, 3)), columns = ['object', 'estimate', 'std_err'])
        df_object['object'] = [object]
        df_object['estimate'] = [np.mean(replicates)]
        df_object['std_err'] = [np.std(replicates, ddof = 1)]
        df_comp_est = pd.concat([df_comp_est, df_object], ignore_index = True)
    
    for object in df_estimates['object'].unique():
        table_estimate = df_estimates.loc[df_estimates['object'] == object, 'estimate'].values[0]
        table_std_error = df_estimates.loc[df_estimates['object'] == object, 'std_err'].values[0]
        deriv_estimate = df_comp_est.loc[df_comp_est['object'] == object, 'estimate'].values[0]
        deriv_std_error = df_comp_est.loc[df_comp_est['object'] == object, 'std_err'].values[0]

        assert abs(table_std_error - deriv_std_error)/(0.5*(abs(table_std_error) + abs(deriv_std_error))) < 0.025
        assert abs(table_estimate - deriv_estimate)/(0.5*(abs(table_estimate) + abs(deriv_estimate))) < 0.01

main()
