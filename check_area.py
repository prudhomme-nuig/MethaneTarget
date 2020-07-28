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

parser = argparse.ArgumentParser('Compute impacts of different national level activity on production, areas, emissions...')
parser.add_argument('--sensitivity-analysis', help='Yields can be +50 or -50')
parser.add_argument('--no-mitigation', action='store_true', help='No mitigation option')
parser.add_argument('--print-table', action='store_true', help='Print tables used in the methane paper and ')
parser.add_argument('--mitigation',  help='Change mitigation option')
parser.add_argument('--carbon',  help='Change mitigation option')

args = parser.parse_args()

#Option for sensitivity analysis: change yield of +50% or -50%
if args.sensitivity_analysis is not None:
    file_name_suffix='_yield'+args.sensitivity_analysis
else:
    file_name_suffix=''

#Option with or without mitigation aplied in 2050 for N2O and methane
if args.no_mitigation:
    activity_df=pd.read_csv("output/activity_2050_no_mitigation.csv")
    methane_intensity_df=pd.read_csv("output/emission_intensity_2050_no_mitigation.csv")
    file_name_suffix+='_no_mitigation'
else:
    activity_df=pd.read_csv("output/activity_2050.csv")
    methane_intensity_df=pd.read_csv("output/emission_intensity_2050.csv")
    file_name_suffix+=''

if args.mitigation is not None:
    activity_df=pd.read_csv("output/activity_2050_mitigation"+args.mitigation+".csv")
    methane_intensity_df=pd.read_csv("output/emission_intensity_2050_mitigation"+args.mitigation+".csv")
    file_name_suffix+="_mitigation"+args.mitigation

if args.carbon is not None:
    file_name_suffix+="_carbon"+args.carbon
    deforestation_df=pd.read_csv("output/deforestation_factor"+file_name_suffix+".csv")
else:
    file_name_suffix+=""
    deforestation_df=pd.read_csv("output/deforestation_factor.csv")

forest_area_df=read_FAOSTAT_df("data/FAOSTAT_forest_area.csv",delimiter="|")
activity_df=pd.read_csv("output/impact_2050"+file_name_suffix+".csv")
country_list=["France","Ireland","Brazil","India"]
production_aggregation_dict={'Milk':['Milk, Total'],'Ruminant Meat':['Beef and Buffalo Meat','Sheep and Goat Meat'],'Monogastric Meat':['Meat, pig','Meat, Poultry'],'Eggs':['Eggs Primary']}
carbon_growth_rate={"Tropical":4.86*48./12.,"Temperate":2.8*48./12.}
climatic_region={"India":"Tropical","Brazil":"Tropical","Ireland":"Temperate","France":"Temperate"}
carbon_release_deforestation=deforestation_df.loc[0,"World"]
production_item_dict={"Rice":["Rice, paddy"],
                      "Feed":['Milk','Ruminant Meat','Monogastric Meat','Eggs']}

