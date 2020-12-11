'''
Example code for application of crosswalk
'''

#APPLY CROSSWALK
##load dataset and crosswalk
import pandas as pd
df = pd.read_csv(r'~/Projects/uniform_counties/full_data.csv',dtype=str)
fips_df = pd.read_csv(r'~/Projects/uniform_counties/fips_crosswalk.csv',dtype=str)

##merge crosswalk and replace fips with new_fips
df = pd.merge(df,fips_df,on=['year','fips'],how='outer',indicator=True) #join with crosswalk
df = df.drop(['fips','_merge','avg_wkly_wage','avg_ann_pay','state','county'], axis=1) #drop variables
df = df.rename(columns={'new_fips':'fips'}) #rename new_fips as fips

##collapse data 
df[['estabs','emp','tot_wages']] = df[['estabs','emp','tot_wages']].apply(pd.to_numeric) #make string variables numeric for collapse
df = df.groupby(['year', 'fips'])[['estabs', 'emp', 'tot_wages']].sum()  #collpase by "new" fips
df['avg_annual_pay'] = round(df['tot_wages']/df['emp'],0) #replace average variable after sum

#MAPPING EXAMPLE (NAIVE)
import geopandas as gpd
# calculate average size of establishments by county by year
df['avg_size_estabs'] = round(df['emp']/df['estabs'],0)
# setup plot
county_map = gpd.read_file('/Users/mason/Projects/uniform_counties/gz_2010_us_050_00_500k/gz_2010_us_050_00_500k.shp')
county_map = county_map[(county_map['STATE'] != '02') & (county_map['STATE'] != '15') & (county_map['STATE'] != '72')] #drop Alaska, Hawaii, and Puerto Rico
projection = "+proj=laea +lat_0=30 +lon_0=-95" #adjust projection
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, figsize=(8.5,6.5))
ax.axis('off')
cmap = plt.get_cmap('plasma')
# join with economic data
county_map['fips'] = county_map['STATE'] + county_map['COUNTY']
df_2000 = df.iloc[df.index.get_level_values('year') == '2000'] #keep year of interest to plot
county_df = pd.merge(county_map, df_2000, on='fips', how='inner')
county_df = county_df.to_crs(projection)
county_df[['avg_size_estabs']] = county_df[['avg_size_estabs']].apply(pd.to_numeric)
county_df.plot(ax=ax, column='avg_size_estabs', legend=True, legend_kwds={'loc':'lower left'}, scheme='quantiles', linewidth=0.3, edgecolor='gray', cmap=cmap)
plt.title('Average Establishment Size (2000)')
#plt.show()

#MAPPING EXAMPLE (BETTER)
## use mapping again to fill in map
df_2000.index.names = ['year','new_fips']
fips_df = fips_df.set_index(['year', 'new_fips'])
filled_in_df = pd.merge(df_2000,fips_df,on=['year','new_fips'],how='inner')
filled_in_county_df = pd.merge(county_map,filled_in_df,on='fips',how='inner')
filled_in_county_df = filled_in_county_df.to_crs(projection)
filled_in_county_df.plot(ax=ax, column='avg_size_estabs', legend=True, legend_kwds={'loc':'lower left'}, scheme='quantiles', linewidth=0.3, edgecolor='gray', cmap=cmap)
plt.title('Average Establishment Size (2000)')
plt.show()

