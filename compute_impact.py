#! /bin/python

import pandas as pd
from common_data import read_FAOSTAT_df
from copy import deepcopy
import argparse

parser = argparse.ArgumentParser('Compute impacts of different national level activity on production, areas, emissions...')
parser.add_argument('--sensitivity-analysis', help='Yields can be +50 or -50')

args = parser.parse_args()

if args.sensitivity_analysis is not None:
    yield_change=float(args.sensitivity_analysis)/100.
    file_name_suffix='_yield'+args.sensitivity_analysis
else:
    yield_change=0
    file_name_suffix=''
    
demand_dict={'Grass':['Grassland area'],'Grain':['Feed prodution','Cropland area (Feed)']}
#,'Rice, paddy':['prodution','area']
production_dict={'Cattle':['Milk, Total','Beef and Buffalo Meat'],'Rice, paddy':['Rice, paddy'],'Swine':['Meat, pig'],'Chickens':['Meat, Poultry','Eggs Primary'],'Sheep and Goats':['Sheep and Goat Meat']}
item_list=['Cattle','Swine','Chickens','Sheep and Goats'] #'Rice, paddy'
country_list=["Ireland","France","India","Brazil"]
yield_dict={'Milk, Total':'Yield','Beef and Buffalo Meat':'Yield/Carcass Weight','Meat, pig':'Yield/Carcass Weight','Meat, Poultry':'Yield/Carcass Weight','Eggs Primary':'Yield','Sheep and Goat Meat':'Yield/Carcass Weight'}
animal_producing_dict={'Milk, Total':'Milk Animals','Beef and Buffalo Meat':'Producing Animals/Slaughtered','Meat, pig':'Producing Animals/Slaughtered','Meat, Poultry':'Producing Animals/Slaughtered','Eggs Primary':'Laying','Sheep and Goat Meat':'Producing Animals/Slaughtered'}
pathway_dict={"Ireland":["Ireland","Netherlands"],
            "France":["France","Netherlands"],
            "India":["India","Brazil"],
            "Brazil":["Brazil"]}
ruminant_list=['Cattle','Sheep and Goats']
production_aggregation_dict={'Milk':['Milk, Total'],'Meat':['Beef and Buffalo Meat','Meat, pig','Meat, Poultry','Sheep and Goat Meat'],'Eggs':['Eggs Primary']}
activity_df=pd.read_csv("output/activity_2050.csv")
activity_ref_df=read_FAOSTAT_df("data/FAOSTAT_manure_management.csv")
yields_df=read_FAOSTAT_df("data/FAOSTAT_yields.csv")
feed_per_head_df=read_FAOSTAT_df("data/GLEAM_feed.csv")
yield_feed_df=pd.read_csv("output/feed_yield_aggregate.csv")
yield_grass_df=pd.read_csv("output/grass_yield.csv")
density_df=pd.read_csv("output/density_livestock.csv",index_col=[0])
area_df=pd.read_csv("data/FAOSTAT_areas.csv",index_col=[0])
yield_rice_df=read_FAOSTAT_df("data/FAOSTAT_rice.csv")
grassland_area_df=pd.read_csv('output/grassland_area.csv')
kha_to_ha=1E3
climatic_region={"India":"Tropical","Brazil":"Tropical","Ireland":"Temperate","France":"Temperate"}
carbon_growth_rate={"Tropical":4.86*48./12.,"Temperate":2.8*48./12.}

#Change yield depending on the sensitivty analysis
new_yield_feed_df=pd.DataFrame(columns=yield_feed_df.columns.values)
for country in country_list:
    new_yield_feed_df[country]=yield_feed_df[country]*(1+yield_change)

