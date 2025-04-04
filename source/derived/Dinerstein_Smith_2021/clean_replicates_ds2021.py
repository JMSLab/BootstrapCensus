import pandas as pd
import numpy as np
import sys
import shutil
sys.path.append('source/lib/JMSLab')
from SaveData import SaveData

def Main():
    paper = 'Dinerstein_Smith_2021'
    
    rawdir  = f'datastore/raw/bootstrap_census/{paper}/orig'
    temp = 'temp'
    indir = 'temp/DS2021/temp/model_data'
    indir_objects_of_int = 'source/raw/bootstrap_census/orig' 
    outdir = 'output/derived/bootstrap_census'
    
    shutil.unpack_archive(f'{rawdir}/DS2021.zip', temp)
    
    df_OOI = pd.read_csv(f'{indir_objects_of_int}/objects_of_interest.csv')
    colnames=['mu1hat', 'mu2hat', 'mu3hat', 'mu1boot', 'mu2boot', 'mu3boot'] 
    df_replicates_raw = pd.read_csv(f'{indir}/supply_estimates.csv', names=colnames, header=None)
    
    df_estimates = PrepareEstimatesDf(df_OOI, paper)
    df_replicates = PrepareReplicatesDf(df_replicates_raw, 'mu1boot', 'MeanCostPerGrade')
    
    IntegrityCheck('MeanCostPerGrade', df_estimates, df_replicates)
        
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

def PrepareReplicatesDf(df_replicates_raw, column_name, object_name):
    df_replicates = df_replicates_raw[[column_name]]
    df_replicates = df_replicates.assign(object = object_name) 
    df_replicates = df_replicates.assign(replicate_number=(np.arange(len(df_replicates)) + 1))
    df_replicates = df_replicates[['object', 'replicate_number', 'mu1boot']]
    
    df_replicates = df_replicates.rename(columns={'mu1boot': 'replicate_value'})
    
    return df_replicates

def IntegrityCheck(object, df_estimates, df_replicates):
    paper_se = df_estimates['std_err'][df_estimates['object']==object].values[0]
    replicate_se = np.around(np.std(df_replicates['replicate_value'][df_replicates['object']==object]), decimals = 2)
    
    assert(np.abs(paper_se-replicate_se) <= 0.1)


    
Main()
