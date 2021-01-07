#! /bin/python

'''
Compute impacts of national methane quotas
on land-use change, production, CO2 and N2O emissions
'''

import pandas as pd
import numpy as np
from common_data import read_FAOSTAT_df
from copy import deepcopy
import argparse
import SI_pathways

parser = argparse.ArgumentParser('Compute impacts of different national level activity on production, areas, emissions...')
parser.add_argument('--sensitivity-analysis', help='Yields can be +50 or -50')
parser.add_argument('--print-table', action='store_true', help='Print tables used in the methane paper and ')
parser.add_argument('--mitigation',  help='Change mitigation option')
parser.add_argument('--carbon',  help='Change mitigation option')

args = parser.parse_args()

#Option for sensitivity analysis: change yield of +50% or -50%
if args.sensitivity_analysis is not None:
    yield_change=float(args.sensitivity_analysis)/100.
    file_name_suffix='_yield'+args.sensitivity_analysis
else:
    yield_change=0
    file_name_suffix=''

if args.carbon is not None:
    file_name_suffix+="_carbon"+args.carbon
    deforestation_df=pd.read_csv("output/deforestation_factor"+file_name_suffix+".csv")
    carbon_growth_rate={"Tropical":4.86*48./12.*(100+float(args.carbon))/100,"Temperate":2.8*48./12.*(100+float(args.carbon))/100}
else:
    #file_name_suffix+=""
    deforestation_df=pd.read_csv("output/deforestation_factor.csv")
    carbon_growth_rate={"Tropical":4.86*48./12.,"Temperate":2.8*48./12.}

if args.mitigation is not None:
    file_name_suffix='_mitigation'+args.mitigation

demand_dict={'Grass':['National Grass area'],'Grain':['Feed prodution','Cropland area (Feed)']}
#,'Rice, paddy':['prodution','area']
production_dict={'Cattle, dairy':['Milk, Total','Beef and Buffalo Meat'],'Cattle, non-dairy':['Beef and Buffalo Meat'],'Rice, paddy':['Rice, paddy'],'Swine':['Meat, pig'],'Poultry Birds':['Meat, Poultry'],'Chickens, layers':['Eggs Primary'],'Sheep and Goats':['Sheep and Goat Meat']}
item_list=['Cattle, dairy','Cattle, non-dairy','Swine','Poultry Birds','Chickens, layers','Sheep and Goats'] #'Rice, paddy'
# country_intensification_pd=pd.read_csv("output/model_country.csv",index_col=0)
# country_list=list(country_intensification_pd.columns)
country_list=["France","Ireland","Brazil","India"]
yield_dict={'Milk, Total':'Yield','Beef and Buffalo Meat':'Yield/Carcass Weight','Meat, pig':'Yield/Carcass Weight','Meat, Poultry':'Yield/Carcass Weight','Eggs Primary':'Yield','Sheep and Goat Meat':'Yield/Carcass Weight'}
animal_producing_dict={'Milk, Total':'Milk Animals','Beef and Buffalo Meat':'Producing Animals/Slaughtered','Meat, pig':'Producing Animals/Slaughtered','Meat, Poultry':'Producing Animals/Slaughtered','Eggs Primary':'Laying','Sheep and Goat Meat':'Producing Animals/Slaughtered'}
pathway_dict={"Ireland":["Ireland","Intensification"],#,"Intensification"
            "France":["France","Intensification"],#,"Intensification"
            "India":["India","Intensification"],#,"Intensification"
            "Brazil":["Brazil","Intensification"]}#,"Intensification"
ruminant_list=['Cattle, dairy','Cattle, non-dairy','Sheep and Goats']
production_aggregation_dict={'Milk':['Milk, Total'],'Ruminant Meat':['Beef and Buffalo Meat','Sheep and Goat Meat'],'Monogastric Meat':['Meat, pig','Meat, Poultry'],'Eggs':['Eggs Primary']}
activity_ref_df=read_FAOSTAT_df("data/FAOSTAT_manure_management.csv",delimiter="|")
yields_df=read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")
feed_per_head_df=read_FAOSTAT_df("data/GLEAM_feed.csv",index_col=0)
yield_feed_df=pd.read_csv("output/feed_yield_aggregate.csv")
yield_grass_df=pd.read_csv("output/grass_yield.csv")
density_df=pd.read_csv("output/density_livestock.csv",index_col=[0])
area_df=read_FAOSTAT_df("data/FAOSTAT_areas.csv",index_col=[0])
yield_rice_df=read_FAOSTAT_df("data/FAOSTAT_rice.csv",delimiter="|")
grassland_area_df=pd.read_csv('output/grassland_area.csv')
N_fertilizer_rate_df=read_FAOSTAT_df("output/N_fertilizer_rate.csv")
forest_area_df=read_FAOSTAT_df("data/FAOSTAT_forest_area.csv",delimiter="|")
kha_to_ha=1E3
climatic_region={"India":"Tropical","Brazil":"Tropical","Ireland":"Temperate","France":"Temperate"}
carbon_release_deforestation=deforestation_df.loc[0,"World"]
trade_feed_df=pd.read_csv("output/trade_aggregate_feed.csv",index_col=0)
yield_feed_international_df=pd.read_csv("output/feed_yield_global_aggregate.csv",index_col=0)
mitigation_list=["No mitigation","MACC"]

