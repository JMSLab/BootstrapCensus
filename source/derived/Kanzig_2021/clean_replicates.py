import numpy as np
import pandas as pd
from scipy.io import loadmat
from statistics import stdev
from source.lib.SaveData import SaveData

def Main():
    paper  = 'Kanzig_2021'
    indir  = 'temp/K2021'
    outdir = 'datastore/output/derived_large'
    logdir = 'output/derived'
    indir_precision = 'source/derived'    
    
    objects = ['OilPriceResponse', 'OilProductionResponse', 'OilInventoriesResponse', 
                'WorldProductionResponse', 'USProductionResponse', 'CPIResponse']
    
    peak_months = {'CPIResponse': 12, 'OilInventoriesResponse': 44,
                'OilPriceResponse': 2, 'OilProductionResponse': 36,
                'USProductionResponse': 39, 'WorldProductionResponse': 43}

    df_replicates_cols = ['object', 'replicate_number', 'replicate_value']
    df_replicates = pd.DataFrame(columns = df_replicates_cols)
    
    df_estimates_cols  = ['object', 'estimate', 'std_err']
    df_estimates = pd.DataFrame(columns = df_estimates_cols)    
    
    n_digits = pd.read_csv(f'{indir_precision}/digits_after_comma_precision.txt',
                           header = None)[0][0]
    df_replicates = df_replicates.round(n_digits)    
    df_estimates  = df_estimates.round(n_digits)    
    
    stdev_list = PrepareReplicates(indir, outdir, logdir, paper,
                                  objects, df_replicates,
                                  df_replicates_cols, peak_months)
    PrepareEstimates(indir, outdir, paper, objects, df_estimates, 
                                    df_estimates_cols, peak_months,
                                    stdev_list)
    
    
def PrepareReplicates(indir, outdir, logdir, paper,
                                  objects, df_replicates,
                                  df_replicates_cols, peak_months):
    stdev_list = []
    for object in objects:
        df_object = pd.read_csv(f'{indir}/{object}.csv', header = None)
    
        df_object = df_object.transpose()
        
        if object in ["OilInventoriesResponse", "OilProductionResponse"]:
            IntegrityChecks(df_object, object)
        
        df_object = df_object[peak_months[object]]
        
        df_long = pd.DataFrame(df_object).reset_index()
        df_long = df_long.set_axis(df_replicates_cols[1:], axis = 1)
        df_long['object'] = object
        df_replicates     = pd.concat([df_replicates, df_long])

        stdev_list.append(stdev(df_long['replicate_value'].values.tolist()))

    SaveData(df_replicates[['object', 'replicate_number', 'replicate_value']],
             keys    = ['object', 'replicate_number'],
             out_file = f'{outdir}/{paper}_Replicates.csv',
             log_file = f'{logdir}/{paper}_Replicates_manifest.log')
    return stdev_list
    
    
    
def IntegrityChecks(df_object, object):
    if object == "OilInventoriesResponse":
        ub_figure = 1.93
        lb_figure = 0.58
        
    if object == "OilProductionResponse":
        ub_figure = -0.26
        lb_figure = -0.99
        
    measurement_month = 50    
        
    ub_replicates = df_object[[measurement_month]].quantile(0.95).values[0]
    lb_replicates = df_object[[measurement_month]].quantile(0.05).values[0]

    assert np.absolute((ub_replicates - lb_replicates) - (ub_figure - lb_figure)) <= 0.01    

def PrepareEstimates(indir, outdir, paper, objects, df_estimates,
                        df_estimates_cols, peak_months, stdev_list):

    estimates_raw = loadmat(f'{indir}/Kaenzig_replication/results/IRFsbench.mat')

    mean_array = estimates_raw['IRFs_base']

    for object in objects:
        object_estimate = mean_array[peak_months[object], objects.index(object)]

        object_sd = stdev_list[objects.index(object)]
        object_df = pd.DataFrame([[object, object_estimate, object_sd]], 
                                    columns = df_estimates_cols)
        df_estimates = pd.concat([df_estimates, object_df], ignore_index=True)

    SaveData(df_estimates,
             keys    = ['object'],
             out_file =  f'{outdir}/{paper}_Estimates.csv',
             log_file = f'{outdir}/{paper}_Estimates_manifest.log')

Main()    
