import os
import shutil

def Main():
    indir = 'datastore/raw/bootstrap_census/Kanzig_2021/orig'
    temp  = 'temp'
    archive_name = 'K2021'
    
    MoveAndUnzip(indir, temp, archive_name)
    
def MoveAndUnzip(indir, temp, archive_name):    
    shutil.copy(f'{indir}/{archive_name}.zip', f'{temp}/{archive_name}.zip')
    
    extract_dir = f'{temp}/{archive_name}'
    
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
        os.makedirs(extract_dir)
    
    shutil.unpack_archive(f'{temp}/{archive_name}.zip', extract_dir) 
        
Main()

