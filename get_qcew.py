import urllib
import urllib.request
import os
import shutil
import zipfile
import pandas as pd

cd = r'C:\Users\mreasne\Documents\GitHub'
extract_dir = os.path.join(cd,r'uniform_counties\raw_data')
try:
    os.mkdir(extract_dir)
except OSError:
    pass
dfs = []

for year in range(1983,2010):
    year_str = str(year)
    #BLS url for retrieval by vintage
    if year < 1990:
        year_url = r'https://data.bls.gov/cew/data/files/' + year_str + r'/csv/' + year_str + r'_annual_naics10_totals.zip'
    else:
        year_url = r'https://data.bls.gov/cew/data/files/' + year_str + r'/csv/' + year_str + r'_annual_by_industry.zip'
    #retrieve and unzip file from BLS
    zip_path, _ = urllib.request.urlretrieve(year_url)
    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(extract_dir)
    #remove csv we want from folder for 1990 onward
    if year > 1989:
        year_source_path = os.path.join(extract_dir,year_str+r'.annual.by_industry',year_str+r'.annual 10 Total, all industries.csv')    
        year_dest_path = os.path.join(extract_dir,year_str+r'.annual 10 Total, all industries.csv')
        shutil.move(year_source_path, year_dest_path)
        year_source_dir = os.path.join(extract_dir,year_str+r'.annual.by_industry')
        shutil.rmtree(year_source_dir)
    #renames csvs
    year_name = os.path.join(extract_dir,year_str)
    os.rename(year_dest_path,year_name)
    #combine csvs
    df = pd.read_csv('<csvfile>')
    dfs.append(df)

df = pd.concat(dfs)
#how often are each FIPS code observed?

#make mapping

