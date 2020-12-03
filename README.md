# Uniform Counties
Mapping for uniform FIPS codes (U.S. counties) from 1983 to 2009 for the contiguous U.S.

## Description

First, the script *get_qcew.py* downloads annual files for the Quarterly Census of Employment and Wages ([QCEW](https://www.bls.gov/cew/downloadable-data-files.htm)) from the Bureau of Labor Statistics (BLS). 

In these files, individual counties are indexed by Federal Information Processing System ([FIPS](https://transition.fcc.gov/oet/info/maps/census/fips/fips.txt)) codes. FIPS codes are unique 5-digit identifiers: the first two digits refer to the state (in alphabetical order) and the last three refer to the county within the state (also in alphabetical order using odd numbers, e.g. 001 for Autauga County, AL followed by 003 for Baldwin County, AL). In some states the corresponding geographical area has an alternative name such as boroughs in Alaska and parishes in Louisiana. Three states have a unqiue FIPS code for at least one independent city and there will be more on that later.

Next the script *fips_map.do* combines each annual file and produces a grid (code-by-year) to visualize the years in which each FIPS code is observed in the data. For all 50 states there are 3,125 FIPS codes that are observed in the data every year from 1983 to 2009 and 26 FIPS codes that are not. 
