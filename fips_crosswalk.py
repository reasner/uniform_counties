import urllib
import urllib.request
import os
import shutil
import zipfile
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib as mpl

# SETUP
cd = os.path.join(os.path.expanduser("~"),r'Projects')
extract_dir = os.path.join(cd,r'uniform_counties',r'raw_data')
try:
    os.mkdir(extract_dir)
except OSError:
    pass
dfs = []

# RETRIEVE DATA
for year in range(1983,2010):
    year_str = str(year)
    ## BLS url for retrieval by vintage
    if year < 1990:
        year_url = r'https://data.bls.gov/cew/data/files/' + year_str + r'/csv/' + year_str + r'_annual_naics10_totals.zip'
    else:
        year_url = r'https://data.bls.gov/cew/data/files/' + year_str + r'/csv/' + year_str + r'_annual_by_industry.zip'
    ## retrieve and unzip file from BLS
    zip_path, _ = urllib.request.urlretrieve(year_url)
    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(extract_dir)
    ## remove csv we want from folder for 1990 onward
    year_dest_path = os.path.join(extract_dir,year_str+r'.annual 10 Total, all industries.csv')
    if year > 1989:
        year_source_path = os.path.join(extract_dir,year_str+r'.annual.by_industry',year_str+r'.annual 10 Total, all industries.csv')    
        shutil.move(year_source_path,year_dest_path)
        year_source_dir = os.path.join(extract_dir,year_str+r'.annual.by_industry')
        shutil.rmtree(year_source_dir)
    ## renames csvs
    year_name = os.path.join(extract_dir,year_str+r'.csv') 
    os.rename(year_dest_path,year_name)
    ## combine csvs
    df = pd.read_csv(year_name,dtype=str)
    dfs.append(df)
## combine
df = dfs[0]
for index,year in enumerate(range(1984,2010)):
    df = df.append(dfs[index+1]) 

# MAKE CROSSWALK
## Setup
### keep private industry at the county level
df = df[(df['own_code'] == '5') & (df['agglvl_code'] == '71')]
### keep relevant variables
to_keep = ['area_fips','year','annual_avg_estabs_count', 'annual_avg_emplvl', 'total_annual_wages','annual_avg_wkly_wage','avg_annual_pay']
df = df[to_keep]
### rename variables to be more easily interpreted
new_names = ['fips','year','estabs','emp','tot_wages','avg_wkly_wage','avg_ann_pay']
df.columns = new_names
### drop unneeded states/territories (02 == AK, 15 == HI, 72 == PR, 78 == VI)
df['state'] = df['fips'].str[:2]
df = df[~(df['state'] == '02') & ~(df['state'] == '15') & ~(df['state'] == '72') & ~(df['state'] == '78')]
### drop non-county observations (such as out-of-state)
df['county'] = df['fips'].str[2:]
df = df[~(df['county'] == '996') & ~(df['county'] == '997') & ~(df['county'] == '998') & ~(df['county'] == '999')]
### indiosyncratic typos in 1983
df = df[~((df['fips'] == '55078') & (df['year'] == '1983'))]
df.loc[(df['fips'] == '55901') & (df['year'] == '1983'),'fips'] = '55078'
### save full data 
full_data_path = os.path.join(cd,r'uniform_counties',r'full_data.csv')
df.to_csv(full_data_path,index=False)
## Make visual grid
### just years and fips
fips_df = df[['fips','year']]
fips_df = fips_df.sort_values(by=['year','fips'])
fips_by_year = []
for year in range(1983,2010):
    fips_year_df = fips_df[fips_df['year'] == str(year)]
    fips_by_year.append(fips_year_df)
fips_wide_df = fips_by_year[0]
fips_wide_df.insert(len(fips_wide_df.columns),'fips_1983', 1)
del fips_wide_df['year']
### make visual grid
for index,year in enumerate(range(1984,2010)):
    left_year = 'fips_'+str(year-1)   
    right_year = 'fips_'+str(year)
    fips_wide_df = pd.merge(fips_wide_df,fips_by_year[index+1],on='fips',how='outer',indicator=True)
    fips_wide_df = fips_wide_df.rename(columns={'year':right_year})
    fips_wide_df.loc[fips_wide_df['_merge'] == 'both',right_year] = 1
    fips_wide_df.loc[fips_wide_df['_merge'] == 'right_only',right_year] = 1
    del fips_wide_df['_merge']
for year in range(1983,2010):
    var_label = 'fips_'+str(year)
    fips_wide_df[var_label] = fips_wide_df[var_label].fillna(0)