#Change yield depending on the sensitivty analysis
new_yield_feed_df=pd.DataFrame(columns=yield_feed_df.columns.values)
for country in country_list:
    new_yield_feed_df[country]=yield_feed_df[country]*(1.+yield_change)

output_df=pd.DataFrame([])
for country in country_list:
    for pathway in pathway_dict[country]:
        for mitigation in mitigation_list:
            #Option with or without mitigation aplied in 2050 for N2O and methane
            if mitigation=="MACC":
                if args.mitigation is not None:
                    emission_intensity_N2O_df=pd.read_csv("output/emission_intensity_N2O_mitigation"+args.mitigation+".csv")
                    activity_df=pd.read_csv("output/activity_2050_mitigation"+args.mitigation+".csv")
                else:
                    mitigation_name=mitigation.lower().replace(" ","_").replace("macc","")
                    emission_intensity_N2O_df=pd.read_csv("output/emission_intensity_N2O.csv")
                    activity_df=pd.read_csv("output/activity_2050.csv")
                    mitigation_potential_df=pd.read_csv("data/national_mitigation_mac.csv",dtype={"Mitigation potential":np.float64})
            else:
                mitigation_name=mitigation.lower().replace(" ","_").replace("MACC","")
                emission_intensity_N2O_df=pd.read_csv("output/emission_intensity_N2O_"+mitigation_name+".csv")
                activity_df=pd.read_csv("output/activity_2050.csv")
                mitigation_potential_df=pd.read_csv("data/"+mitigation_name+".csv",dtype={"Mitigation potential":np.float64})

            productivity_change_mac = {}
            production_change_mask = mitigation_potential_df["Production change"]!=0
            country_mask = mitigation_potential_df["Country"]==country
            for index in mitigation_potential_df.loc[production_change_mask & country_mask,:].index:
                animal=mitigation_potential_df.loc[index,"Item"]
                productivity_change_mac[animal]={}
                for production in production_dict[animal]:
                    productivity_change_mac[animal][production]=mitigation_potential_df.loc[index,"Production change"]

            if pathway == "Intensification":
                pathway_tmp=country
                pathway_name="Intensified"
                for item in item_list:
                    if item not in productivity_change_mac.keys():
                        if ("Cattle" in item) & ("Cattle" in productivity_change_mac.keys()):
                            productivity_change_mac[item]=productivity_change_mac["Cattle"]
                        else:
                            productivity_change_mac[item]={}
                    for production in production_dict[item]:
                        yield_change_tmp = SI_pathways.compute_yield_change(country,item,production,yields_df)
                        if production in productivity_change_mac[item].keys():
                            productivity_change_mac[item][production]=productivity_change_mac[item][production]*yield_change_tmp
                        else:
                            productivity_change_mac[item][production]=yield_change_tmp
            else:
                pathway_tmp=country
                pathway_name=country
            country_pathway_mitigation_mask=deepcopy((activity_df['Country']==country) & (activity_df['Pathways']==pathway_name) & (activity_df['Mitigation']==mitigation))
            activity_df.loc[country_pathway_mitigation_mask,'National Grass area']=0
            activity_df.loc[country_pathway_mitigation_mask,'National Grass area 2010']=0
            activity_df.loc[country_pathway_mitigation_mask,'N2O manure']=0
            activity_df.loc[country_pathway_mitigation_mask,'N2O manure 2010']=0
            for item in item_list:
                for production in production_dict[item]:
                    animal_number_ref=activity_ref_df.loc[(activity_ref_df['Area']==country) & (activity_ref_df['Element']=='Stocks') & (activity_ref_df['Item']==item),'Value'].values[0]
                    if "Cattle" in item:
                        cattle_all_number_ref=activity_ref_df.loc[(activity_ref_df['Area']==country) & (activity_ref_df['Element']=='Stocks') & (activity_ref_df['Item']=="Cattle"),'Value'].values[0]
                        slaugthered_animals=yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==animal_producing_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
                        slaugthered_animals_ref=yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==animal_producing_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
                        animal_producing=slaugthered_animals*animal_number_ref/cattle_all_number_ref
                        animal_producing_ref=slaugthered_animals_ref*animal_number_ref/cattle_all_number_ref
                    else:
                        animal_producing=yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==animal_producing_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
                        animal_producing_ref=yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==animal_producing_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
                    share_animal_producing=animal_producing/animal_number_ref
                    activity_df.loc[country_pathway_mitigation_mask,"Share Annimal producing 2010 "+production+" "+item]=share_animal_producing
                    activity_df.loc[country_pathway_mitigation_mask,"Activity 2010 "+item]=animal_number_ref
                    if item not in productivity_change_mac.keys():
                        productivity_change_mac[item]={}
                    if production not in productivity_change_mac[item].keys():
                        productivity_change_mac[item][production]=1
                    yields=yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==yield_dict[production]) & (yields_df['Item']==production),'Value'].values[0]*productivity_change_mac[item][production]
                    yields_ref=yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==yield_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
                    animal_number=activity_df.loc[country_pathway_mitigation_mask,'Activity '+item].values
                    if "Beef and Buffalo Meat"==production:
                        if production in activity_df.columns:
                            country_pathway_nan_mask=country_pathway_mitigation_mask & np.isnan(activity_df[production])
                            activity_df.loc[country_pathway_nan_mask,production]=0
                            country_pathway_nan_mask=country_pathway_mitigation_mask & np.isnan(activity_df[production+' 2010'])
                            activity_df.loc[country_pathway_nan_mask,production+' 2010']=0
                            activity_df.loc[country_pathway_mitigation_mask,production]+=yields*share_animal_producing*animal_number
                            activity_df.loc[country_pathway_mitigation_mask,production+' 2010']+=yields_ref*animal_producing_ref
                        else:
                            activity_df.loc[country_pathway_mitigation_mask,production]=yields*share_animal_producing*animal_number
                            activity_df.loc[country_pathway_mitigation_mask,production+' 2010']=yields_ref*animal_producing_ref
                    else:
                        activity_df.loc[country_pathway_mitigation_mask,production]=yields*share_animal_producing*animal_number
                        activity_df.loc[country_pathway_mitigation_mask,production+' 2010']=yields_ref*animal_producing_ref
                    activity_df.loc[country_pathway_mitigation_mask,production+' '+item+' yield 2010']=yields_ref
                    activity_df.loc[country_pathway_mitigation_mask,production+' '+item+' yield']=yields
                #Feed production
                feed='Grains'
                country_pathway_item_feed_mask=(feed_per_head_df['Country']==country) & (feed_per_head_df['Item']==item) & (feed_per_head_df['Feed']==feed)
                activity_df.loc[country_pathway_mitigation_mask,'National Feed production '+item]=feed_per_head_df.loc[country_pathway_item_feed_mask,'Value'].values[0]*animal_number*trade_feed_df.loc["Share feed demand domestically produced",country]*productivity_change_mac[item][production]
                animal_number_ref=activity_ref_df.loc[(activity_ref_df['Area']==country) & (activity_ref_df['Item']==item) & (activity_ref_df['Element']=='Stocks'),'Value'].values[0]
                activity_df.loc[country_pathway_mitigation_mask,'UP 2010 '+item]=animal_number_ref
                activity_df.loc[country_pathway_mitigation_mask,'UP '+item]=animal_number
                activity_df.loc[country_pathway_mitigation_mask,'National Feed production 2010 '+item]=feed_per_head_df.loc[(feed_per_head_df['Country']==country) & (feed_per_head_df['Item']==item) & (feed_per_head_df['Feed']==feed),'Value'].values[0]*animal_number_ref*trade_feed_df.loc["Share feed demand domestically produced",country]
                activity_df.loc[country_pathway_mitigation_mask,'International Feed production '+item]=feed_per_head_df.loc[country_pathway_item_feed_mask,'Value'].values[0]*animal_number*(1-trade_feed_df.loc["Share feed demand domestically produced",country])*productivity_change_mac[item][production]
                activity_df.loc[country_pathway_mitigation_mask,'International Feed production 2010 '+item]=feed_per_head_df.loc[(feed_per_head_df['Country']==country) & (feed_per_head_df['Item']==item) & (feed_per_head_df['Feed']==feed),'Value'].values[0]*animal_number_ref*(1-trade_feed_df.loc["Share feed demand domestically produced",country])
                activity_df.loc[country_pathway_mitigation_mask,'National crop production '+item]=activity_df.loc[country_pathway_mitigation_mask,'National Feed production 2010 '+item]+trade_feed_df.loc["Crop other",country]
                activity_df.loc[country_pathway_mitigation_mask,'National crop production 2010 '+item]=activity_df.loc[country_pathway_mitigation_mask,'National Feed production 2010 '+item]+trade_feed_df.loc["Crop other",country]
                #Feed yield
                activity_df.loc[country_pathway_mitigation_mask,'National Feed yield '+item]=new_yield_feed_df.loc[0,country]
                activity_df.loc[country_pathway_mitigation_mask,'National Feed yield 2010 '+item]=yield_feed_df.loc[0,country]
                activity_df.loc[country_pathway_mitigation_mask,'International Feed yield '+item]=yield_feed_international_df.loc[0,country]
                activity_df.loc[country_pathway_mitigation_mask,'International Feed yield 2010 '+item]=yield_feed_international_df.loc[0,country]
                #Grass area
                activity_df.loc[country_pathway_mitigation_mask,'National Grass area '+item]=animal_number*feed_per_head_df.loc[(feed_per_head_df['Country']==country) & (feed_per_head_df['Item']==item) & (feed_per_head_df['Feed']=='Grass'),'Value'].values[0]/(yield_grass_df.loc[0,country]*(1.+yield_change))
                activity_df.loc[country_pathway_mitigation_mask,'National Grass area 2010 '+item]=animal_number_ref*feed_per_head_df.loc[(feed_per_head_df['Country']==country) & (feed_per_head_df['Item']==item) & (feed_per_head_df['Feed']=='Grass'),'Value'].values[0]/yield_grass_df.loc[0,country]
                activity_df.loc[country_pathway_mitigation_mask,'National Grass area']+=activity_df.loc[country_pathway_mitigation_mask,'National Grass area '+item]
                activity_df.loc[country_pathway_mitigation_mask,'National Grass area 2010']+=activity_df.loc[country_pathway_mitigation_mask,'National Grass area 2010 '+item]
                #N2O emissions
                activity_df.loc[country_pathway_mitigation_mask,'N2O manure '+item]=animal_number*emission_intensity_N2O_df.loc[(emission_intensity_N2O_df['Country']==country) & (emission_intensity_N2O_df['Item']==item) & (emission_intensity_N2O_df['Emission']=='Manure total'),'Intensity'].values[0]
                activity_df.loc[country_pathway_mitigation_mask,'N2O manure 2010 '+item]=animal_number_ref*emission_intensity_N2O_df.loc[(emission_intensity_N2O_df['Country']==country) & (emission_intensity_N2O_df['Item']==item) & (emission_intensity_N2O_df['Emission']=='Manure total'),'Intensity'].values[0]
                activity_df.loc[country_pathway_mitigation_mask,'N2O manure']+=activity_df.loc[country_pathway_mitigation_mask,'N2O manure '+item]
                activity_df.loc[country_pathway_mitigation_mask,'N2O manure 2010']+=activity_df.loc[country_pathway_mitigation_mask,'N2O manure 2010 '+item]

            activity_df.loc[country_pathway_mitigation_mask,'National Grass area index']=activity_df.loc[country_pathway_mitigation_mask,'National Grass area']/activity_df.loc[country_pathway_mitigation_mask,'National Grass area 2010']
            activity_df.loc[country_pathway_mitigation_mask & (activity_df.loc[country_pathway_mitigation_mask,'National Grass area 2010']==0),'National Grass area index']=0
            activity_df.loc[country_pathway_mitigation_mask,'N2O manure index']=activity_df.loc[country_pathway_mitigation_mask,'N2O manure']/activity_df.loc[country_pathway_mitigation_mask,'N2O manure 2010']

            #Livestock area
            #activity_df.loc[country_pathway_mitigation_mask,'Livestock area']=activity_df.loc[country_pathway_mitigation_mask,'National Grass area']+activity_df.loc[country_pathway_mitigation_mask,'Feed area']
            for production_aggregate in production_aggregation_dict.keys():
                activity_df.loc[country_pathway_mitigation_mask,production_aggregate]=0
                activity_df.loc[country_pathway_mitigation_mask,production_aggregate+' 2010']=0
                for production_aggregated in production_aggregation_dict[production_aggregate]:
                    activity_df.loc[country_pathway_mitigation_mask,production_aggregate]+=activity_df.loc[country_pathway_mitigation_mask,production_aggregated].values
                    activity_df.loc[country_pathway_mitigation_mask,production_aggregate+' 2010']+=activity_df.loc[country_pathway_mitigation_mask,production_aggregated+' 2010'].values
                activity_df.loc[country_pathway_mitigation_mask,production_aggregate+' change']=activity_df.loc[country_pathway_mitigation_mask,production_aggregate]-activity_df.loc[country_pathway_mitigation_mask,production_aggregate+' 2010']
            item='Rice, paddy'
            #Rice area
            activity_df.loc[country_pathway_mitigation_mask,'National Rice area']=activity_df.loc[country_pathway_mitigation_mask,'Activity rice Rice, paddy']
            activity_df.loc[country_pathway_mitigation_mask,'National Rice area 2010']=yield_rice_df.loc[(yield_rice_df['Area']==country) & (yield_rice_df['Element']=='Area harvested'),'Value'].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'National Rice area change']=activity_df.loc[country_pathway_mitigation_mask,'National Rice area']-activity_df.loc[country_pathway_mitigation_mask,'National Rice area 2010']
            activity_df.loc[country_pathway_mitigation_mask & (activity_df['National Rice area change']>forest_area_df.loc[forest_area_df["Area"]==country,"Value"].values[0]),'National Rice area']=activity_df.loc[country_pathway_mitigation_mask & (activity_df['National Rice area change']>forest_area_df.loc[forest_area_df["Area"]==country,"Value"].values[0]),'National Rice area 2010']+forest_area_df.loc[forest_area_df["Area"]==country,"Value"].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'National Rice area index']=activity_df.loc[country_pathway_mitigation_mask,'National Rice area']/activity_df.loc[country_pathway_mitigation_mask,'National Rice area 2010']
            activity_df.loc[country_pathway_mitigation_mask & (activity_df.loc[country_pathway_mitigation_mask,'National Rice area 2010']==0),'National Rice area index']=0
            #Rice production
            activity_df.loc[country_pathway_mitigation_mask,'Production '+item]=activity_df.loc[country_pathway_mitigation_mask,'National Rice area']*yield_rice_df.loc[(yield_rice_df['Area']==country) & (yield_rice_df['Element']=='Yield'),'Value'].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'Production '+item+' 2010']=activity_df.loc[country_pathway_mitigation_mask,'National Rice area 2010']*yield_rice_df.loc[(yield_rice_df['Area']==country) & (yield_rice_df['Element']=='Yield'),'Value'].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'Production '+item+' change']=activity_df.loc[country_pathway_mitigation_mask,'Production '+item]-activity_df.loc[country_pathway_mitigation_mask,'Production '+item+' 2010']
            activity_df.loc[country_pathway_mitigation_mask,'Yield '+item]=yield_rice_df.loc[(yield_rice_df['Area']==country) & (yield_rice_df['Element']=='Yield'),'Value'].values[0]
            #Total production
            activity_df.loc[country_pathway_mitigation_mask,'Total production']=0
            activity_df.loc[country_pathway_mitigation_mask,'Total production 2010']=0
            for production in production_aggregation_dict.keys():
                activity_df.loc[country_pathway_mitigation_mask,'Total production']+=activity_df.loc[country_pathway_mitigation_mask,production].values
                activity_df.loc[country_pathway_mitigation_mask,'Total production 2010']+=activity_df.loc[country_pathway_mitigation_mask,production+' 2010'].values
            #Spared land
            activity_df.loc[country_pathway_mitigation_mask,'National Grass area change']=0
            activity_df.loc[country_pathway_mitigation_mask,'National Feed area change']=0
            activity_df.loc[country_pathway_mitigation_mask,'National Feed area']=0
            activity_df.loc[country_pathway_mitigation_mask,'National Feed area 2010']=0
            activity_df.loc[country_pathway_mitigation_mask,'International Feed area']=0
            activity_df.loc[country_pathway_mitigation_mask,'International Feed area 2010']=0
            for item in item_list:
                if item in ruminant_list:
                    activity_df.loc[country_pathway_mitigation_mask,'National Grass area change']+=activity_df.loc[country_pathway_mitigation_mask,'National Grass area '+item]-activity_df.loc[country_pathway_mitigation_mask,'National Grass area 2010 '+item]
                activity_df.loc[country_pathway_mitigation_mask,'National Feed area 2010']+=activity_df.loc[country_pathway_mitigation_mask,'National Feed production 2010 '+item]/yield_feed_df[country].values[0]
                activity_df.loc[country_pathway_mitigation_mask,'National Feed area']+=(activity_df.loc[country_pathway_mitigation_mask,'National Feed production '+item])/activity_df.loc[country_pathway_mitigation_mask,'National Feed yield '+item].values[0]
                activity_df.loc[country_pathway_mitigation_mask,'International Feed area 2010']+=activity_df.loc[country_pathway_mitigation_mask,'International Feed production 2010 '+item]/yield_feed_international_df[country].values[0]
                activity_df.loc[country_pathway_mitigation_mask,'International Feed area']+=(activity_df.loc[country_pathway_mitigation_mask,'International Feed production '+item])/activity_df.loc[country_pathway_mitigation_mask,'International Feed yield '+item].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'National Feed area change']=activity_df.loc[country_pathway_mitigation_mask,'National Feed area']-activity_df.loc[country_pathway_mitigation_mask,'National Feed area 2010']
            activity_df.loc[country_pathway_mitigation_mask,'National Feed area index']=activity_df.loc[country_pathway_mitigation_mask,'National Feed area']/activity_df.loc[country_pathway_mitigation_mask,'National Feed area 2010']
            activity_df.loc[country_pathway_mitigation_mask,'International Feed area change']=activity_df.loc[country_pathway_mitigation_mask,'International Feed area']-activity_df.loc[country_pathway_mitigation_mask,'International Feed area 2010']
            activity_df.loc[country_pathway_mitigation_mask,'International Feed area index']=activity_df.loc[country_pathway_mitigation_mask,'International Feed area']/activity_df.loc[country_pathway_mitigation_mask,'International Feed area 2010']
            activity_df.loc[country_pathway_mitigation_mask,'National cropland area']=area_df.loc[(area_df["Area"]==country) & (area_df["Item"]=="Cropland"),"Value"].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'National other cropland area 2010']=activity_df.loc[country_pathway_mitigation_mask,'National cropland area']-activity_df.loc[country_pathway_mitigation_mask,'National Feed area 2010']-activity_df.loc[country_pathway_mitigation_mask,'National Rice area 2010']
            activity_df.loc[country_pathway_mitigation_mask,'National other cropland area']=activity_df.loc[country_pathway_mitigation_mask,'National other cropland area 2010']
            #N2O emissions from fertilization of feed
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert feed']=activity_df.loc[country_pathway_mitigation_mask,'National Feed area']*N_fertilizer_rate_df.loc[(N_fertilizer_rate_df['Area']==country) & (N_fertilizer_rate_df['Item']=="Cropland"),'Value'].values[0]*(1.+yield_change)*emission_intensity_N2O_df.loc[(emission_intensity_N2O_df['Country']==country) & (emission_intensity_N2O_df['Emission']=='fertilizer'),'Intensity'].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert rice']=activity_df.loc[country_pathway_mitigation_mask,'National Rice area']*N_fertilizer_rate_df.loc[(N_fertilizer_rate_df['Area']==country) & (N_fertilizer_rate_df['Item']=="Cropland"),'Value'].values[0]*emission_intensity_N2O_df.loc[(emission_intensity_N2O_df['Country']==country) & (emission_intensity_N2O_df['Emission']=='fertilizer'),'Intensity'].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert other']=activity_df.loc[country_pathway_mitigation_mask,'National other cropland area']*N_fertilizer_rate_df.loc[(N_fertilizer_rate_df['Area']==country) & (N_fertilizer_rate_df['Item']=="Cropland"),'Value'].values[0]*(1.+yield_change)*emission_intensity_N2O_df.loc[(emission_intensity_N2O_df['Country']==country) & (emission_intensity_N2O_df['Emission']=='fertilizer'),'Intensity'].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert grass']=activity_df.loc[country_pathway_mitigation_mask,'National Grass area']*N_fertilizer_rate_df.loc[(N_fertilizer_rate_df['Area']==country) & (N_fertilizer_rate_df['Item']=="Grassland"),'Value'].values[0]*(1.+yield_change)*emission_intensity_N2O_df.loc[(emission_intensity_N2O_df['Country']==country) & (emission_intensity_N2O_df['Emission']=='fertilizer'),'Intensity'].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert']=activity_df.loc[country_pathway_mitigation_mask,'N2O fert grass']+activity_df.loc[country_pathway_mitigation_mask,'N2O fert feed']+activity_df.loc[country_pathway_mitigation_mask,'N2O fert other']+activity_df.loc[country_pathway_mitigation_mask,'N2O fert rice']
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert feed 2010']=activity_df.loc[country_pathway_mitigation_mask,'National Feed area 2010']*N_fertilizer_rate_df.loc[(N_fertilizer_rate_df['Area']==country),'Value'].values[0]*emission_intensity_N2O_df.loc[(emission_intensity_N2O_df['Country']==country) & (emission_intensity_N2O_df['Emission']=='fertilizer'),'Intensity'].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert rice 2010']=activity_df.loc[country_pathway_mitigation_mask,'National Rice area 2010']*N_fertilizer_rate_df.loc[(N_fertilizer_rate_df['Area']==country) & (N_fertilizer_rate_df['Item']=="Cropland"),'Value'].values[0]*emission_intensity_N2O_df.loc[(emission_intensity_N2O_df['Country']==country) & (emission_intensity_N2O_df['Emission']=='fertilizer'),'Intensity'].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert other 2010']=activity_df.loc[country_pathway_mitigation_mask,'National other cropland area']*N_fertilizer_rate_df.loc[(N_fertilizer_rate_df['Area']==country) & (N_fertilizer_rate_df['Item']=="Cropland"),'Value'].values[0]*emission_intensity_N2O_df.loc[(emission_intensity_N2O_df['Country']==country) & (emission_intensity_N2O_df['Emission']=='fertilizer'),'Intensity'].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert grass 2010']=activity_df.loc[country_pathway_mitigation_mask,'National Grass area 2010']*N_fertilizer_rate_df.loc[(N_fertilizer_rate_df['Area']==country) & (N_fertilizer_rate_df['Item']=="Grassland"),'Value'].values[0]*emission_intensity_N2O_df.loc[(emission_intensity_N2O_df['Country']==country) & (emission_intensity_N2O_df['Emission']=='fertilizer'),'Intensity'].values[0]
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert 2010']=activity_df.loc[country_pathway_mitigation_mask,'N2O fert feed 2010']+activity_df.loc[country_pathway_mitigation_mask,'N2O fert other 2010']+activity_df.loc[country_pathway_mitigation_mask,'N2O fert grass 2010']+activity_df.loc[country_pathway_mitigation_mask,'N2O fert rice 2010']
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert index']=activity_df.loc[country_pathway_mitigation_mask,'N2O fert']/activity_df.loc[country_pathway_mitigation_mask,'N2O fert 2010']
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert feed change']=activity_df.loc[country_pathway_mitigation_mask,'N2O fert feed']-activity_df.loc[country_pathway_mitigation_mask,'N2O fert feed 2010']
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert rice change']=activity_df.loc[country_pathway_mitigation_mask,'N2O fert rice']-activity_df.loc[country_pathway_mitigation_mask,'N2O fert rice 2010']
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert other change']=activity_df.loc[country_pathway_mitigation_mask,'N2O fert other']-activity_df.loc[country_pathway_mitigation_mask,'N2O fert other 2010']
            activity_df.loc[country_pathway_mitigation_mask,'N2O fert grass change']=activity_df.loc[country_pathway_mitigation_mask,'N2O fert grass']-activity_df.loc[country_pathway_mitigation_mask,'N2O fert grass 2010']
            activity_df.loc[country_pathway_mitigation_mask,'N2O']=activity_df.loc[country_pathway_mitigation_mask,'N2O fert']+activity_df.loc[country_pathway_mitigation_mask,'N2O manure']
            activity_df.loc[country_pathway_mitigation_mask & (activity_df.loc[country_pathway_mitigation_mask,'National Feed area 2010']==0),'National Feed area index']=0
            activity_df.loc[country_pathway_mitigation_mask,'National Total area change']=activity_df.loc[country_pathway_mitigation_mask,'National Grass area change']+activity_df.loc[country_pathway_mitigation_mask,'National Feed area change']+activity_df.loc[country_pathway_mitigation_mask,'National Rice area change']
            activity_df.loc[country_pathway_mitigation_mask,'National Total area']=activity_df.loc[country_pathway_mitigation_mask,'National Grass area']+activity_df.loc[country_pathway_mitigation_mask,'National Feed area']+activity_df.loc[country_pathway_mitigation_mask,'National Rice area']+activity_df.loc[country_pathway_mitigation_mask,'National other cropland area']
            activity_df.loc[country_pathway_mitigation_mask,'National Total area 2010']=activity_df.loc[country_pathway_mitigation_mask,'National Grass area 2010']+activity_df.loc[country_pathway_mitigation_mask,'National Feed area 2010']+activity_df.loc[country_pathway_mitigation_mask,'National Rice area 2010']+activity_df.loc[country_pathway_mitigation_mask,'National other cropland area 2010']
            activity_df.loc[country_pathway_mitigation_mask,'National Total area index']=activity_df.loc[country_pathway_mitigation_mask,'National Total area']/activity_df.loc[country_pathway_mitigation_mask,'National Total area 2010']
            activity_df.loc[country_pathway_mitigation_mask & (activity_df.loc[country_pathway_mitigation_mask,'National Total area 2010']==0),'National Total area index']=0
            country_pathway_reforestation_mask=country_pathway_mitigation_mask & (activity_df['National Grass area change']<0)
            country_pathway_deforestation_mask=country_pathway_mitigation_mask & (activity_df['National Grass area change']>0)
            country_pathway_no_change_mask=country_pathway_mitigation_mask & (activity_df['National Grass area change']==0)
            activity_df.loc[country_pathway_reforestation_mask,'Grass offset']=-activity_df.loc[country_pathway_reforestation_mask,'National Grass area change']*carbon_growth_rate[climatic_region[country]]
            activity_df.loc[country_pathway_deforestation_mask,'Grass offset']=-activity_df.loc[country_pathway_deforestation_mask,'National Grass area change']*deforestation_df.loc[0,country]
            activity_df.loc[country_pathway_no_change_mask,'Grass offset']=0
            country_pathway_reforestation_mask=country_pathway_mitigation_mask & (activity_df['National Feed area change']<0)
            country_pathway_deforestation_mask=country_pathway_mitigation_mask & (activity_df['National Feed area change']>0)
            country_pathway_no_change_mask=country_pathway_mitigation_mask & (activity_df['National Feed area change']==0)
            activity_df.loc[country_pathway_reforestation_mask,'Feed offset']=-activity_df.loc[country_pathway_reforestation_mask,'National Feed area change']*carbon_growth_rate[climatic_region[country]]
            activity_df.loc[country_pathway_deforestation_mask,'Feed offset']=-activity_df.loc[country_pathway_deforestation_mask,'National Feed area change']*deforestation_df.loc[0,country]
            activity_df.loc[country_pathway_no_change_mask,'Feed offset']=0
            international_pathway_reforestation_mask=country_pathway_mitigation_mask & (activity_df['International Feed area change']<0)
            international_pathway_deforestation_mask=country_pathway_mitigation_mask & (activity_df['International Feed area change']>0)
            international_pathway_no_change_mask=country_pathway_mitigation_mask & (activity_df['International Feed area change']==0)
            activity_df.loc[international_pathway_reforestation_mask,'International Feed offset']=-activity_df.loc[international_pathway_reforestation_mask,'International Feed area change']*carbon_growth_rate[climatic_region[country]]
            activity_df.loc[international_pathway_deforestation_mask,'International Feed offset']=-activity_df.loc[international_pathway_deforestation_mask,'International Feed area change']*deforestation_df.loc[0,"World"]
            activity_df.loc[international_pathway_no_change_mask,'International Feed offset']=0
            country_pathway_reforestation_mask=country_pathway_mitigation_mask & (activity_df['National Rice area change']<0)
            country_pathway_deforestation_mask=country_pathway_mitigation_mask & (activity_df['National Rice area change']>0)
            country_pathway_no_change_mask=country_pathway_mitigation_mask & (activity_df['National Rice area change']==0)
            activity_df.loc[country_pathway_reforestation_mask,'Rice offset']=-activity_df.loc[country_pathway_reforestation_mask,'National Rice area change']*carbon_growth_rate[climatic_region[country]]
            activity_df.loc[country_pathway_deforestation_mask,'Rice offset']=-activity_df.loc[country_pathway_deforestation_mask,'National Rice area change']*carbon_release_deforestation
            activity_df.loc[country_pathway_no_change_mask,'Rice offset']=0
            output_df=pd.concat([output_df,activity_df.loc[country_pathway_mitigation_mask,:]])
