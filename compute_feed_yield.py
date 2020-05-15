#! /bin/python

'''
Compute mean feed yield with national yield of every crops used to feed animals
'''

import numpy as np
import pandas as pd
from common_data import convert_unit_dict,read_FAOSTAT_df

#Data
# country_pd=pd.read_csv("output/model_country.csv",index_col=0)
# country_list=list(np.unique(country_pd.values))
# country_list.extend(list(country_pd.columns))
country_list=["France","Ireland","Brazil","India"]

#read yields
feed_yields_df=read_FAOSTAT_df("data/FAOSTAT_feed_yields.csv",delimiter="|")

#read share of feed demand nationaly produced
feed_share_trade_df=read_FAOSTAT_df("output/share_trade_feed.csv",index_col=0)

# read feed item
feed_demand_df=read_FAOSTAT_df("data/FAOSTAT_trade.csv",delimiter="|")
feed_mask=feed_demand_df["Element"]=="Feed"
feed_demand_df=feed_demand_df.loc[feed_mask,:]

# read feed item group to no group
FBS_group_df=pd.read_csv("data/FAOSTAT_FBS_group.csv",index_col='Item Group Code')

# read dict FBS to SUA
FBS_to_SUA_df=pd.read_csv("data/FAOSTAT_aggregation_all_primary_products.csv",delimiter='|',index_col='FBS_ItemCode')

#read FM to DM
FM_to_DM_df=pd.read_csv('data/feed_dry_matter.csv',index_col='ItemCode')

#aggregate yields base on item in feed
yields_df=pd.DataFrame(columns=country_list)
#Compute global yield of feed for each country
#Difference of yield between country is due of the crop mix
global_yields_df=pd.DataFrame(columns=country_list)
for country in country_list:
    feed_tot_demand=0;global_feed_tot_demand=0
    yields_df.loc[0,country]=0;global_yields_df.loc[0,country]=0
    country_mask=feed_demand_df["Country"]==country
    feed_item_list=list(feed_demand_df.loc[country_mask,'Item Code'])
    print(country)
    if country=="Ireland":
        feed_dict={};feed_yield_dict={}
    for feed in feed_item_list:
        if feed in FM_to_DM_df.index:
            FM_to_DM=FM_to_DM_df.loc[feed,'Value']
            if not isinstance(FM_to_DM_df.loc[feed,'Value'],np.float64):
                FM_to_DM=np.mean(FM_to_DM_df.loc[feed,'Value'].values)
        else:
            FM_to_DM=0.9
            #print(FBS_to_SUA_df.loc[feed,'SUA_ItemName,,'])
        if feed not in FBS_to_SUA_df.index:
            print(feed_demand_df.loc[feed_demand_df.loc[:,'Item Code']==feed,'Item'].values[0])
        else:
            if feed in feed_share_trade_df.loc[(feed_share_trade_df['Country']==country),'Item Code'].values:
                feed_share_trade=feed_share_trade_df.loc[(feed_share_trade_df['Element']=="Share production in total") & (feed_share_trade_df['Item Code']==feed) & (feed_share_trade_df['Country']==country),'Value'].values[0]
            else:
                feed_share_trade=0
            if type(FBS_to_SUA_df.loc[feed,'FBS_ItemName'])==str:
                SUA_item_list=[FBS_to_SUA_df.loc[feed,'SUA_ItemCode']]
            else:
                SUA_item_list=FBS_to_SUA_df.loc[feed,'SUA_ItemCode'].values
            if np.any(feed_yields_df.loc[(feed_yields_df['Area']==country),'Item Code'].isin(SUA_item_list)):
                feed_yield=np.mean(feed_yields_df.loc[(feed_yields_df.loc[(feed_yields_df['Area']==country),'Item Code'].isin(SUA_item_list)) & (feed_yields_df['Area']==country),'Value'].values)
            else:
                feed_yield=0
            global_feed_yield=np.mean(feed_yields_df.loc[(feed_yields_df.loc[(feed_yields_df['Area']=="World"),'Item Code'].isin(SUA_item_list)) & (feed_yields_df['Area']=="World"),'Value'])
            if np.any(feed_demand_df.loc[(feed_demand_df['Country']==country),'Item Code'].isin([feed])):
                feed_tot_demand+=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Country']==country),'Value'].values[0]*feed_share_trade
                global_feed_tot_demand+=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Country']==country),'Value'].values[0]*(1-feed_share_trade)
                yields_df.loc[0,country]+=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Country']==country),'Value'].values[0]*feed_share_trade*feed_yield*FM_to_DM
                global_yields_df.loc[0,country]+=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Country']==country),'Value'].values[0]*(1-feed_share_trade)*global_feed_yield*FM_to_DM
                #Print in the article yields and share for each crop in the feed mix
                # if country=="Ireland":
                #     if type(FBS_to_SUA_df.loc[feed,'FBS_ItemName'])==str:
                #         if FBS_to_SUA_df.loc[feed,'FBS_ItemName'] not in feed_dict.keys():
                #             feed_yield_dict[FBS_to_SUA_df.loc[feed,'FBS_ItemName']]=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Area']==country),'Value'].values[0]*feed_yield
                #             feed_dict[FBS_to_SUA_df.loc[feed,'FBS_ItemName']]=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Area']==country),'Value'].values[0]
                #         else:
                #             feed_yield_dict[FBS_to_SUA_df.loc[feed,'FBS_ItemName']]+=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Area']==country),'Value'].values[0]*feed_yield
                #             feed_dict[FBS_to_SUA_df.loc[feed,'FBS_ItemName']]+=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Area']==country),'Value'].values[0]
                #     else:
                #         if FBS_to_SUA_df.loc[feed,'FBS_ItemName'].values[0] not in feed_dict.keys():
                #             feed_yield_dict[FBS_to_SUA_df.loc[feed,'FBS_ItemName'].values[0]]=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Area']==country),'Value'].values[0]*feed_yield
                #             feed_dict[FBS_to_SUA_df.loc[feed,'FBS_ItemName'].values[0]]=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Area']==country),'Value'].values[0]
                #         else:
                #             feed_yield_dict[FBS_to_SUA_df.loc[feed,'FBS_ItemName'].values[0]]+=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Area']==country),'Value'].values[0]*feed_yield
                #             feed_dict[FBS_to_SUA_df.loc[feed,'FBS_ItemName'].values[0]]+=feed_demand_df.loc[(feed_demand_df['Item Code']==feed) & (feed_demand_df['Area']==country),'Value'].values[0]
    if yields_df.loc[0,country]==0:
        yields_df.loc[0,country]=0
    else:
        yields_df.loc[0,country]=yields_df.loc[0,country]/feed_tot_demand
    global_yields_df.loc[0,country]=global_yields_df.loc[0,country]/global_feed_tot_demand
yields_df.to_csv('output/feed_yield_aggregate.csv')
global_yields_df.to_csv('output/feed_yield_global_aggregate.csv')
