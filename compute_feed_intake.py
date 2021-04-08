#!/usr/bin/env python

'''
Compute feed intake per head per animal
Dairy cattle in FAOSTAT is represented by female adult in Gleam
Non-dairy cattle in FAOSTAT is represented by average of non-dairy system in Gleam 
Feed intake for sheep and monogastric are directed extracted from Gleam
'''

import numpy as np
import pandas as pd
from common_data import read_FAOSTAT_df

def compute_feed_intake_simplified_IPCC_computation(body_weight_df,digestibility_energy_df,country,item):
    body_weight_mask=(body_weight_df["Country"]==country) & (body_weight_df["Item"]==item)
    digestibility_energy_mask=(digestibility_energy_df["Country"]==country)
    dry_matter_intake = ((5.4 * body_weight_df.loc[body_weight_mask,"Value"]*1000)/500)/((1-digestibility_energy_df.loc[digestibility_energy_mask,"Value"])/1)*365/1000
    return dry_matter_intake.values[0]

#Country studied in the article
country_list=["France","Ireland","Brazil","India"]

#Load feed share from gleam
feed_per_head_df=read_FAOSTAT_df("data/GLEAM_feed.csv",index_col=0)

#Compute total intake for dairy and non dairy cattle of FAOSTAT
#Load body weight from Gleam
body_weight_df=read_FAOSTAT_df("data/GLEAM_body_weight.csv")
#Load share of concentrate and grass in ration
share_feed_in_ration_df=read_FAOSTAT_df("data/GLEAM_ration.csv")

#Load digestibility from litterature
digestibility_energy_df=read_FAOSTAT_df("data/digestibility_energy.csv")

feed_intake_df=pd.DataFrame(columns=feed_per_head_df.columns)
index=0
for country in country_list:
    for item in np.unique(feed_per_head_df['Item']):
        for feed in ["Grass","Grains"]:
            feed_intake_df.loc[index,"Country"]=country
            feed_intake_df.loc[index,"Feed"]=feed
            feed_intake_df.loc[index,"Item"]=item
            feed_intake_df.loc[index,"Unit"]="t/Head"  
            if "Cattle, dairy" in item:
                feed_intake_df.loc[index,"Value"]=share_feed_in_ration_df.loc[(share_feed_in_ration_df["Country"]==country) & (share_feed_in_ration_df["Feed"]==feed) & (share_feed_in_ration_df["Item"]==item),"Value"].values[0]*compute_feed_intake_simplified_IPCC_computation(body_weight_df,digestibility_energy_df,country,item)
            else:
                feed_intake_df.loc[index,"Value"]=feed_per_head_df.loc[(feed_per_head_df['Country']==country) & (feed_per_head_df['Feed']==feed) & (feed_per_head_df['Item']==item),'Value'].values[0]
            index+=1
        
feed_intake_df.to_csv('output/GLEAM_feed.csv')