#! /bin/python

'''
Compute methane intensity per unit of production in 2050 for each intensification pathway, with and without mitigation
'''

import pandas as pd
import numpy as np
from common_data import read_FAOSTAT_df
import argparse

parser = argparse.ArgumentParser('Compute methane intensity per unit of production in 2050 for each intensification pathway')
parser.add_argument('--no-mitigation', action='store_true', help='No mitigation option')

args = parser.parse_args()

country_list=["France","Ireland","Brazil","India"]
country_intensification_pd=pd.read_csv("output/model_country.csv",index_col=0)
country_list.extend(list(np.unique(country_intensification_pd.values)))

animal_list=["Cattle, non-dairy","Cattle, dairy","Chickens, layers","Poultry Birds","Sheep and Goats","Swine"]
GWP100_CH4=34
GWP100_N2O=298

#Mitigation potential and cost
# fom national MAC curves
if args.no_mitigation:
    mitigation_potential_df=pd.read_csv("data/no_mitigation.csv",dtype={"Mitigation potential":np.float64})
    output_file_name='output/emission_intensity_2050_no_mitigation.csv'
else:
    mitigation_potential_df=pd.read_csv("data/national_mitigation_mac.csv",dtype={"Mitigation potential":np.float64})
    output_file_name='output/emission_intensity_2050.csv'

#Option with or without mitigation aplied in 2050 for N2O and methane
if args.no_mitigation:
    mitigation_potential_df=pd.read_csv("data/no_mitigation.csv",dtype={"Mitigation potential":np.float64})
    output_file_name='output/emission_intensity_2050_no_mitigation.csv'
else:
    mitigation_potential_df=pd.read_csv("data/national_mitigation_mac.csv",dtype={"Mitigation potential":np.float64})
    output_file_name='output/emission_intensity_2050.csv'

#Read methane emissions in 2010 from FAOSTAT
methane_df=read_FAOSTAT_df("data/FAOSTAT_methane.csv",delimiter=",")
methane_Ent_Ferm_df=read_FAOSTAT_df("data/FAOSTAT_enteric_fermentation.csv",delimiter="|")
methane_Ent_Ferm_df.name="enteric"
methane_Man_df=read_FAOSTAT_df("data/FAOSTAT_manure_management.csv",delimiter="|")
methane_Man_df.name="manure"
methane_rice_df=read_FAOSTAT_df("data/FAOSTAT_rice.csv",delimiter="|")
methane_rice_df.name="rice"
item_of_df={methane_rice_df.name:["Rice, paddy"],
            methane_Man_df.name:animal_list,
            methane_Ent_Ferm_df.name:["Cattle, non-dairy","Cattle, dairy","Sheep and Goats"]}

nutrious_Man_df=pd.DataFrame(columns=["Country","Item","Value"])
index=0
for country in country_list:
    for item in animal_list:
        nutrious_Man_df.loc[index,:]=[country,item,0]
        for manure in ['management','application','left']:
            man_df=read_FAOSTAT_df("data/FAOSTAT_N2O_manure_"+manure+".csv",delimiter="|")
            if any ((man_df['Area']==country) & (man_df['Item']==item)):
                nutrious_Man_df.loc[index,'Value']+=man_df.loc[(man_df['Area']==country) & (["Emissions (N2O)" in list_element for list_element in man_df["Element"]]) & (man_df['Item']==item),'Value'].values[0]
        index+=1

index=0
share_methane_df=pd.DataFrame(columns=["Country","Item","Value"])
for country in country_list:
    for item in animal_list:
        share_methane_df.loc[index,:]=[country,item,0]
        share_methane_df.loc[index,'Value']=methane_Man_df.loc[(methane_Man_df['Area']==country) & (methane_Man_df['Element']=='Emissions (CH4) (Manure management)') & (methane_Man_df['Item']==item),'Value'].values[0]*GWP100_CH4/(methane_Man_df.loc[(methane_Man_df['Area']==country) & (methane_Man_df['Element']=='Emissions (CH4) (Manure management)') & (methane_Man_df['Item']==item),'Value'].values[0]*GWP100_CH4+nutrious_Man_df.loc[(nutrious_Man_df['Country']==country) & (nutrious_Man_df['Item']==item),'Value'].values[0]*GWP100_N2O)
        index+=1
#item_to_product_dict={'Cattle':['Milk, Total','Beef and Buffalo Meat'],'Swine':['Meat, pig'],'Chickens':['Meat, Poultry','Eggs Primary'],'Poultry Birds':['Meat, Poultry'],'Sheep and Goats':['Sheep and Goat Meat']}

