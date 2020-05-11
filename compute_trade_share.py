#! /bin/python

'''
Compute share in trade of net imported feed and domestically produced feed
'''

import pandas as pd
from common_data import read_FAOSTAT_df
import numpy as np
#import argparse

#Food balance sheets of FAOSTAT
#Include Feed, domestic production, import, export and change in stock
FB_df=read_FAOSTAT_df("data/FAOSTAT_trade.csv",delimiter='|')
FB_df=FB_df.drop("Domain",axis=1)

#List of country
country_intensification_pd=pd.read_csv("output/model_country.csv",index_col=0)
country_list=list(country_intensification_pd.columns)

output_df=pd.DataFrame(columns=FB_df.columns);index=0
feed_element_mask=FB_df["Element"]=="Feed"
total_share_trade=pd.DataFrame(columns=country_list)
for country in country_list:
    country_mask=FB_df["Country"]==country
    no_null_feed_mask=((FB_df["Value"]>0 ) & feed_element_mask)
    feed_list=np.unique(FB_df.loc[country_mask & no_null_feed_mask,"Item"].values)
    total_national_production=0
    total_production=0
    other=0
    for feed in feed_list:
        feed_mask=FB_df["Item"]==feed
        production_mask=FB_df["Element"]=="Production"
        stock_mask=FB_df["Element"]=="Stock Variation"
        import_mask=FB_df["Element"]=="Import Quantity"
        export_mask=FB_df["Element"]=="Export Quantity"
        total=FB_df.loc[country_mask & feed_mask & production_mask,"Value"].values[0]+FB_df.loc[country_mask & feed_mask & import_mask,"Value"].values[0]-FB_df.loc[country_mask & feed_mask & export_mask,"Value"].values[0]
        total_with_stock=FB_df.loc[country_mask & feed_mask & production_mask,"Value"].values[0]+FB_df.loc[country_mask & feed_mask & stock_mask,"Value"].values[0]+FB_df.loc[country_mask & feed_mask & import_mask,"Value"].values[0]-FB_df.loc[country_mask & feed_mask & export_mask,"Value"].values[0]
        production=FB_df.loc[country_mask & feed_mask & production_mask,"Value"]
        total_national_production+=production.values[0]
        total_production+=total
        share_production=production.values[0]/total
        output_df=output_df.append(FB_df.loc[country_mask & feed_mask & production_mask,:],ignore_index=True)
        output_df.loc[index,"Element"]="Share production in total"
        output_df.loc[index,"Value"]=share_production
        output_df.loc[index,"Unit"]=""
        index+=1
        feed_quantity=FB_df.loc[country_mask & feed_mask & feed_element_mask,"Value"]
        share_feed=feed_quantity.values[0]/total_with_stock
        if share_feed>1:
            print(feed+" in "+country+" : "+str(share_feed))
            share_feed=1
        output_df=output_df.append(FB_df.loc[country_mask & feed_mask & production_mask,:],ignore_index=True)
        other+=production.values[0]-feed_quantity.values[0]
        output_df.loc[index,"Element"]="Share feed in total"
        output_df.loc[index,"Value"]=share_feed
        output_df.loc[index,"Unit"]=""
        index+=1
    total_share_trade.loc["Share feed demand domestically produced",country]=np.min([total_national_production/total_production,1])
    total_share_trade.loc["Crop other",country]=other
output_df.to_csv("output/share_trade_feed.csv")
total_share_trade.to_csv("output/trade_aggregate_feed.csv")