### save visual grid
fips_wide_df['num_years_observed'] = fips_wide_df.sum(axis=1)
fips_wide_df = fips_wide_df.sort_values(by=['fips'])
vis_years_path = os.path.join(cd,r'uniform_counties',r'vis_years.csv')
fips_wide_df.to_csv(vis_years_path,index=False)
## Make crosswalk
fips_df['new_fips'] = fips_df['fips']
### fix counties that do not appear in every year
fips_df.loc[fips_df['fips'] == '12025','new_fips'] = '12086' #uniform across name change
fips_df.loc[fips_df['fips'] == '31115','new_fips'] = '31071' #combine w/ neighbor
fips_df.loc[fips_df['fips'] == '31117','new_fips'] = '31113' #combine w/ neighbor
fips_df.loc[fips_df['fips'] == '48033','new_fips'] = '48415' #combine w/ neighbor
fips_df.loc[fips_df['fips'] == '48301','new_fips'] = '48389' #combine w/ neighbor
fips_df.loc[fips_df['fips'] == '51560','new_fips'] = '51005' #combine w/ neighbor
fips_df.loc[fips_df['fips'] == '51780','new_fips'] = '51083' #combine w/ neighbor
fips_df.loc[fips_df['fips'] == '08014','new_fips'] = '08031' #make one "Denver" county
fips_df.loc[fips_df['fips'] == '08001','new_fips'] = '08031' #make one "Denver" county
fips_df.loc[fips_df['fips'] == '08059','new_fips'] = '08031' #make one "Denver" county
fips_df.loc[fips_df['fips'] == '08123','new_fips'] = '08031' #make one "Denver" county
fips_df.loc[fips_df['fips'] == '08013','new_fips'] = '08031' #make one "Denver" county
fips_df.loc[fips_df['fips'] == '55078','new_fips'] = '55115' #combine reservation in WI w/ neighbor
### fix independent cities (//combine w/ neighbor for all)
fips_df.loc[fips_df['fips'] == '51510','new_fips'] = '51059'
fips_df.loc[fips_df['fips'] == '51515','new_fips'] = '51019'
fips_df.loc[fips_df['fips'] == '51520','new_fips'] = '51191'
fips_df.loc[fips_df['fips'] == '51530','new_fips'] = '51163'
fips_df.loc[fips_df['fips'] == '51540','new_fips'] = '51003'
fips_df.loc[fips_df['fips'] == '51550','new_fips'] = '51710'
fips_df.loc[fips_df['fips'] == '51570','new_fips'] = '51053'
fips_df.loc[fips_df['fips'] == '51580','new_fips'] = '51005'
fips_df.loc[fips_df['fips'] == '51590','new_fips'] = '51143'
fips_df.loc[fips_df['fips'] == '51595','new_fips'] = '51081'
fips_df.loc[fips_df['fips'] == '51600','new_fips'] = '51059'
fips_df.loc[fips_df['fips'] == '51610','new_fips'] = '51059'
fips_df.loc[fips_df['fips'] == '51620','new_fips'] = '51175'
fips_df.loc[fips_df['fips'] == '51630','new_fips'] = '51177'
fips_df.loc[fips_df['fips'] == '51640','new_fips'] = '51035'
fips_df.loc[fips_df['fips'] == '51650','new_fips'] = '51199'
fips_df.loc[fips_df['fips'] == '51660','new_fips'] = '51165'
fips_df.loc[fips_df['fips'] == '51670','new_fips'] = '51149'
fips_df.loc[fips_df['fips'] == '51678','new_fips'] = '51163'
fips_df.loc[fips_df['fips'] == '51680','new_fips'] = '51031'
fips_df.loc[fips_df['fips'] == '51683','new_fips'] = '51153'
fips_df.loc[fips_df['fips'] == '51685','new_fips'] = '51153'
fips_df.loc[fips_df['fips'] == '51690','new_fips'] = '51089'
fips_df.loc[fips_df['fips'] == '51700','new_fips'] = '51199'
fips_df.loc[fips_df['fips'] == '51710','new_fips'] = '51710'
fips_df.loc[fips_df['fips'] == '51720','new_fips'] = '51195'
fips_df.loc[fips_df['fips'] == '51730','new_fips'] = '51053'
fips_df.loc[fips_df['fips'] == '51735','new_fips'] = '51199'
fips_df.loc[fips_df['fips'] == '51740','new_fips'] = '51710'
fips_df.loc[fips_df['fips'] == '51750','new_fips'] = '51121'
fips_df.loc[fips_df['fips'] == '51760','new_fips'] = '51087'
fips_df.loc[fips_df['fips'] == '51770','new_fips'] = '51161'
fips_df.loc[fips_df['fips'] == '51775','new_fips'] = '51161'
fips_df.loc[fips_df['fips'] == '51790','new_fips'] = '51015'
fips_df.loc[fips_df['fips'] == '51820','new_fips'] = '51015'
fips_df.loc[fips_df['fips'] == '51830','new_fips'] = '51095'
fips_df.loc[fips_df['fips'] == '51840','new_fips'] = '51069'
### cities split from surrounding county
fips_df.loc[fips_df['fips'] == '24510','new_fips'] = '24005'
fips_df.loc[fips_df['fips'] == '29510','new_fips'] = '29189'
### save mapping (3,061 counties in final crosswalk)
fips_crosswalk_path = os.path.join(cd,r'uniform_counties',r'fips_crosswalk.csv')
fips_df.to_csv(fips_crosswalk_path,index=False)

