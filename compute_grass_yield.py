#!/usr/bin/env python

'''
Compute mean grass yield at a national scale based on FAOSTAT data
'''

import numpy as np
import pandas as pd
from common_data import read_FAOSTAT_df

#Compute average grass yield per country
country_pd=pd.read_csv("output/model_country.csv",index_col=0)
country_list=list(country_pd.values)
country_list.extend(list(country_pd.columns)

#Load grassland area
area_df=read_FAOSTAT_df("data/FAOSTAT_areas.csv")

#Aggregate grassland types
grassland_area_df=pd.DataFrame(columns=country_list)
for country in country_list:
    grassland_area_df.loc[0,country]=0.
    for grassland_type in np.unique(area_df['Item']):
        country_grass_mask=(area_df['Area']==country) & (area_df['Item']==grassland_type)
        if grassland_type in list(area_df.loc[area_df['Area']==country,'Item'].values):
            grassland_area_df.loc[0,country]+=area_df.loc[country_grass_mask,'Value'].values[0]

#Load animal number
animal_number_df=read_FAOSTAT_df("data/FAOSTAT_manure_management.csv",delimiter=",")

#Load feed share from gleam
feed_per_head_df=read_FAOSTAT_df("data/GLEAM_feed.csv")

#Compute grass yield
grass_yield_df=pd.DataFrame(columns=country_list)
for country in country_list:
    grass_quantity=0
    for item in np.unique(feed_per_head_df['Item']):
        grass_per_head=feed_per_head_df.loc[(feed_per_head_df['Country']==country) & (feed_per_head_df['Feed']=='Grass') & (feed_per_head_df['Item']==item),'Value']
        number_head=animal_number_df.loc[(animal_number_df['Area']==country) & (animal_number_df['Element']=='Stocks') & (animal_number_df['Item']==item),'Value']
        grass_quantity+=number_head.values[0]*grass_per_head.values[0]
    grass_yield_df[country]=grass_quantity/grassland_area_df[country]

grass_yield_df.to_csv('output/grass_yield.csv')
