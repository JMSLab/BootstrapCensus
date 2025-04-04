import pandas as pd
import numpy as np
import sys
sys.path.append('source/lib/JMSLab')
from SaveData import SaveData

def Main():
    paper                = 'Reimers_Waldfogel_2021'
    indir_replicates     = 'temp/RW2021'
    indir_objects_of_int = 'source/raw/bootstrap_census/orig' 
    outdir               = 'output/derived/bootstrap_census'
    indir_precision      = 'source/derived/bootstrap_census'
    
    file_names       = ['table3_bottom_replicates.dta',
                        'table3_top_replicates.dta',
                        'table4_replicates.dta']
    
    variable_object_map = {'nyt1' : 'PercentageIncreaseAfterNYTReview',
                           'nyt1r' : 'PercentageIncreaseAfterNYTReviewAndRecommendation',
                           'starmean' : 'AmazonStarElasticity',
                           'nyt_not_rec_only' : 'AnnualPercentageIncreaseFollowingNYT',
                           'ratio' : 'DeltaConsumerSurplusRatio',
                           'dCS_reviews' : 'DeltaConsumerSurplusReviews',
                           'dCS_stars_adj' : 'DeltaConsumerSurplusStars'}
    
    df_replicates_cols = ['replicate_number', 'object', 'replicate_value']
    
    df_replicates = pd.DataFrame(columns = df_replicates_cols)
    
    df_replicates = AugmentDfReplicates(indir_replicates, file_names,
                                        df_replicates, df_replicates_cols,
                                        variable_object_map)
    
    objects_paper = df_replicates['object'].unique()
        
    df_estimate_std = pd.read_csv(f'{indir_objects_of_int}/objects_of_interest.csv')
    
    df_estimates = PrepareObjectEstimateStdDf(df_estimate_std,
                                                        objects_paper)
    
    CheckIntegrity(df_replicates, df_estimates)
    
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
    
    
def AugmentDfReplicates(indir_replicates, file_names, df_replicates,
                        df_replicates_cols, variable_object_map):
    
    for file in file_names:
        df_objects = pd.read_stata(f'{indir_replicates}/{file}')
        df_objects.dropna(inplace = True)
        df_objects_long = pd.DataFrame(df_objects.stack()).reset_index()
        df_objects_long = df_objects_long.set_axis(df_replicates_cols, axis = 1)    
        df_replicates = pd.concat([df_replicates, df_objects_long])
    
    df_replicates['replicate_number'] = pd.to_numeric(df_replicates['replicate_number'])
    df_replicates = df_replicates.replace({"object":variable_object_map})
    df_replicates['replicate_number'] = df_replicates['replicate_number'] + 1
    
    elasticity_cols = ['AmazonStarElasticity',
                       'PercentageIncreaseAfterNYTReview',
                       'PercentageIncreaseAfterNYTReviewAndRecommendation']
       
    df_replicates['replicate_value'] = np.where(df_replicates['object'].isin(elasticity_cols),
                                      df_replicates['replicate_value'] * -1,
                                      df_replicates['replicate_value'])
    
    df_replicates['replicate_value'] = np.array([float(replicate_value) \
        for replicate_value in df_replicates['replicate_value']])
    
    return df_replicates

def PrepareObjectEstimateStdDf(df_estimate_std, objects_paper):
    
    object_map = {}
    for object in objects_paper:
        object_map[object] = [df_estimate_std[df_estimate_std\
                                              ['shortname_object'] == object]\
                              ['estimate'].values[0],
                              df_estimate_std[df_estimate_std\
                                              ['shortname_object'] == object]\
                              ['bootstrap_se'].values[0]]
          
    stacked = pd.DataFrame(object_map).stack().reset_index()
    df_object_estimate_std = stacked.pivot(index = 'level_1',
                                           columns = 'level_0').reset_index()
    
    colnames = ['object', 'estimate', 'std_err']
    
    df_object_estimate_std = df_object_estimate_std.set_axis(colnames,
                                                             axis = 1)
    
    return df_object_estimate_std
    
def CheckIntegrity(df_replicates, df_estimates):
    
    df_replicate_std = df_replicates.groupby('object')['replicate_value'].std().reset_index()
    df_check = df_estimates.merge(df_replicate_std, on = 'object')
    
    assert all(x <= 1e-02 for x in np.absolute(df_check['std_err'] - df_check['replicate_value']))

Main()    
    

