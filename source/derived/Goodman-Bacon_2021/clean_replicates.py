import pandas as pd
import numpy as np
from source.lib.SaveData import SaveData

def Main():
    paper = 'Goodman-Bacon_2021'
    
    indir  = f'datastore/raw/{paper}/orig'
    indir_objects_of_int = 'source/raw/orig' 
    outdir = 'output/derived'
    indir_precision = 'source/derived'
    
    df_replicates = pd.read_stata(f'{indir}/table9.dta')
    
    objects_map = {'dqaly65': 'QALYsSaved',
                   'r': 'PublicReturn'}
    
    df_replicates = CleanReplicates(df_replicates, objects_map)
    
    objects_paper = df_replicates['object'].unique()        
    df_estimate_std = pd.read_csv(f'{indir_objects_of_int}/objects_of_interest.csv')
    df_estimates = PrepareEstimatesDf(df_replicates, objects_paper, df_estimate_std)
    
    integrity_map = {'QALYsSaved': [5.47, 11.87],
                   'PublicReturn': [-86, 194]}
    
    for object in objects_paper:
        IntegrityCheck(object, df_replicates, integrity_map)

    n_digits = pd.read_csv(f'{indir_precision}/digits_after_comma_precision.txt',
                           header = None)[0][0]
    df_replicates = df_replicates.round(n_digits)    
    df_estimates  = df_estimates.round(n_digits)    
        
    SaveData(df_replicates[['object', 'replicate_number', 'replicate_value']],
             keys    =['object', 'replicate_number'],
             out_file =  f'{outdir}/{paper}_Replicates.csv',
             log_file = f'{outdir}/{paper}_Replicates.log')
    
    SaveData(df_estimates,
             keys    =['object'],
             out_file =  f'{outdir}/{paper}_Estimates.csv',
             log_file = f'{outdir}/{paper}_Estimates.log')    

def CleanReplicates(df_replicates, objects_map):
    df_replicates_cols = ['replicate_number', 'object', 'replicate_value']   
    
    df_replicates = df_replicates[pd.isnull(df_replicates['white'])]
    
    df_objects_long = pd.DataFrame(df_replicates.stack()).reset_index()        
    df_objects_long = df_objects_long.set_axis(df_replicates_cols, axis = 1)    
    
    variable_names  = list(objects_map.keys())
    df_objects_long = df_objects_long[df_objects_long['object'].isin(variable_names)]
            
    df_replicates = df_objects_long.replace({"object":objects_map}) 
    df_replicates['replicate_number'] = df_replicates['replicate_number'] + 1

    # Turn public return replicates into percent point units
    df_replicates.loc[df_replicates['object'] == 'PublicReturn', 'replicate_value'] =\
        df_replicates['replicate_value'][df_replicates['object'] == 'PublicReturn'] * 100
         
    return df_replicates
    
def PrepareEstimatesDf(df_replicates, objects_paper, df_estimate_std):
    object_map = {}
    for object in objects_paper:
        object_map[object] = [df_estimate_std[df_estimate_std\
                                              ['shortname_object'] == object]\
                              ['estimate'].values[0]]
    
    stacked = pd.DataFrame(object_map).stack().reset_index()
    df_object_estimate = stacked.pivot(index = 'level_1',
                                       columns = 'level_0').reset_index()

    colnames = ['object', 'estimate']
    
    df_object_estimate = df_object_estimate.set_axis(colnames,
                                                     axis = 1)
    # Turn PublicReturn estimate into percent point units
    PRIndex = np.where(df_object_estimate == 'PublicReturn')[0][0]
    df_object_estimate.at[PRIndex, 'estimate'] =\
        df_object_estimate['estimate'][PRIndex] * 100

    colnames_std = ['object', 'std_err']
    df_std = df_replicates[['object', 'replicate_value']].groupby('object').std().reset_index()
    
    df_std = df_std.set_axis(colnames_std, axis = 1)
    df_estimates = df_object_estimate.merge(df_std, on = 'object')
    
    return df_estimates

def IntegrityCheck(object, df_replicates, integrity_map):
    array_object  = df_replicates[df_replicates['object'] ==\
                                  object]['replicate_value']
    
    p5_replicates = np.percentile(array_object, 5,
                                  method = 'averaged_inverted_cdf')
    p50_replicates = np.percentile(array_object, 50,
                                  method = 'averaged_inverted_cdf')
    
    p5_paper  = integrity_map[object][0]
    p50_paper = integrity_map[object][1]
    
    if object == 'PublicReturn':
        p5_replicates = np.around(p5_replicates, 0)
        p50_replicates = np.around(p50_replicates, 0)
    elif object == 'QALYsSaved':
        p5_replicates = np.around(p5_replicates, 2)
        p50_replicates = np.around(p50_replicates, 2)

    assert p5_replicates == p5_paper
    assert p50_replicates == p50_paper
    
Main()

