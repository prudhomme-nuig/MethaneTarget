#!/usr/bin/env python

'''
Compute deforesattion emission factor based on IPCC methodology
for countries with the highest agricultural exapnsion during these
last 10 years
'''

import pandas as pd
import numpy as np
from common_data import read_FAOSTAT_df
from copy import deepcopy

last_year=2017
first_year=2008

country_list=["France","Ireland","Brazil","India"]
agricultural_df=read_FAOSTAT_df("data/FAOSTAT_agricultural_expansion.csv")
agricultural_expansion_df=pd.DataFrame(columns=["Area","Value"])
agricultural_expansion_df["Value"]=(agricultural_df.loc[agricultural_df["Year"]==last_year,"Value"].values-agricultural_df.loc[agricultural_df["Year"]==first_year,"Value"].values)*1E-6
agricultural_expansion_df["Area"]=agricultural_df.loc[agricultural_df["Year"]==last_year,"Area"].values
agricultural_selection=agricultural_expansion_df.nlargest(6, ['Value']).drop(43)

deforestation_df=read_FAOSTAT_df("data/FAOSTAT_deforestation.csv")
mask=(deforestation_df["Element"]=="Net emissions/removals (CO2) (Forest land)") & (deforestation_df["Item"]=="Net Forest conversion")
cumulative_emission_pd=deepcopy(deforestation_df.loc[mask,:])
mask=(deforestation_df["Element"]=="Area") & (deforestation_df["Item"]=="Net Forest conversion")
cumulative_deforestation_pd=deepcopy(deforestation_df.loc[mask,:])
for country in np.unique(agricultural_selection["Area"]):
    country_emission_mask=cumulative_emission_pd["Area"]==country
    country_deforestation_mask=cumulative_deforestation_pd["Area"]==country
    emission_sum=0; deforestation_sum=0
    for year in np.arange(first_year,last_year+1):
        if year in cumulative_emission_pd.loc[country_emission_mask,"Year"].values:
            emission_sum+=deepcopy(cumulative_emission_pd.loc[country_emission_mask & (cumulative_emission_pd["Year"]==year),"Value"].values[0])
            deforestation_sum+=deepcopy(cumulative_deforestation_pd.loc[country_deforestation_mask & (cumulative_deforestation_pd["Year"]==year),"Value"].values[0])
    cumulative_emission_pd.loc[country_emission_mask & (cumulative_emission_pd["Year"]==first_year),"Value"]=deepcopy(emission_sum)
    cumulative_deforestation_pd.loc[country_deforestation_mask & (cumulative_deforestation_pd["Year"]==first_year),"Value"]=deepcopy(deforestation_sum)
emission_deforestation_df=cumulative_deforestation_pd.loc[cumulative_deforestation_pd["Area"].isin(agricultural_selection["Area"].values),:]

total_deforestation=[];total_emission=[]
for country in agricultural_selection["Area"].values:
    print (country)
    mask=(cumulative_deforestation_pd["Year"]==first_year) & (cumulative_deforestation_pd["Area"]==country)
    emission_factor=np.sum(emission_deforestation_df.loc[emission_deforestation_df['Area']==country,"Value"].values)/np.sum(cumulative_deforestation_pd.loc[mask,'Value'].values)
    mask=(deforestation_df["Element"]=="Net emissions/removals (CO2) (Forest land)") & (deforestation_df["Item"]=="Net Forest conversion")
    total_emission.extend(deforestation_df.loc[mask & (deforestation_df["Area"]==country),'Value'].values)
    mask=(deforestation_df["Element"]=="Area") & (deforestation_df["Item"]=="Net Forest conversion")
    total_deforestation.extend(deforestation_df.loc[mask & (deforestation_df["Area"]==country),'Value'].values)
mean_emission_factor_df=pd.DataFrame(columns=["World"])
mean_emission_factor_df["World"]=[np.sum(total_emission)/np.sum(total_deforestation)/20]
for country in country_list:
    if cumulative_deforestation_pd.loc[cumulative_deforestation_pd["Area"]==country,"Value"].sum()>0:
        mean_emission_factor_df[country]=cumulative_emission_pd.loc[(cumulative_emission_pd["Area"]==country),"Value"].sum()/cumulative_deforestation_pd.loc[cumulative_deforestation_pd["Area"]==country,"Value"].sum()/20
    else:
        mean_emission_factor_df[country]=mean_emission_factor_df["World"]

mean_emission_factor_df.to_csv("output/deforestation_factor.csv")