def compute_emission_intensity(mitigation_potential_df,df,country,item,share_methane_df=share_methane_df):
    mitigation_df=mitigation_potential_df.loc[mitigation_potential_df["Emission"]==df.name,:]
    if item =='Rice, paddy':
        item_name='Rice'
    else:
        item_name=item
    for index in mitigation_df.index:
        if ((mitigation_df.loc[index,"gaz"]=='CH4') | (mitigation_df.loc[index,"gaz"]=='both')) & (mitigation_df.loc[index,"Item"] in item_name):
            if mitigation_df.loc[index,"gaz"]=='both':
                gaz_share=share_methane_df.loc[(share_methane_df['Country']==country) & (share_methane_df['Item']==item),'Value'].values[0]/GWP100_CH4
            elif mitigation_df.loc[index,"gaz"]=='CH4':
                gaz_share=1
            else:
                gaz_share=0
            if (mitigation_df.loc[index,"Item"]=="Cattle"):
                share_item=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010)  & (df["Element"]=="Stocks"),"Value"].values[0]/df.loc[(df["Item"]=="Cattle") & (df["Area"]==country) & (df["Year"]==2010) & (df["Element"]=="Stocks"),"Value"].values[0]
            else:
                share_item=1
            if mitigation_df.loc[index,"Indicator"]=="share":
                emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor" in list_element for list_element in df["Element"]]),"Value"].values[0]*(1-mitigation_df.loc[index,"Mitigation potential"])
            elif mitigation_df.loc[index,"Indicator"]=="mitigation":
                emission_total=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Emissions (CH4)" in list_element for list_element in df["Element"]]),"Value"].values[0]-(mitigation_df.loc[index,"Mitigation potential"]*gaz_share*share_item)
                emission_intensity=emission_total/df.loc[(df["Area"]==country) & (df["Year"]==2010) & (df["Item"]==item) & (df["Element"]=="Stocks"),"Value"].values[0]
            elif mitigation_df.loc[index,"Indicator"]=="mitigation per ha":
                emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor" in list_element for list_element in df["Element"]]),"Value"].values[0]-(mitigation_df.loc[index,"Mitigation potential"]*gaz_share)
            elif mitigation_df.loc[index,"Indicator"]=="mitigation per head":
                emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor" in list_element for list_element in df["Element"]]),"Value"].values[0]-(mitigation_df.loc[index,"Mitigation potential"]*gaz_share)
        else:
            emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor" in list_element for list_element in df["Element"]]),"Value"].values[0]
    return emission_intensity

def compute_activity(mitigation_potential_df,df,country,item):
    for index in mitigation_potential_df.index:
        if item=="Rice, paddy":
            activity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (df["Element"]=="Area harvested"),"Value"].values[0]
        else:
            activity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (df["Element"]=="Stocks"),"Value"].values[0]
    return activity

for df in [methane_Ent_Ferm_df,methane_Man_df]:
    index=len(df["Area"])
    for country in country_list:
        for item in item_of_df[df.name]:
            value=df.loc[(df["Area"]==country) & (df["Item"]==item) & (["Emissions (CH4)" in list_element for list_element in df["Element"]]),"Value"].values[0]/df.loc[(df["Area"]==country) & (df["Item"]==item) & (["Stock" in list_element for list_element in df["Element"]]),"Value"].values[0]
            df.loc[index,:]=[df.name,country,"Implied emission factor",item,2010,"tCH4/head",value]
            index+=1

output_df=pd.DataFrame(columns=["Country","Emission","Item","Intensity"])
output_activity_df=pd.DataFrame(columns=["Country","Emission","Item","Activity"])
index=0
for emission_df in [methane_Ent_Ferm_df,methane_rice_df,methane_Man_df]:
    for country in country_list:
        for item in item_of_df[emission_df.name]:
            if emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]==0:
                output_df.loc[index,:]=[country,emission_df.name,item,0]
            else:
                if emission_df.name in mitigation_potential_df.loc[mitigation_potential_df["Country"]==country,"Emission"].values:
                    emission_intensity=compute_emission_intensity(mitigation_potential_df,emission_df,country,item,share_methane_df=share_methane_df)
                    output_df.loc[index,:]=[country,emission_df.name,item,emission_intensity]
                else:
                    if emission_df.name in ['manure','enteric']:
                        intensity=emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]/emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Stocks" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                    else:
                        intensity=emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]/emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Area harvested" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                    output_df.loc[index,:]=[country,emission_df.name,item,intensity]
            # activity=compute_activity(mitigation_potential_df,emission_df,country,item)
            # output_activity_df.loc[index,:]=[country,emission_df.name,item,activity]
            index+=1
output_df.to_csv(output_file_name,index=False)

#output_activity_df.to_csv('output/activity_2050.csv',index=False)
