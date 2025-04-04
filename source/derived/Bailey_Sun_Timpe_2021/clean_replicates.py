import pandas as pd
import numpy as np
import sys
import zipfile
sys.path.append('source/lib/JMSLab')
from statistics import stdev
from SaveData import SaveData


def Main():
    paper = 'Bailey_Sun_Timpe_2021'
    rawdir = 'datastore/raw/bootstrap_census/Bailey_Sun_Timpe_2021/orig'
    indir = 'temp/B2021'
    outdir = 'output/derived/bootstrap_census'
    indir_precision = 'source/derived/bootstrap_census'

    objects_dic = {"ATETeconomicSelfSufficiency": "tab4_z_ess2_fullinfo_all",
                    "ATETyearsOfSchooling": "tab1_hc_1_fullinfo_all",
                    "ATETcompletedCollege": "tab1_hc_4_fullinfo_all",
                    "ATETattendedSomeCollege": "tab1_hc_3_fullinfo_all",
                    "ATETcompletedHighSchool": "tab1_hc_2_fullinfo_all",
                    "ATEThumanCapital": "tab1_z_hc_fullinfo_all"}
    
    unzip_data(rawdir, indir, ['code for js', 'replicates'])
    n_digits = pd.read_csv(f'{indir_precision}/digits_after_comma_precision.txt',
                           header = None)[0][0]
    
    st_dev_dic = clean_replicates(f'{indir}/replicates', f'{outdir}/{paper}_Replicates',
                        objects_dic, n_digits)

    # Slice tab#_ part of object values to retrieve estimates from bootstrap_replicates
    for object in objects_dic:
        objects_dic[object] = objects_dic[object][5:]
    
    prepare_estimates(f'{indir}/code for js/output', f'{outdir}/{paper}_Estimates', 
                        objects_dic, st_dev_dic, n_digits)


def clean_replicates(indir, outfile, objects_dir, n):
    '''
    Builds the replicates used in Bailey_Sun_Timpe_2021

    Parameters
    ----------
    indir: string
        The directory where the raw data is stored
    outfile: string
        The file where the csv file should be saved
    objects_dir: dic
        A dictionary where the names of the objects
        are the keys, and their file names are their
        data
    n: int
        Number of digits to round the replicates to

    Return
    ------
    Returns a dictionary of the standard deviation for each
    object in objects_dir
    '''
    st_dev_dic = {}
    paper_replicates = []

    for object in objects_dir:
        object_data = pd.read_stata(f'{indir}/{objects_dir[object]}.dta', preserve_dtypes = True)
        replicate_num = range(1, len(object_data.index) + 1)
        
        object_replicates = pd.DataFrame((object_data['itt']/object_data['fs']).values,
                                        columns = ['replicate_value'])
        object_replicates['replicate_number'] = replicate_num
        object_replicates['object'] = np.full((len(object_data.index), 1), object)

        # Multiply replicates by 100 to turn to percent points to match paper
        if object != 'ATETyearsOfSchooling':
            object_replicates['replicate_value'] = object_replicates['replicate_value'] * 100
            object_replicates['replicate_value'] = np.around(object_replicates['replicate_value'], n)
        else:
            object_replicates['replicate_value'] = np.around(object_replicates['replicate_value'], n)
        
        paper_replicates.append(object_replicates)
        st_dev_dic[object] = stdev(object_replicates['replicate_value'].values.tolist())
    
    df_replicates = pd.concat([replicates for replicates in paper_replicates],
                                    ignore_index = True)
    SaveData(df_replicates[['object', 'replicate_number', 'replicate_value']],
             keys     = ['object', 'replicate_number'],
             out_file =  f'{outfile}.csv',
             log_file = f'{outfile}.log')
    return st_dev_dic


def prepare_estimates(indir, outfile, objects_dic, sd_dic, n):
    '''
    Builds the replicates used in Bailey_Sun_Timpe_2021

    Parameters
    ----------
    indir: string
        The directory where the raw data is stored
    outfile: string
        The file where the csv file should be saved
    objects_dir: dic
        A dictionary where the names of the objects
        are the keys, and the column name in 
        bootstrap_replicates.xlsx contains their data
    sd_dic: dic
        A dictionary containing the standard deviation
        for each object in objects_dir
    n: int
        Number of digits to round the replicates to
    '''
    df_data = pd.read_excel(f'{indir}/bootstrap_replicate.xls')
    df_estimates = pd.DataFrame(columns = ['estimate', 'std_err', 'object'])

    for object in objects_dic:

        # Multiply estimates by 100 to turn to percent points to match paper
        if object == 'ATETyearsOfSchooling':
            estimate = np.around(df_data[objects_dic[object]][0], 2)
        elif object == 'ATETcompletedCollege' or object == 'ATEThumanCapital':
            estimate = np.around(df_data[objects_dic[object]][0] * 100, 0)
        else:
            estimate = np.around(df_data[objects_dic[object]][0] * 100, 1)
        
        object_row = {'estimate': estimate, 
                      'std_err': np.around(sd_dic[object], n),
                      'object': object}
        df_object = pd.DataFrame(object_row, index = [0])
        df_estimates = pd.concat([df_estimates, df_object], ignore_index = True)
        check_estimates(df_estimates)
    
    SaveData(df_estimates[['object', 'estimate', 'std_err']],
             keys   = ['object'],
             out_file = f'{outfile}.csv',
             log_file = f'{outfile}.log')

def check_estimates(df_estimates):
    '''
    Checks that the estimates in df_estimates are equal
    to those in objects_of_interest.csv

    Parameters
    ----------
    df_estimates: pandas dataframe
        The dataframe containing the object names and
        their estimates
    '''
    indir = 'source/raw/bootstrap_census/orig'
    df_orig = pd.read_csv(f'{indir}/objects_of_interest.csv')
    df_orig = df_orig[df_orig['citation'] == 'Bailey_Sun_Timpe_2021']
    objects = df_estimates['object'].values

    for object in objects:
        df_orig_ob = df_orig[df_orig['shortname_object'] == object]
        orig_estimate = df_orig_ob['estimate'].values[0]
        estimate = df_estimates[df_estimates['object'] == object]['estimate'].values[0]
        assert orig_estimate == estimate

def unzip_data(indir, outdir, files):
    '''
    Unzips files from indir and places them in outdir

    Parameters
    ----------
    indir: string
        The directory where the zipped files are placed
    outdir: string
        The directory where the zipped files should be
        outputted to
    files: list
        A list of strings of the names of the zipped 
        files to be unzipped
    '''
    for file in files:
        with zipfile.ZipFile(f'{indir}/{file}.zip', 'r') as zip_ref:
            zip_ref.extractall(outdir)

Main()
