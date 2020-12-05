# Uniform Counties
Mapping for uniform FIPS codes (U.S. counties) from 1983 to 2009 for the contiguous U.S.

## Description

First, the script *get_qcew.py* downloads annual files for the Quarterly Census of Employment and Wages ([QCEW](https://www.bls.gov/cew/downloadable-data-files.htm)) from the Bureau of Labor Statistics (BLS). While the BLS has a nice [API]() for fetching specific data from the QCEW, it only features the more recent data, so this script directly downloads the annual files.

In these files, individual counties are indexed by Federal Information Processing System ([FIPS](https://transition.fcc.gov/oet/info/maps/census/fips/fips.txt)) codes. FIPS codes are unique 5-digit identifiers: the first two digits refer to the state (in alphabetical order) and the last three refer to the county within the state (also in alphabetical order using odd numbers, e.g. 001 for Autauga County, AL followed by 003 for Baldwin County, AL). In some states the corresponding geographical area has an alternative name such as boroughs in Alaska and parishes in Louisiana. Three states have a unqiue FIPS code for at least one independent city and there will be more on that later.

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

Some additional tweaks become clear when making the changes outlined above and looking over the data. The majority of the county changes catalogued by the Census relate to "independent cities" in Virginia. There are two other states with an "independent city": St. Louis in Missouri and Baltimore in Maryland. While at a minimum the cities that partoke in annexations/exchanges must be combined with their surrounding counties it becomes clear that if you would like to use variables such as employment density indpendent cities become outliers. That is, they appear very dense compared to similar cities in other states that are combined with their surrounding county. Essentially, despite their categorization in Virginia law as not being a component of a county, when trying to construct a panel roughly equivalently defined geographical units over space they do not fit. So, it makes sense to combine all the independent cities with their surrounding county, which corrects for the changes and oddness. However, two independent “cities” are actually quite large in terms of land area (actually larger than some full-fledged counties) and are not really surrounded by any other single county (Suffolk and Virginia Beach) so it is most natural to keep them as "counties", especially since neither are subject to any geographic boundary changes over the time period.

In total the changes to be implemented in making the mapping are as follows:

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
