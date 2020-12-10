# Uniform Counties
Mapping for uniform FIPS codes (U.S. counties) from 1983 to 2009 for the contiguous U.S.

## Description

The Python script for this project, *fips_crosswalk.py*, does three main things:

1. Retrieves data on employment and wages by county to serve as the basis for the mapping
2. Creates a visualization of which counties are observed in the data over the panel period to aid in creating a crosswalk and then implements that information to make a usuable county crosswalk over time
3. Provides and example of how to use the crosswalk when making maps from the data

## Retrieve data
First, the script retrieves annual files for the Quarterly Census of Employment and Wages ([QCEW](https://www.bls.gov/cew/downloadable-data-files.htm)) from the Bureau of Labor Statistics (BLS). While the BLS has a nice [API]() for fetching specific data from the QCEW, it only features the more recent data, so this script directly downloads the annual files.

In these files, individual counties are indexed by Federal Information Processing System ([FIPS](https://transition.fcc.gov/oet/info/maps/census/fips/fips.txt)) codes. FIPS codes are unique 5-digit identifiers: the first two digits refer to the state (in alphabetical order) and the last three refer to the county within the state (also in alphabetical order using odd numbers, e.g. 001 for Autauga County, AL followed by 003 for Baldwin County, AL). In some states the corresponding geographical area has an alternative name such as boroughs in Alaska and parishes in Louisiana. Three states have a unqiue FIPS code for at least one independent city and there will be more on that later.

## Make crosswalk

Next the script combines each annual file (*full_data.csv*) and produces a grid (code-by-year) to visualize the years in which each FIPS code is observed in the data (*vis_data.csv*). For all 50 states there are 3,125 FIPS codes that are observed in the data every year from 1983 to 2009 and 26 FIPS codes that are not. However, because the focus of most research (including my own!) is only the contiguous U.S., I will not consider FIPS codes for Alaska, Hawaii, or Puerto Rico. This results in 3,103 counties obsvered every year and 9 that make the panel unbalanced:

| FIPS | County | # of Years Observed | Issue |
| :---: | :---: | :---: | :---: |
| 08014 | Broomfield, CO | 8 | Data not available before 2002 |
| 12025 | Dade, FL | 7 | Data unavailable after 1989 |
| 12086 | Miami-Dade, FL | 20 | Data not available before 1990 |
| 31115 | Loup, NE | 16 | Data unavailable for 1990 to 2000 |
| 31117 | McPherson, NE | 16 | Data unavailable for 1990 to 2000 |
| 48033 | Borden, TX | 16 | Data unavailable for 1990 to 2000 |
| 48301 | Loving, TX | 16 | Data unavailable for 1990 to 2000 |
| 51560 | Clifton Forge, VA	 | 8 | Data unavailable after 1989 (except 2001) |
| 51780 | South Boston, VA | 7 | Data unavailable after 1989 |

When can then combine this information with the U.S. Census Bureau's (Census) own documentation on [changes to counties](https://www.census.gov/programs-surveys/geography/technical-documentation/county-changes.html) to determine the source of the changes and then determine best course of action in each case (the link includes changes beyond the 1983 to 2009 timespan and cotiguous U.S. scope of this project, so I have also compiled the relevant data from this website in *census_county_changes.txt*)

Based on mapping the changes from the Census to the FIPS with less than 27 observations above, the following issues seem to arise that would impact comparing counties across time: 

1. Name changes that impact the alphabetical ordering of counties within a state and require a new FIPS code (e.g. Dade County, FL (12025) becoming (Miami-Dade Couinty, FL (12086))
2. Multiple counties being combined into a single new county / a single county being split into multiple counties (South Boston, VA (51780) being combined with Halifax County, VA (51083))
3. New counties being created from parts of exitsting counties (e.g. Broomfield County, CO (08014) from parts of Adams County, CO (08001), Boulder County, CO (08013), and Weld County, CO (08123))

However, an additional issue that is not apparent by comparoing FIPS code across time also becomes clear in the Census's county changes documentation:

4. Parts of counties being exchanged between existing counties 

The solution for the first issue is to simply pick one of the FIPS codes and make it uniform across time with the mapping. For the second issue, in somes years we have a single observation whereas in others years we have multiple observations representing subcomponents. So the options include combining the multiple obersvations in the earlier periods to have a comparable observation to the new single county or to split the single observation into the multiples. It is clearly better to combine the multiples, even considering the loss of information, becuase it does not require any data assumptions. If county C was created from county A and B, then there is no ambiguity about an observation composed of A+B being comparable with C. The alternative, splitting the single observation into multiples, requires some kind of assumption about how to allocate the value across the subcomponents. With the previous example, we could split the population value for C between A and B by refering to the ratio in a base year where we observed both A and B. However, in this case, the imputed values for A and B would only as good as the assumed ratio is constant over time. The same basic logic applies to the third and fourth issues and the non-ambigious solution is similarly aggregation. For the most part the application of this solution is trivial, however, a few cases arise (such as the creation of a mega-Denver county) that could pose an issue for someone interested in looking exclusively at Colorado). 

Some additional tweaks become clear when making the changes outlined above and looking over the data. The majority of the county changes catalogued by the Census relate to "independent cities" in Virginia. There are two other states with an "independent city": St. Louis in Missouri and Baltimore in Maryland. While at a minimum the cities that annexed/exchanged territory must be combined with their surrounding counties, it is clear that if you would like to use variables such as employment density that indpendent cities will become outliers. That is, they appear very dense compared to similar cities in other states that are combined with their surrounding county. Essentially, despite their categorization in Virginia law as not being a component of a county, when trying to construct a panel of roughly equivalently defined geographical units over space they do not fit in. So, it makes sense to combine all the independent cities with their surrounding county, which corrects for the changes and oddness. However, two independent “cities” are actually quite large in terms of land area (actually larger than some full-fledged counties) and are not really surrounded by any other single county (Suffolk and Virginia Beach) so it is most natural to keep them as "counties", especially since neither are subject to any geographic boundary changes over the time period. The list of all changes to be implemented in making the mapping are listed at the end of this docuemnt.

## Mapping example
While it is easy to add additional data to the panel once the crosswalk is made (just apply the crosswalk to the new data before merging), it is not quite as simple to combine the data with most map-making solutions. Say we want to use the data in our panel with consistent FIPS codes on the number of establishments and workers in each county in each year to calculate and then plot the average size (in terms of the number of employees) of establishments. It is simple to calculate this value for each county and then merge the data by FIPS codes with the [2010 county shapefile from the Census](https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.2010.html). While some changes to the FIPS codes will not be an issue for this mapping (e.g. Dade County, FL (12025) to Miami-Dade County, FL (12086)), any change that combines counties will cause an issue:

![naive plot](naive_plot.png)

The flaw in this naive approach to mapping the data is most apparent in Colorado: the average number of establishments for the new "Denver" county, which was necessitated due to the creation of Bloomfield County as well as some other territory exchanges, has only applied to the area of the actual Denver County, CO (08031)! However, because this observation in the data actually represents multiple counties, the average size of establishments in the new "Denver" county should be applied to the entire area. While it is possible to redefine the shapefile for this adjustment with software like (ArcGIS), this simplest solution is to simply apply the crosswalk in reverse once the appropriate calculations have been performed on the data, which results in the only missing values remaining on the map being the consequence of counties with zero reported workers in 2000:

![better plot](better_plot.png)

Much better to my eye!

## List of all changes for FIPS crosswalk
| Original FIPS | County | New FIPS | County | Desc |
| :---: | :---: | :---: | :---: | :---: |
| 08001 | Adams County, CO | 08031 | Denver County, CO |  | 
| 08013 | Boulder County, CO | 08031 | Denver County, CO |  | 
| 08014 | Broomfield County, CO | 08031 | Denver County, CO |  | 
| 08059 | Jefferson County, CO | 08031 | Denver County, CO |  | 
| 08123 | Weld County, CO | 08031 | Denver County, CO |  | 
| 12025 | Dade County, FL | 12086 | Miami-Dade County, FL | name change | 
| 24510 | Baltimore City, MD | 24005 | Baltimore County, MD | merge city with surrounding county | 
| 29510 | St Louis City, MO | 29189 | St Louis County, MO |  | 
| 31115 | Loup County, NE | 31071 | Garfield County, NE | combine county that is too small for wage/emp. data (pop. of 632 in 2010 Census) with neighboring county | 
| 31117 | McPherson County, NE | 31113 | Logan County,NE | combine county that is too small for wage/emp. data (pop. of 539 in 2010 Census) with neighboring county | 
| 48033 | Borden County, TX | 48415 | Scurry County, TX | combine county that is too small for wage/emp. data (pop. of 641 in 2010 Census) with neighboring county | 
| 48301 | Loving County, TX | 48389 | Reeves County, TX | combine county that is too small for wage/emp. data (pop. of 169  in 2010 Census) with neighboring county | 
| 51510 | Alexandria City, VA | 51059 | Fairfax County, VA | merge city with surrounding county | 
| 51515 | Bedford City, VA | 51019 | Bedford County, VA | merge city with surrounding county | 
| 51520 | Bristol City, VA | 51191 | Washington County, VA | merge city with surrounding county | 
| 51530 | Buena Vista City, VA | 51163 | Rockbridge County, VA | merge city with surrounding county | 
| 51540 | Charlottesville City, VA | 51003 | Albemarle County, VA | merge city with surrounding county | 
| 51550 | Chesapeake City, VA | 51710 | Norfolk City, VA | combine Chesapeake, Portsmouth, and Norfolk into Norfolk | 
| 51560 | Clifton Forge City, VA | 51005 | Alleghany County, VA | merge city with surrounding county | 
| 51570 | Colonial Heights City, VA | 51053 | Dinwiddie County, VA | merge city with surrounding county | 
| 51580 | Covington City, VA | 51005 | Alleghany County, VA | merge city with surrounding county | 
| 51590 | Danville City, VA | 51143 | Pittsylvania County, VA | merge city with surrounding county | 
| 51595 | Emporia City, VA | 51081 | Greensville County, VA | merge city with surrounding county | 
| 51600 | Fairfax City, VA | 51059 | Fairfax County, VA | merge city with surrounding county | 
| 51610 | Falls Church City, VA | 51059 | Fairfax County, VA | merge city with surrounding county | 
| 51620 | Franklin City, VA | 51175 | Southampton County, VA | merge city with surrounding county | 
| 51630 | Fredericksburg City, VA | 51177 | Spotsylvania County, VA | merge city with surrounding county | 
| 51640 | Galax City, VA | 51035 | Carroll County, VA | merge city with surrounding county | 
| 51650 | Hampton City, VA | 51199 | York County, VA | merge Hampton, Poquoson, and Newport News into York County, VA | 
| 51660 | Harrisonburg City, VA | 51165 | Rockingham County, VA | merge city with surrounding county | 
| 51670 | Hopewell City, VA | 51149 | Prince George County, VA | merge city with surrounding county | 
| 51678 | Lexington City, VA | 51163 | Rockbridge County, VA | merge city with surrounding county | 
| 51680 | Lynchburg City, VA | 51031 | Campbell County, VA | merge city with neighboring county | 
| 51683 | Manassas City, VA | 51153 | Prince William County, VA | merge city with surrounding county | 
| 51685 | Manassas Park City, VA | 51153 | Prince William County, VA | merge city with surrounding county | 
| 51690 | Martinsville City, VA | 51089 | Henry County, VA | merge city with surrounding county | 
| 51700 | Newport News City, VA | 51199 | York County, VA | merge Hampton, Poquoson, and Newport News into York County, VA | 
| 51720 | Norton City, VA | 51195 | Wise County, VA | merge city with surrounding county | 
| 51730 | Petersburg City, VA | 51053 | Dinwiddie County, VA | merge city with neighboring county | 
| 51735 | Poquoson City, VA | 51199 | York County, VA | merge Hampton, Poquoson, and Newport News into York County, VA | 
| 51740 | Portsmouth City, VA | 51710 | Norfolk City, VA | combine Chesapeake, Portsmouth, and Norfolk into Norfolk | 
| 51750 | Radford City, VA | 51121 | Montgomery County, VA | merge city with neighboring county | 
| 51760 | Richmond City, VA | 51087 | Henrico County, VA | merge city with neighboring county | 
| 51770 | Roanoke City, VA | 51161 | Roanoke County, VA | merge city with surrounding county | 
| 51775 | Salem City, VA | 51161 | Roanoke County, VA | merge city with surrounding county | 
| 51780 | South Boston City, VA | 51083 | Halifax County, VA | merge city with surrounding county | 
| 51790 | Staunton City, VA | 51015 | Augusta County, VA | merge city with surrounding county | 
| 51820 | Waynesboro City, VA | 51015 | Augusta County, VA | merge city with surrounding county | 
| 51830 | Williamsburg City, VA | 51095 | James City County, VA | merge city with neighboring county | 
| 51840 | Winchester City, VA | 51069 | Frederick County, VA | merge city with surrounding county | 
| 55078 | Menominee County, WI | 55115 | Shawano County, WI | merge county with neighboring county | 