#Total offset
output_df.loc[:,'Total offset']=output_df.loc[:,'Rice offset']+output_df.loc[:,'Feed offset']+output_df.loc[:,'Grass offset']
#country_pathway_mitigation_mask=(activity_df['Country']==country) & (activity_df['Pathways']==pathway)
# #Spared area
# area_rice_ref=yield_rice_df.loc[(yield_rice_df['Area']==country) & (yield_rice_df['Element']=='Area harvested'),'Value'].values[0]
# activity_df.loc[country_pathway_mitigation_mask,'Spared area']=area_rice_ref-activity_df.loc[country_pathway_mitigation_mask & (activity_df['Item']=='Rice, paddy'),'National Rice area']
# for item in ruminant_list:
#     country_pathway_mitigation_mask=(activity_df['Country']==country) & (activity_df['Pathways']==pathway) & (activity_df['Item']==item)
#     activity_df.loc[country_pathway_mitigation_mask,'Spared area']+=grassland_area_df.loc[item,country]-activity_df.loc[country_pathway_mitigation_mask & (activity_df['Item']==item),'Grass area']
# for item in item_list:
#     country_pathway_mitigation_mask=(activity_df['Country']==country) & (activity_df['Pathways']==pathway) & (activity_df['Item']==item)
#         country_pathway_item_feed_mask=(feed_per_head_df['Country']==pathway) & (feed_per_head_df['Item']==item) & (feed_per_head_df['Feed']==feed)
#     area_ref=feed_per_head_df.loc[country_pathway_item_feed_mask,'Value'].values[0]*activity_ref_df[(activity_ref_df['Area']==country) & (activity_ref_df['Element']=='Stocks') & (activity_ref_df['Item']==item)]/yield_feed_df[country]
#     activity_df.loc[country_pathway_mitigation_mask,'Spared area']+=area_ref-activity_df.loc[country_pathway_mitigation_mask,'Spared area']
output_df.to_csv("output/impact_2050"+file_name_suffix+".csv")

