#! /bin/python

import numpy as np
import pandas as pd
from common_data import convert_unit_dict,read_FAOSTAT_df

#Data
country_list=["Ireland","France","India","Brazil","Netherlands"]

#read yields
feed_yields_df=read_FAOSTAT_df("data/FAOSTAT_feed_yields.csv")

# read feed item
feed_demand_df=read_FAOSTAT_df("data/FAOSTAT_feed_item.csv")
#Gleam-i user guide
#grain_list=[Pulses,Cassava,Wheat,Maize,Barley,Millet,Sorghum,Rice,Rapeseed,Banana fruit]
#grain_list=['Peas','Cassava','Wheat','Maize','Barley','Millet','Sorghum','Rice','Rapeseed','Bananas']
grain_list=[2547,2532,2511,2514,2513,2517,2518,2804,2804,2615]

# read feed item group to no group
FBS_group_df=pd.read_csv("data/FAOSTAT_FBS_group.csv",index_col='Item Group Code')

# read dict FBS to SUA
FBS_to_SUA_df=pd.read_csv("data/FAOSTAT_aggregation_all_primary_products.csv",delimiter='|',index_col='FBS_ItemCode')

#read FM to DM
FM_to_DM_df=pd.read_csv('data/feed_dry_matter.csv',index_col='ItemCode')

#aggregate yields base on item in feed
yields_df=pd.DataFrame(columns=country_list)
for country in country_list:
    feed_tot_demand=0
    yields_df.loc[0,country]=0
    feed_item_list=grain_list
    for feed in feed_item_list:
        if feed in FM_to_DM_df.index:
            FM_to_DM=FM_to_DM_df.loc[feed,'Value']
        else:
            FM_to_DM=0.9
            print(FBS_to_SUA_df.loc[feed,'SUA_ItemName'])
        if feed not in FBS_to_SUA_df.index:
            print(feed)
        else:
            if not isinstance(FM_to_DM_df.loc[feed,'Value'],np.float64):
                FM_to_DM=np.mean(FM_to_DM_df.loc[feed,'Value'].values)
            if np.any(feed_yields_df.loc[(feed_yields_df['Area']==country),'Item Code'].isin([FBS_to_SUA_df.loc[feed,'SUA_ItemCode']])):
                feed_yield=feed_yields_df.loc[(feed_yields_df['Item Code']==FBS_to_SUA_df.loc[feed,'SUA_ItemCode']) & (feed_yields_df['Area']==country),'Value'].values[0]
            else:
                feed_yield=0
            if np.any(feed_demand_df.loc[(feed_demand_df['Area']==country),'Item Code'].isin([feed])):
                feed_tot_demand+=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Area']==country),'Value'].values[0]
                yields_df.loc[0,country]+=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Area']==country),'Value'].values[0]*feed_yield*FM_to_DM
    yields_df.loc[0,country]=yields_df.loc[0,country]/feed_tot_demand
yields_df.to_csv('output/feed_yield_aggregate.csv')