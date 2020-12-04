import urllib
import urllib.request
import os
import shutil
import zipfile
import pandas as pd

#cd = r'C:\Users\mreasne\Documents\GitHub'
cd = os.path.join(os.path.expanduser("~"),r'Projects')
extract_dir = os.path.join(cd,r'uniform_counties',r'raw_data')
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
    year_dest_path = os.path.join(extract_dir,year_str+r'.annual 10 Total, all industries.csv')
    if year > 1989:
        year_source_path = os.path.join(extract_dir,year_str+r'.annual.by_industry',year_str+r'.annual 10 Total, all industries.csv')    
        shutil.move(year_source_path,year_dest_path)
        year_source_dir = os.path.join(extract_dir,year_str+r'.annual.by_industry')
        shutil.rmtree(year_source_dir)
    #renames csvs
    year_name = os.path.join(extract_dir,year_str+r'.csv') 
    os.rename(year_dest_path,year_name)
    #combine csvs
    df = pd.read_csv(year_name,dtype=str,index_col=False)
    dfs.append(df)

#how often are each FIPS code observed?
df = dfs[0]
for index,year in enumerate(range(1984,2010)):
    df = df.append(dfs[index+1]) 

#make mapping
    #keep private industry at the county level
df = df[(df['own_code'] == '5') & (df['agglvl_code'] == '71')]
    #keep relevant variables
to_keep = ['area_fips','year','annual_avg_estabs_count', 'annual_avg_emplvl', 'total_annual_wages','annual_avg_wkly_wage','avg_annual_pay']
df = df[to_keep]
    #rename variables to be more easily interpreted
new_names = ['fips','year','estabs','emp','tot_wages','avg_wkly_wage','avg_ann_pay']
df.columns = new_names
    #drop unneeded states/territories (02 == AK, 15 == HI, 72 == PR, 78 == VI)
df['state'] = df['fips'].str[:2]
df = df[~(df['state'] == "02") & ~(df['state'] == "15") & ~(df['state'] == "72") & ~(df['state'] == "78")]
#save full data 
full_data_path = os.path.join(cd,r'uniform_counties',r'full_data.csv')
df.to_csv(full_data_path,index=False)
