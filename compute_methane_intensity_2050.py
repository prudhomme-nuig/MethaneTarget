#! /bin/python

import pandas as pd
import numpy as np
from common_data import read_FAOSTAT_df

country_list=["France","Ireland","Brazil","India","Netherlands"]
animal_list=["Cattle","Chickens","Mules and Asses","Poultry Birds","Sheep and Goats","Swine"]

#Mitigation potential and cost
# fom national MAC curves
mitigation_potential_df=pd.read_csv("data/national_mitigation_mac.csv",dtype={"Mitigation potential":np.float64})

#Read methane emissions in 2010 from FAOSTAT
methane_df=read_FAOSTAT_df("data/FAOSTAT_methane.csv",delimiter=",")
methane_Ent_Ferm_df=read_FAOSTAT_df("data/FAOSTAT_enteric_fermentation.csv",delimiter=",")
methane_Ent_Ferm_df.name="enteric"
methane_Man_df=read_FAOSTAT_df("data/FAOSTAT_manure_management.csv",delimiter=",")
methane_Man_df.name="manure"
methane_rice_df=read_FAOSTAT_df("data/FAOSTAT_rice.csv",delimiter=",")
methane_rice_df.name="rice"
item_of_df={methane_rice_df.name:["Rice, paddy"],
            methane_Man_df.name:animal_list,
            methane_Ent_Ferm_df.name:["Cattle"]}
#item_to_product_dict={'Cattle':['Milk, Total','Beef and Buffalo Meat'],'Swine':['Meat, pig'],'Chickens':['Meat, Poultry','Eggs Primary'],'Poultry Birds':['Meat, Poultry'],'Sheep and Goats':['Sheep and Goat Meat']}

def compute_emission_intensity(mitigation_potential_df,df,country,item):
    mitigation_df=mitigation_potential_df.loc[mitigation_potential_df["Emission"]==df.name,:]
    for index in mitigation_df.index:
        if mitigation_df.loc[index,"Indicator"]=="share":
            emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor" in list_element for list_element in df["Element"]]),"Value"].values[0]*(1-mitigation_df.loc[index,"Mitigation potential"])
        elif mitigation_df.loc[index,"Indicator"]=="mitigation":
            emission_total=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Emissions (CH4)" in list_element for list_element in df["Element"]]),"Value"].values[0]-mitigation_df.loc[index,"Mitigation potential"]
            emission_intensity=emission_total/df.loc[(df["Area"]=="Country") & (df["Year"]==2010) & (df["Element"]=="Stocks"),"Value"]
        elif mitigation_df.loc[index,"Indicator"]=="mitigation per ha":
            emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor" in list_element for list_element in df["Element"]]),"Value"].values[0]-mitigation_df.loc[index,"Mitigation potential"]
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
            df.loc[index,:]=["",country,"Implied emission factor",item,2010,"tCH4/head",value]
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
                    emission_intensity=compute_emission_intensity(mitigation_potential_df,emission_df,country,item)
                    output_df.loc[index,:]=[country,emission_df.name,item,emission_intensity]
                else:
                    if emission_df.name in ['manure','enteric']:
                        intensity=emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]/emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Stocks" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                    else:
                        intensity=emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]/emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Area harvested" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                    output_df.loc[index,:]=[country,emission_df.name,item,intensity]
            activity=compute_activity(mitigation_potential_df,emission_df,country,item)
            output_activity_df.loc[index,:]=[country,emission_df.name,item,activity]
            index+=1
output_df.to_csv('output/emission_intensity_2050.csv',index=False)
#output_activity_df.to_csv('output/activity_2050.csv',index=False)