for country in country_list:
    for pathway in pathway_dict[country]:
        country_pathway_mask=deepcopy((activity_df['Country']==country) & (activity_df['Pathways']==pathway))
        activity_df.loc[country_pathway_mask,'Grassland area']=0
        activity_df.loc[country_pathway_mask,'Grassland area 2010']=0
        for item in item_list:
            if item not in ruminant_list:
                pathway_tmp=country
            else:
                pathway_tmp=pathway
            for production in production_dict[item]:
                animal_producing=yields_df.loc[(yields_df['Area']==pathway_tmp) & (yields_df['Element']==animal_producing_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
                animal_number_ref=activity_ref_df.loc[(activity_ref_df['Area']==pathway_tmp) & (activity_ref_df['Element']=='Stocks') & (activity_ref_df['Item']==item),'Value'].values[0]
                share_animal_producing=animal_producing/animal_number_ref
                yields=yields_df.loc[(yields_df['Area']==pathway_tmp) & (yields_df['Element']==yield_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
                yields_ref=yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==yield_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
                animal_number=activity_df.loc[country_pathway_mask,'Activity manure '+item].values
                activity_df.loc[country_pathway_mask,production]=yields*share_animal_producing*animal_number
                animal_producing_ref=yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==animal_producing_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
                activity_df.loc[country_pathway_mask,production+' 2010']=yields_ref*animal_producing_ref

            #Feed production
            feed='Grains'
            country_pathway_item_feed_mask=(feed_per_head_df['Country']==country) & (feed_per_head_df['Item']==item) & (feed_per_head_df['Feed']==feed)
            activity_df.loc[country_pathway_mask,'Feed production '+item]=feed_per_head_df.loc[country_pathway_item_feed_mask,'Value'].values[0]*animal_number
            animal_number_ref=activity_ref_df.loc[(activity_ref_df['Area']==country) & (activity_ref_df['Item']==item) & (activity_ref_df['Element']=='Stocks'),'Value'].values[0]
            activity_df.loc[country_pathway_mask,'Feed production 2010 '+item]=feed_per_head_df.loc[(feed_per_head_df['Country']==country) & (feed_per_head_df['Item']==item) & (feed_per_head_df['Feed']==feed),'Value'].values[0]*animal_number_ref
            #Feed yield
            activity_df.loc[country_pathway_mask,'Feed yield '+item]=new_yield_feed_df.loc[0,country]
            activity_df.loc[country_pathway_mask,'Feed yield 2010 '+item]=yield_feed_df.loc[0,country]
            #Grassland area
            activity_df.loc[country_pathway_mask,'Grassland area '+item]=animal_number*feed_per_head_df.loc[(feed_per_head_df['Country']==country) & (feed_per_head_df['Item']==item) & (feed_per_head_df['Feed']=='Grass'),'Value'].values[0]/yield_grass_df.loc[0,pathway]
            activity_df.loc[country_pathway_mask,'Grassland area 2010 '+item]=animal_number_ref*feed_per_head_df.loc[(feed_per_head_df['Country']==country) & (feed_per_head_df['Item']==item) & (feed_per_head_df['Feed']=='Grass'),'Value'].values[0]/yield_grass_df.loc[0,country]
            activity_df.loc[country_pathway_mask,'Grassland area']+=activity_df.loc[country_pathway_mask,'Grassland area '+item]
            activity_df.loc[country_pathway_mask,'Grassland area 2010']+=activity_df.loc[country_pathway_mask,'Grassland area 2010 '+item]
        activity_df.loc[country_pathway_mask,'Grassland area index']=activity_df.loc[country_pathway_mask,'Grassland area']/activity_df.loc[country_pathway_mask,'Grassland area 2010']
        activity_df.loc[country_pathway_mask & (activity_df.loc[country_pathway_mask,'Grassland area 2010']==0),'Grassland area index']=0
        #Livestock area
        #activity_df.loc[country_pathway_mask,'Livestock area']=activity_df.loc[country_pathway_mask,'Grassland area']+activity_df.loc[country_pathway_mask,'Feed area']
        for production_aggregate in production_aggregation_dict.keys():
            activity_df.loc[country_pathway_mask,production_aggregate]=0
            activity_df.loc[country_pathway_mask,production_aggregate+' 2010']=0
            for production_aggregated in production_aggregation_dict[production_aggregate]:
                activity_df.loc[country_pathway_mask,production_aggregate]+=activity_df.loc[country_pathway_mask,production_aggregated]
                activity_df.loc[country_pathway_mask,production_aggregate+' 2010']+=activity_df.loc[country_pathway_mask,production_aggregated+' 2010']
        item='Rice, paddy'
        #Rice area
        activity_df.loc[country_pathway_mask,'Rice area']=activity_df.loc[country_pathway_mask,'Activity rice Rice, paddy']
        activity_df.loc[country_pathway_mask,'Rice area 2010']=yield_rice_df.loc[(yield_rice_df['Area']==country) & (yield_rice_df['Element']=='Area harvested'),'Value'].values[0]
        activity_df.loc[country_pathway_mask,'Rice area index']=activity_df.loc[country_pathway_mask,'Rice area']/activity_df.loc[country_pathway_mask,'Rice area 2010']
        activity_df.loc[country_pathway_mask & (activity_df.loc[country_pathway_mask,'Rice area 2010']==0),'Rice area index']=0
        activity_df.loc[country_pathway_mask,'Spared Rice area']=activity_df.loc[country_pathway_mask,'Rice area']-activity_df.loc[country_pathway_mask,'Rice area 2010']
        #Rice production
        activity_df.loc[country_pathway_mask,'Production '+item]=activity_df.loc[country_pathway_mask,'Rice area']*yield_rice_df.loc[(yield_rice_df['Area']==country) & (yield_rice_df['Element']=='Yield'),'Value'].values[0]
        activity_df.loc[country_pathway_mask,'Production '+item+' 2010']=activity_df.loc[country_pathway_mask,'Rice area 2010']*yield_rice_df.loc[(yield_rice_df['Area']==country) & (yield_rice_df['Element']=='Yield'),'Value'].values[0]
        activity_df.loc[country_pathway_mask,'Yield '+item]=yield_rice_df.loc[(yield_rice_df['Area']==country) & (yield_rice_df['Element']=='Yield'),'Value'].values[0]
        #Total production
        activity_df.loc[country_pathway_mask,'Total production']=0
        activity_df.loc[country_pathway_mask,'Total production 2010']=0
        for production in ['Milk','Meat','Eggs','Production Rice, paddy']:
            activity_df.loc[country_pathway_mask,'Total production']+=activity_df.loc[country_pathway_mask,production]
            activity_df.loc[country_pathway_mask,'Total production 2010']+=activity_df.loc[country_pathway_mask,production+' 2010']
        #Spared land
        activity_df.loc[country_pathway_mask,'Spared Grassland area']=0
        activity_df.loc[country_pathway_mask,'Spared Feed area']=0
        activity_df.loc[country_pathway_mask,'Feed area']=0
        activity_df.loc[country_pathway_mask,'Feed area 2010']=0
        for item in item_list:
            if item in ruminant_list:
                activity_df.loc[country_pathway_mask,'Spared Grassland area']+=activity_df.loc[country_pathway_mask,'Grassland area 2010 '+item]-activity_df.loc[country_pathway_mask,'Grassland area '+item]
            activity_df.loc[country_pathway_mask,'Feed area 2010']+=activity_df.loc[country_pathway_mask,'Feed production 2010 '+item]/yield_feed_df[country].values[0]
            activity_df.loc[country_pathway_mask,'Feed area']+=(activity_df.loc[country_pathway_mask,'Feed production '+item])/activity_df.loc[country_pathway_mask,'Feed yield '+item].values[0]
            activity_df.loc[country_pathway_mask,'Spared Feed area']+=activity_df.loc[country_pathway_mask,'Feed area']-activity_df.loc[country_pathway_mask,'Feed area 2010']
        activity_df.loc[country_pathway_mask,'Feed area index']=activity_df.loc[country_pathway_mask,'Feed area']/activity_df.loc[country_pathway_mask,'Feed area 2010']
        activity_df.loc[country_pathway_mask & (activity_df.loc[country_pathway_mask,'Feed area 2010']==0),'Feed area index']=0
        activity_df.loc[country_pathway_mask,'Spared Total area']=activity_df.loc[country_pathway_mask,'Spared Grassland area']+activity_df.loc[country_pathway_mask,'Spared Feed area']+activity_df.loc[country_pathway_mask,'Spared Rice area']
        activity_df.loc[country_pathway_mask,'Total area']=activity_df.loc[country_pathway_mask,'Grassland area']+activity_df.loc[country_pathway_mask,'Feed area']+activity_df.loc[country_pathway_mask,'Rice area']
        activity_df.loc[country_pathway_mask,'Total area 2010']=activity_df.loc[country_pathway_mask,'Grassland area 2010']+activity_df.loc[country_pathway_mask,'Feed area 2010']+activity_df.loc[country_pathway_mask,'Rice area 2010']
        activity_df.loc[country_pathway_mask,'Total area index']=activity_df.loc[country_pathway_mask,'Total area']/activity_df.loc[country_pathway_mask,'Total area 2010']
        activity_df.loc[country_pathway_mask & (activity_df.loc[country_pathway_mask,'Total area 2010']==0),'Total area index']=0
        activity_df.loc[country_pathway_mask,'Total offset']=activity_df.loc[country_pathway_mask,'Spared Total area']*carbon_growth_rate[climatic_region[country]]
        activity_df.loc[country_pathway_mask,'Grassland offset']=activity_df.loc[country_pathway_mask,'Spared Grassland area']*carbon_growth_rate[climatic_region[country]]
        activity_df.loc[country_pathway_mask,'Feed offset']=activity_df.loc[country_pathway_mask,'Spared Feed area']*carbon_growth_rate[climatic_region[country]]
        activity_df.loc[country_pathway_mask,'Rice offset']=activity_df.loc[country_pathway_mask,'Spared Rice area']*carbon_growth_rate[climatic_region[country]]
        #country_pathway_mask=(activity_df['Country']==country) & (activity_df['Pathways']==pathway)
        # #Spared area
        # area_rice_ref=yield_rice_df.loc[(yield_rice_df['Area']==country) & (yield_rice_df['Element']=='Area harvested'),'Value'].values[0]
        # activity_df.loc[country_pathway_mask,'Spared area']=area_rice_ref-activity_df.loc[country_pathway_mask & (activity_df['Item']=='Rice, paddy'),'Rice area']
        # for item in ruminant_list:
        #     country_pathway_mask=(activity_df['Country']==country) & (activity_df['Pathways']==pathway) & (activity_df['Item']==item)
        #     activity_df.loc[country_pathway_mask,'Spared area']+=grassland_area_df.loc[item,country]-activity_df.loc[country_pathway_mask & (activity_df['Item']==item),'Grassland area']
        # for item in item_list:
        #     country_pathway_mask=(activity_df['Country']==country) & (activity_df['Pathways']==pathway) & (activity_df['Item']==item)
        #         country_pathway_item_feed_mask=(feed_per_head_df['Country']==pathway) & (feed_per_head_df['Item']==item) & (feed_per_head_df['Feed']==feed)
        #     area_ref=feed_per_head_df.loc[country_pathway_item_feed_mask,'Value'].values[0]*activity_ref_df[(activity_ref_df['Area']==country) & (activity_ref_df['Element']=='Stocks') & (activity_ref_df['Item']==item)]/yield_feed_df[country]
        #     activity_df.loc[country_pathway_mask,'Spared area']+=area_ref-activity_df.loc[country_pathway_mask,'Spared area']
activity_df.to_csv("output/impact_2050"+file_name_suffix+".csv")