activity_df["Highest area change"]=activity_df[["National Grass area change","National Rice area change"]].idxmax(axis=1)
activity_df["National quota used and unused"]=deepcopy(activity_df["National quota"])
for country in country_list:
    country_forest_area=forest_area_df.loc[forest_area_df["Area"]==country,"Value"].values[0]
    country_mask=deepcopy((activity_df['Country']==country))
    country_forest_area_mask=(activity_df['National Total area change']>country_forest_area) & (activity_df['Country']==country)
    if len(country_forest_area_mask[country_forest_area_mask])>2:
        print(country)
        #area_change_column_name=activity_df.loc[country_forest_area_mask,"Highest area change"].values[0]
        area_reduction=deepcopy(activity_df.loc[country_forest_area_mask,"National Total area change"]-country_forest_area)
        area_reduction_rate=deepcopy((country_forest_area)/(activity_df.loc[country_forest_area_mask,"National Total area change"]))
        activity_df.loc[country_forest_area_mask,"National Total area change"]=activity_df.loc[country_forest_area_mask,"National Total area change"]-area_reduction
        for item in ["Rice","Feed","Grass"]:
            for column_name in ["National "+item+" area",'Production '+item,'N2O fert '+item.lower()]:
                if ("Production" in  column_name):
                    if (item=="Grass"):
                        continue
                    else:
                        for production in production_item_dict[item]:
                            if "Rice" in production:
                                column_name='Production '+production
                            else:
                                column_name=production
                            activity_df.loc[country_forest_area_mask,column_name]=activity_df.loc[country_forest_area_mask,column_name+" 2010"]+activity_df.loc[country_forest_area_mask,column_name+" change"]*area_reduction_rate
                else:
                    activity_df.loc[country_forest_area_mask,column_name]=activity_df.loc[country_forest_area_mask,column_name+" 2010"]+activity_df.loc[country_forest_area_mask,column_name+" change"]*area_reduction_rate
            activity_df.loc[country_forest_area_mask,'National '+item+' area index']=activity_df.loc[country_forest_area_mask,'National '+item+' area']/activity_df.loc[country_forest_area_mask,'National '+item+' area 2010']
            activity_df.loc[country_forest_area_mask,'National '+item+' area change']=activity_df.loc[country_forest_area_mask,'National '+item+' area']-activity_df.loc[country_forest_area_mask,'National '+item+' area 2010']
            country_pathway_reforestation_mask=country_forest_area_mask & (activity_df['National '+item+' area change']<0)
            country_pathway_deforestation_mask=country_forest_area_mask & (activity_df['National '+item+' area change']>0)
            country_pathway_no_change_mask=country_forest_area_mask & (activity_df['National '+item+' area change']==0)
            activity_df.loc[country_pathway_reforestation_mask,item+' offset']=-activity_df.loc[country_pathway_reforestation_mask,'National '+item+' area change']*carbon_growth_rate[climatic_region[country]]
            activity_df.loc[country_pathway_deforestation_mask,item+' offset']=-activity_df.loc[country_pathway_deforestation_mask,'National '+item+' area change']*carbon_release_deforestation
            activity_df.loc[country_pathway_no_change_mask,item+' offset']=0
        activity_df.loc[country_forest_area_mask,'National Total area change']=activity_df.loc[country_forest_area_mask,'National Grass area change']+activity_df.loc[country_forest_area_mask,'National Feed area change']+activity_df.loc[country_forest_area_mask,'National Rice area change']
        activity_df.loc[country_forest_area_mask,'National Total area']=activity_df.loc[country_forest_area_mask,'National Grass area']+activity_df.loc[country_forest_area_mask,'National Feed area']+activity_df.loc[country_forest_area_mask,'National Rice area']+activity_df.loc[country_forest_area_mask,'National other cropland area']
        activity_df.loc[country_forest_area_mask,'National Total area index']=activity_df.loc[country_forest_area_mask,'National Total area']/activity_df.loc[country_forest_area_mask,'National Total area 2010']
        activity_df.loc[country_forest_area_mask,'N2O fert']=activity_df.loc[country_forest_area_mask,'N2O fert grass']+activity_df.loc[country_forest_area_mask,'N2O fert feed']+activity_df.loc[country_forest_area_mask,'N2O fert other']+activity_df.loc[country_forest_area_mask,'N2O fert rice']
        activity_df.loc[country_forest_area_mask,'N2O fert index']=activity_df.loc[country_forest_area_mask,'N2O fert']/activity_df.loc[country_forest_area_mask,'N2O fert 2010']
        activity_df.loc[country_forest_area_mask,'N2O']=activity_df.loc[country_forest_area_mask,'N2O fert']+activity_df.loc[country_forest_area_mask,'N2O manure']
        activity_df.loc[country_forest_area_mask,"National quota unused"]=activity_df.loc[country_forest_area_mask,"National quota used and unused"]-activity_df.loc[country_forest_area_mask,"National quota"]
        activity_df.loc[country_forest_area_mask,"National quota"]=activity_df.loc[country_forest_area_mask,"National 2010"]-(activity_df.loc[country_forest_area_mask,"National 2010"]-activity_df.loc[country_forest_area_mask,"National quota unused"])*area_reduction_rate
        for production in production_aggregation_dict.keys():
            activity_df.loc[country_forest_area_mask,'Total production']+=activity_df.loc[country_forest_area_mask,production].values
            activity_df.loc[country_forest_area_mask,'Total production 2010']+=activity_df.loc[country_forest_area_mask,production+' 2010'].values
        activity_df.loc[country_forest_area_mask,'Total offset']=activity_df.loc[country_forest_area_mask,'Rice offset']+activity_df.loc[country_forest_area_mask,'Feed offset']+activity_df.loc[country_forest_area_mask,'Grass offset']

activity_df.to_csv("output/impact_2050"+file_name_suffix+".csv")

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
    print_table_df=print_table_results(activity_df,country_list,column_name_to_variable_name_dict)
    print_table_df.to_csv("output/paper_table1"+file_name_suffix+".csv",sep=";",encoding="utf-8",decimal =",",float_format='%.3f')
