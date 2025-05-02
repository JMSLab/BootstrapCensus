import pandas as pd
import numpy as np
from source.lib.SaveData import SaveData

def Main():
    paper = 'Adermon_Lindahl_Palme_2021'
    
    indir  = f'datastore/raw/{paper}/orig'
    indir_objects_of_int = 'source/raw/orig' 
    outdir = 'output/derived'
    
    df_OOI = pd.read_csv(f'{indir_objects_of_int}/objects_of_interest.csv')
    df_replicates_raw = pd.read_csv(f'{indir}/bs_replicates_adermon.csv')
    
    df_estimates = PrepareEstimatesDf(df_OOI, paper)
    
    replicates_1 = PrepareReplicatesDf(df_replicates_raw, 1, 'AdopteesParents')
    replicates_2 = PrepareReplicatesDf(df_replicates_raw, 2, 'AdopteesExtendedFam')
    df_replicates = pd.concat([replicates_1, replicates_2])
    
    IntegrityCheck('AdopteesParents', df_estimates, df_replicates)
    IntegrityCheck('AdopteesExtendedFam', df_estimates, df_replicates)
        
    SaveData(df_replicates,
             keys    =['object', 'replicate_number'],
             out_file =  f'{outdir}/{paper}_Replicates.csv',
             log_file = f'{outdir}/{paper}_Replicates.log')
    
    SaveData(df_estimates,
             keys    =['object'],
             out_file =  f'{outdir}/{paper}_Estimates.csv',
             log_file = f'{outdir}/{paper}_Estimates.log')    
    
def PrepareEstimatesDf(df_OOI, paper):
    df_OOI = df_OOI[df_OOI['citation'] == paper]
    
    df_estimates = df_OOI[['shortname_object', 'estimate', 'bootstrap_se']]
    df_estimates = df_estimates.rename(columns={'shortname_object': 'object', 'bootstrap_se': 'std_err'})
    
    return df_estimates

def PrepareReplicatesDf(df_replicates_raw, column_n, object_name):
    df_replicates = df_replicates_raw[df_replicates_raw['column'] == column_n]
    df_replicates = df_replicates.assign(object = object_name) 
    df_replicates = df_replicates.assign(replicate_number=(np.arange(len(df_replicates)) + 1))
    df_replicates = df_replicates[['object', 'replicate_number', 'point_estimate']]
    
    df_replicates = df_replicates.rename(columns={'point_estimate': 'replicate_value'})
    
    return df_replicates

def IntegrityCheck(object, df_estimates, df_replicates):
    paper_se = df_estimates['std_err'][df_estimates['object']==object].values[0]
    replicate_se = np.around(np.std(df_replicates['replicate_value'][df_replicates['object']==object]), decimals = 3)
    
    assert(np.abs(paper_se-replicate_se) <= 0.001)
    
Main()