if args.print_table:
    column_name_to_variable_name_dict={"Methane quota":{'All':['National quota'],
                                                        'Milk':['Quota enteric Cattle, dairy','Quota manure Cattle, dairy'],
                                                        'Ruminant Meat':['Quota enteric Cattle, non-dairy','Quota manure Cattle, non-dairy','Quota enteric Sheep and Goats','Quota manure Sheep and Goats'],
                                                        'Monogastric Meat':['Quota manure Poultry Birds','Quota manure Swine'],
                                                        'Eggs':['Quota manure Chickens, layers'],
                                                        'Rice':['Quota rice Rice, paddy']},
                                        "Production":{'Milk':['Milk, Total'],
                                                      'Ruminant Meat':['Beef and Buffalo Meat','Sheep and Goat Meat'],
                                                      'Monogastric Meat':['Meat, pig','Meat, Poultry'],
                                                      'Eggs':['Eggs Primary'],
                                                      'Rice':['Production Rice, paddy']},
                                        "Area":{'Grassland':['National Grass area'],
                                                'Cropland for feed':['National Feed area'],
                                                'Cropland for other':['National other cropland area'],
                                                'Net imports of feed area':['International Feed area']},
                                        "CO2 offset":{'Grassland':["Grass offset"],
                                                      'Cropland for feed':["Feed offset"],
                                                      'Cropland for other':["Rice offset"],
                                                      'Net imports':["International Feed offset"]},
                                        "N2O emissions":{'Grassland':["N2O fert grass"],
                                                      'Cropland for feed':["N2O fert feed"],
                                                      'Cropland for other than feed':["N2O fert other"]}
                                        }
    from common_methane import print_table_results
    print_table_df=print_table_results(output_df,country_list,column_name_to_variable_name_dict)
    print_table_df.to_csv("output/paper_table1"+file_name_suffix+".csv",sep=";",encoding="utf-8",decimal =",",float_format='%.3f')
