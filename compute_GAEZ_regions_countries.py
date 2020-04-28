#! /bin/python

'''
For each country, look for the dominant GAEZ and list all countries in this GAEZ with a share > 50%
'''

import pandas as pd
from common_data import read_FAOSTAT_df

GAEZ_df=pd.read_csv("data/GAEZ_thermal_zone.csv",encoding="utf-8")
country_list=["France","Ireland","Brazil","India"]

GAEZ_share=GAEZ_df.iloc[:,2:].divide(GAEZ_df.iloc[:,1],axis=0)
GAEZ_share.index=GAEZ_df["Country"].values
GAEZ_country_dict={};country_in_same_GAEZ={};country_in_GAEZ={}
for country in country_list:
    GAEZ_series=GAEZ_df.loc[GAEZ_df["Country"]==country,:]
    GAEZ_country_dict[country]=GAEZ_share.loc[country,:].idxmax(1)
    GAEZ_mask=GAEZ_share.loc[:,GAEZ_country_dict[country]]>0.5
    country_in_same_GAEZ[country]=GAEZ_share.loc[GAEZ_mask,:].index.values
    if GAEZ_share.loc[country,:].idxmax(1) not in country_in_GAEZ.keys():
        country_in_GAEZ[GAEZ_share.loc[country,:].idxmax(1)]=GAEZ_share.loc[GAEZ_mask,:].index.values

country_in_same_GAEZ_pd=pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in country_in_same_GAEZ.items() ]))
country_in_same_GAEZ_pd.to_csv("output/country_in_same_GAEZ.csv")
GAEZ_of_country_pd=pd.DataFrame.from_dict(dict([ (k,pd.Series(v)) for k,v in GAEZ_country_dict.items() ]))
GAEZ_of_country_pd.to_csv("output/GAEZ_country.csv")
country_in_GAEZ_pd=pd.DataFrame.from_dict(dict([ (k,pd.Series(v)) for k,v in country_in_GAEZ.items() ]))
country_in_GAEZ_pd.to_csv("output/GAEZ_list_country.csv")
