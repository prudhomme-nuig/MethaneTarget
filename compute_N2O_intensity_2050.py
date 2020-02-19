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
N2O_df=read_FAOSTAT_df("data/FAOSTAT_N2O_reference.csv",delimiter=",")
N2O_fertilizer_df=read_FAOSTAT_df("data/FAOSTAT_N2O_fertilizer.csv",delimiter=",")
N2O_fertilizer_df.name="fertilizer"
N2O_Man_man_df=read_FAOSTAT_df("data/FAOSTAT_N2O_manure_management.csv",delimiter=",")
N2O_Man_man_df.name="manure management"
N2O_Man_app_df=read_FAOSTAT_df("data/FAOSTAT_N2O_manure_application.csv",delimiter=",")
N2O_Man_app_df.name="manure application"
N2O_Man_left_df=read_FAOSTAT_df("data/FAOSTAT_N2O_manure_left.csv",delimiter=",")
N2O_Man_left_df.name="manure left"
emission_type_list=["manure","rice"]
item_of_df={"manure application":animal_list,
            "manure management":animal_list,
            "manure left":animal_list,
            "Manure total":animal_list,
            "fertilizer":['Synthetic Nitrogen fertilizers'],}
#item_to_product_dict={'Cattle':['Milk, Total','Beef and Buffalo Meat'],'Swine':['Meat, pig'],'Chickens':['Meat, Poultry','Eggs Primary'],'Poultry Birds':['Meat, Poultry'],'Sheep and Goats':['Sheep and Goat Meat']}

def compute_emission_intensity(mitigation_potential_df,df,country,item):
    mitigation_df=mitigation_potential_df.loc[mitigation_potential_df["Emission"]==df.name,:]
    for index in mitigation_df.index:
        if mitigation_df.loc[index,"Indicator"]=="share":
            emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor" in list_element for list_element in df["Element"]]),"Value"].values[0]*(1-mitigation_df.loc[index,"Mitigation potential"])
        elif mitigation_df.loc[index,"Indicator"]=="mitigation":
            emission_total=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Emissions (N2O)" in list_element for list_element in df["Element"]]),"Value"].values[0]-mitigation_df.loc[index,"Mitigation potential"]
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

#Aggregate manure emission sources and Recompute implied emission factor because it is not always computed in FAOSTAT
index=0
aggregate_df=pd.DataFrame(columns=N2O_Man_man_df.columns)
for country in country_list:
    for item in animal_list:
        value_emission=0
        for df in [N2O_Man_man_df,N2O_Man_app_df,N2O_Man_left_df]:
            value_emission+=df.loc[(df["Area"]==country) & (df["Item"]==item) & (["Emissions (N2O)" in list_element for list_element in df["Element"]]),"Value"].values[0]
            value_stock=df.loc[(df["Area"]==country) & (df["Item"]==item) & (["Stock" in list_element for list_element in df["Element"]]),"Value"].values[0]
        if value_stock>0:
            value=value_emission/value_stock
        else:
            value=0
        aggregate_df.loc[index,:]=["",country,"Implied emission factor",item,2010,"tN2O/head",value]
        index+=1
        aggregate_df.loc[index,:]=["",country,"Emissions (N2O)",item,2010,"tN2O",value_emission]
        index+=1
        aggregate_df.loc[index,:]=["",country,"Stocks",item,2010,"head",value_stock]
        index+=1
aggregate_df.name='Manure total'

output_df=pd.DataFrame(columns=["Country","Emission","Item","Intensity"])
output_activity_df=pd.DataFrame(columns=["Country","Emission","Item","Activity"])
index=0
for emission_df in [aggregate_df,N2O_fertilizer_df]:
    for country in country_list:
        for item in item_of_df[emission_df.name]:
            if 'Manure' in emission_df.name:
                if emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (N2O)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]==0:
                    output_df.loc[index,:]=[country,emission_df.name,item,0]
                else:
                    intensity=emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (N2O)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]/emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Stocks" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                    output_df.loc[index,:]=[country,emission_df.name,item,intensity]
            else:
                if emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Implied" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]==0:
                    output_df.loc[index,:]=[country,emission_df.name,item,0]
                else:
                    intensity=emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Implied" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                    output_df.loc[index,:]=[country,emission_df.name,item,intensity]
            index+=1
output_df.to_csv('output/emission_intensity_N2O.csv',index=False)
#output_activity_df.to_csv('output/activity_2050.csv',index=False)