# APPLY TO DATA (MAKE PANEL)
new_fips_df = pd.merge(df,fips_df,on=['year','fips'],how='outer',indicator=True)
new_fips_df = new_fips_df.drop(['fips','_merge','avg_wkly_wage','avg_ann_pay','state','county'], axis=1)
new_fips_df = new_fips_df.rename(columns={'new_fips':'fips'})
## collapse
new_fips_df[['estabs','emp','tot_wages']] = new_fips_df[['estabs','emp','tot_wages']].apply(pd.to_numeric)
new_fips_summed = new_fips_df.groupby(['year', 'fips'])[['estabs', 'emp', 'tot_wages']].sum()
new_fips_summed['avg_annual_pay'] = round(new_fips_summed['tot_wages']/new_fips_summed['emp'],0)

## save full panel (w/ new FIPS)
panel_path = os.path.join(cd,r'uniform_counties',r'panel.csv')
new_fips_summed.to_csv(panel_path,float_format='%.f')

# MAPPING EXAMPLE
## calculate average size of establishments by county by year
new_fips_summed['avg_size_estabs'] = round(new_fips_summed['emp']/new_fips_summed['estabs'],0)
## map average size of establishments
###setup map
shapefile_path = os.path.join(cd,r'uniform_counties',r'gz_2010_us_050_00_500k',r'gz_2010_us_050_00_500k.shp')
county_map = gpd.read_file(shapefile_path)
county_map = county_map[(county_map['STATE'] != '02') & (county_map['STATE'] != '15') & (county_map['STATE'] != '72')]
projection = "+proj=laea +lat_0=30 +lon_0=-95"
fig, ax = plt.subplots(1, figsize=(8.5,6.5))
ax.axis('off')
'''
cmap = mpl.colors.LinearSegmentedColormap.from_list('Custom cmap', ["steelblue", "white", "tomato"])
'''
cmap = plt.get_cmap('plasma')
###join economic data
county_map['fips'] = county_map['STATE'] + county_map['COUNTY']
new_fips_2000_df = new_fips_summed.iloc[new_fips_summed.index.get_level_values('year') == '2000']
county_econ_df = pd.merge(county_map, new_fips_2000_df, on='fips', how='inner')
county_econ_df = county_econ_df.to_crs(projection)
county_econ_df[['avg_size_estabs']] = county_econ_df[['avg_size_estabs']].apply(pd.to_numeric)
county_econ_df.plot(ax=ax, column='avg_size_estabs', legend=True, legend_kwds={'loc':'lower left'}, scheme='quantiles', linewidth=0.3, edgecolor='gray', cmap=cmap)
plt.title('Average Establishment Size (2000)')
naive_plot_path = os.path.join(cd,r'uniform_counties','naive_plot.png')
plt.savefig(naive_plot_path,bbox_inches='tight',dpi=300)


## use mapping again to fill in map
new_fips_2000_df.index.names = ['year','new_fips']
fips_df = fips_df.set_index(['year', 'new_fips'])
filled_in_df = pd.merge(new_fips_2000_df,fips_df,on=['year','new_fips'],how='inner')
filled_in_map_df = pd.merge(county_map,filled_in_df,on='fips',how='inner')
filled_in_map_df = filled_in_map_df.to_crs(projection)
filled_in_map_df.plot(ax=ax, column='avg_size_estabs', legend=True, legend_kwds={'loc':'lower left'}, scheme='quantiles', linewidth=0.3, edgecolor='gray', cmap=cmap)
plt.title('Average Establishment Size (2000)')
better_plot_path = os.path.join(cd,r'uniform_counties','better_plot.png')
plt.savefig(better_plot_path,bbox_inches='tight',dpi=300)

