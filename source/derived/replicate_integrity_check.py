import pandas as pd
import numpy as np

def main():
    outfile = 'output/derived/mismatched_replicates.csv'
    paper_names = ['Reimers_Waldfogel_2021', 'Finkelstein_Gentzkow_Williams_2021',
               'Goodman-Bacon_2021', 'Abebe_Caria_Ortiz-Ospina_2021',
	           'Mueller_Spinnewijn_Topa_2021', 'Kostol_Myhre_2021',
               'Bailey_Sun_Timpe_2021', 'Seibold_2021', 'Dinerstein_Smith_2021',
               'Adermon_Lindahl_Palme_2021', 'Bourreau_Sun_Verboven_2021', 'Weaver_2021',
               'Braguinsky_Ohyama_Okazaki_Syverson_2021', 'Kanzig_2021']
    df_OOI = pd.read_csv('source/raw/orig/objects_of_interest.csv')
    df_OOI = df_OOI[df_OOI['can_produce_replicates'] != 'X']

    mismatches = integrity_check(paper_names, df_OOI)
    mismatches.to_csv(outfile)

def integrity_check(paper_names, df_OOI):
    '''
    Checks if each object for each paper in 
    paper_names matches reported number of replicates
    in df_OOI

    Parameters
    ----------
    paper_names: str
        Name of papers to be checked

    Returns
    -------
    df_out: dataframe
        paper       object      rep_rep     ext_rep
        paper_name  object_name #_reported  #_extracted
    '''
    df_out = pd.DataFrame()

    for paper in paper_names:
        df_paper = df_OOI.loc[df_OOI['citation'] == paper]
        df_replicates = pd.read_csv(f'output/derived/{paper}_Replicates.csv')

        for object in df_paper['shortname_object'].unique():
            rep_num = df_paper.loc[df_paper['shortname_object'] == object, 'n_replicates'].values[0]
            extract_num = len(df_replicates[df_replicates['object'] == object])
            if rep_num != extract_num:
                df_object = pd.DataFrame({'paper': paper, 'object': object, 'rep_rep': rep_num, 'ext_rep': extract_num}, index = [0])
                df_out = pd.concat([df_out, df_object], ignore_index = True)
    
    return df_out

if __name__ == '__main__':
    main()
