#!/usr/bin/env python

'''
Compute mean grass yield at a national scale based on FAOSTAT data
'''

import numpy as np
import pandas as pd
from common_data import read_FAOSTAT_df

#Load grassland area
area_df=read_FAOSTAT_df("data/FAOSTAT_areas.csv")
N_fertilizer_use_df=read_FAOSTAT_df("data/FAOSTAT_N_fertilizer.csv")
coef_fertilizer_crop=3

#Aggregate different type of Grassland
grassland_aggregate={"Grassland":["Land under temp. meadows and pastures","Land with temporary fallow","Land under perm. meadows and pastures"]}
country_list=list(np.unique(area_df["Area"].values))
for country in country_list:
    country_mask=area_df["Area"]==country
    tmp_mak= country_mask & (area_df["Item"]=="Cropland")
    row_to_add=area_df.loc[tmp_mak,:]
    row_to_add.loc[:,"Item"]="Grassland"
    area_grassland_total=0
    for grassland_type in grassland_aggregate["Grassland"]:
        mask_grassland=area_df["Item"]==grassland_type
        area_grassland_total+=area_df.loc[country_mask & mask_grassland,"Value"].values[0]
    row_to_add.loc[:,"Value"]=area_grassland_total
    area_df = area_df.append(row_to_add,ignore_index=True)

mask_cropland = area_df["Item"]=="Cropland"
mask_pasture = area_df["Item"]=="Grassland"

N_fertilizer_rate_df=pd.DataFrame(columns=area_df.columns)
for country in country_list:
    row_to_add["Area"]=country
    row_to_add["Element"]="Fertilizer rate"
    row_to_add["Unit"]="tN/ha"
    mask_country=area_df["Area"]==country
    cropland_mask=area_df["Item"]=="Cropland"
    grassland_mask=area_df["Item"]=="Grassland"
    area_tot=coef_fertilizer_crop*area_df.loc[cropland_mask & mask_country,"Value"].values[0]+area_df.loc[grassland_mask & mask_country,"Value"].values[0]
    row_to_add.loc[:,"Item"]="Cropland"
    row_to_add.loc[:,"Value"]=coef_fertilizer_crop*N_fertilizer_use_df.loc[N_fertilizer_use_df['Area']==country,"Value"].values[0]/area_tot
    if area_tot==0:
        row_to_add.loc[:,"Value"]=0
    N_fertilizer_rate_df=N_fertilizer_rate_df.append(row_to_add,ignore_index=True)
    row_to_add.loc[:,"Item"]="Grassland"
    row_to_add.loc[:,"Value"]=N_fertilizer_use_df.loc[N_fertilizer_use_df['Area']==country,"Value"].values[0]/area_tot
    if area_tot==0:
        row_to_add.loc[:,"Value"]=0
    N_fertilizer_rate_df=N_fertilizer_rate_df.append(row_to_add,ignore_index=True)

N_fertilizer_rate_df.to_csv("output/N_fertilizer_rate.csv")
