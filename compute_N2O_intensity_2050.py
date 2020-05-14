#! /bin/python

'''
Compute national nitrous oxyde intensity of manure and fertilization
'''

import pandas as pd
import numpy as np
from common_data import read_FAOSTAT_df
import argparse

parser = argparse.ArgumentParser('Compute national nitrous oxyde intensity of manure and fertilization')
parser.add_argument('--no-mitigation', action='store_true', help='No mitigation option')
parser.add_argument('--print-table', action='store_true', help='Print table')

args = parser.parse_args()

country_list=["France","Ireland","Brazil","India"]

animal_list=["Cattle, non-dairy","Cattle, dairy","Chickens, layers","Poultry Birds","Sheep and Goats","Swine"]

element_list=["Stocks","Emissions (N2O)"]
#Mitigation potential and cost
# fom national MAC curves
#Option with or without mitigation aplied in 2050 for N2O and methane
if args.no_mitigation:
    mitigation_potential_df=pd.read_csv("data/no_mitigation.csv",dtype={"Mitigation potential":np.float64})
    output_file_name='output/emission_intensity_N2O_no_mitigation.csv'
else:
    mitigation_potential_df=pd.read_csv("data/national_mitigation_mac.csv",dtype={"Mitigation potential":np.float64})
    output_file_name='output/emission_intensity_N2O.csv'

#Read methane emissions in 2010 from FAOSTAT
N2O_df=read_FAOSTAT_df("data/FAOSTAT_N2O_reference.csv",delimiter=",")
N2O_fertilizer_df=read_FAOSTAT_df("data/FAOSTAT_N2O_fertilizer.csv",delimiter=",")
N2O_fertilizer_df.name="fertilizer"
N2O_Man_man_df=read_FAOSTAT_df("data/FAOSTAT_N2O_manure_management.csv",delimiter="|")
N2O_Man_man_df.name="manure"
N2O_Man_app_df=read_FAOSTAT_df("data/FAOSTAT_N2O_manure_application.csv",delimiter="|")
N2O_Man_app_df.name="manure application"
N2O_Man_left_df=read_FAOSTAT_df("data/FAOSTAT_N2O_manure_left.csv",delimiter="|")
N2O_Man_left_df.name="manure left"
emission_type_list=["manure","rice"]
item_of_df={"manure application":animal_list,
            "manure management":animal_list,
            "manure left":animal_list,
            "Manure total":animal_list,
            "fertilizer":['Synthetic Nitrogen fertilizers'],}
#item_to_product_dict={'Cattle':['Milk, Total','Beef and Buffalo Meat'],'Swine':['Meat, pig'],'Chickens':['Meat, Poultry','Eggs Primary'],'Poultry Birds':['Meat, Poultry'],'Sheep and Goats':['Sheep and Goat Meat']}

nutrious_Man_df=pd.DataFrame(columns=["Area","Item","Element","Year","Value"])
nutrious_Man_df.name="manure"
index=0
for country in country_list:
    for item in animal_list:
        for element in element_list:
            nutrious_Man_df.loc[index,:]=[country,item,element,2010,0]
            for manure in ['management','application','left']:
                if manure=="application":
                    manure_element_name="applied"
                elif manure=="left":
                    manure_element_name="on pasture"
                else:
                    manure_element_name=manure
                if element=="Emissions (N2O)":
                    element_for_mask=element+" (Manure "+manure_element_name+")"
                else:
                    element_for_mask=element
                man_df=read_FAOSTAT_df("data/FAOSTAT_N2O_manure_"+manure+".csv",delimiter="|")
                mask=(man_df['Area']==country) & (man_df['Element']==element_for_mask) & (man_df['Item']==item)
                nutrious_Man_df.loc[index,'Value']+=man_df.loc[mask,'Value'].values[0]
            index+=1
methane_Man_df=read_FAOSTAT_df("data/FAOSTAT_manure_management.csv",delimiter="|")
GWP100_CH4=34
GWP100_N2O=298
index=0
share_nitrous_df=pd.DataFrame(columns=["Country","Item","Year","Value"])
for country in country_list:
    for item in animal_list:
        share_nitrous_df.loc[index,:]=[country,item,2010,0]
        share_nitrous_df.loc[index,'Value']=nutrious_Man_df.loc[(nutrious_Man_df['Area']==country) & (nutrious_Man_df['Element']=='Emissions (N2O)') & (nutrious_Man_df['Item']==item),'Value'].values[0]*GWP100_N2O/(methane_Man_df.loc[(methane_Man_df['Area']==country) & (methane_Man_df['Element']=='Emissions (CH4) (Manure management)') & (methane_Man_df['Item']==item),'Value'].values[0]*GWP100_CH4+nutrious_Man_df.loc[(nutrious_Man_df['Area']==country) & (nutrious_Man_df['Item']==item) & (nutrious_Man_df['Element']=='Emissions (N2O)'),'Value'].values[0]*GWP100_N2O)
        index+=1

table = pd.pivot_table(share_nitrous_df, values=['Value'], index=['Country'],columns=["Item"],aggfunc='first')
table.index.name=None
table.to_excel("output/table_share_nitrous_manure_emis.xlsx",index_label=None,float_format = "%0.3f")

share_dairy_df=pd.DataFrame(columns=country_list,index=["Share dairy herd in cattle herd"])
for country in country_list:
    cattle_dairy=nutrious_Man_df.loc[(nutrious_Man_df["Area"]==country) & (nutrious_Man_df["Element"]=="Stocks") & (nutrious_Man_df["Item"]=="Cattle, dairy"),'Value'].values[0]
    cattle_non_dairy=nutrious_Man_df.loc[(nutrious_Man_df["Area"]==country) & (nutrious_Man_df["Element"]=="Stocks") & (nutrious_Man_df["Item"]=="Cattle, non-dairy"),'Value'].values[0]
    share_dairy_df.loc["Share dairy herd in cattle herd",country]=cattle_dairy/(cattle_dairy+cattle_non_dairy)

def compute_emission_intensity(mitigation_potential_df,df,country,item):
    mitigation_df=mitigation_potential_df.loc[mitigation_potential_df["Emission"]==df.name,:]
    if "Cattle" in item:
        item_list=["Cattle",item]
    else:
        item_list=[item]
    mitigation_df=mitigation_df.loc[mitigation_df["Item"].str.contains('|'.join(item_list)),:]
    for index in mitigation_df.index:
        if mitigation_df.loc[index,"gaz"]=='both':
            gaz_share=share_nitrous_df.loc[(share_nitrous_df['Country']==country) & (share_nitrous_df['Item']==item),'Value'].values[0]/GWP100_N2O
        elif mitigation_df.loc[index,"gaz"]=='N2O':
            gaz_share=1
        else:
            gaz_share=0
        if mitigation_df.loc[index,"Item"]=="Cattle":
            if item=="Cattle, dairy":
                share_item=share_dairy_df.loc["Share dairy herd in cattle herd",country]
            else:
                share_item=1-share_dairy_df.loc["Share dairy herd in cattle herd",country]
        else:
            share_item=1
        if mitigation_df.loc[index,"Indicator"]=="share":
            emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor" in list_element for list_element in df["Element"]]),"Value"].values[0]*(1-mitigation_df.loc[index,"Mitigation potential"])
        elif mitigation_df.loc[index,"Indicator"]=="mitigation":
            emission_total=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Emissions (N2O)" in list_element for list_element in df["Element"]]),"Value"].values[0]-mitigation_df.loc[index,"Mitigation potential"]*gaz_share*share_item
            emission_intensity=emission_total/df.loc[(df["Area"]=="Country") & (df["Year"]==2010) & (df["Element"]=="Stocks"),"Value"]
        elif mitigation_df.loc[index,"Indicator"]=="mitigation per ha":
            emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor" in list_element for list_element in df["Element"]]),"Value"].values[0]-mitigation_df.loc[index,"Mitigation potential"]*gaz_share
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
        value_stock=nutrious_Man_df.loc[(nutrious_Man_df["Area"]==country) & (nutrious_Man_df["Item"]==item) & (nutrious_Man_df["Element"]=="Stocks"),"Value"].values[0]
        value_emission=nutrious_Man_df.loc[(nutrious_Man_df["Area"]==country) & (nutrious_Man_df["Item"]==item) & (nutrious_Man_df["Element"]=="Emissions (N2O)"),"Value"].values[0]
        if item in mitigation_potential_df["Item"]:
            value=compute_emission_intensity(mitigation_potential_df,nutrious_Man_df,country,item)
        else:
            value=value_emission/value_stock
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
output_df.to_csv(output_file_name,index=False)
#output_activity_df.to_csv('output/activity_2050.csv',index=False)

if args.print_table:
    output_ref_df=pd.DataFrame(columns=output_df.columns)
    nutrious_Man_df.name="Manure total"
    for emission_df in [nutrious_Man_df,N2O_fertilizer_df]:
        for country in country_list:
            for item in item_of_df[emission_df.name]:
                if 'Manure' in emission_df.name:
                    if emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (N2O)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]==0:
                        output_ref_df.loc[index,:]=[country,emission_df.name,item,0]
                    else:
                        intensity=emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (N2O)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]/emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Stocks" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                        output_ref_df.loc[index,:]=[country,emission_df.name,item,intensity]
                else:
                    if emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Implied" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]==0:
                        output_ref_df.loc[index,:]=[country,emission_df.name,item,0]
                    else:
                        intensity=emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Implied" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                        output_ref_df.loc[index,:]=[country,emission_df.name,item,intensity]
                index+=1
    t_to_kg=1000
    output_df["EI 2050 (kgN2O/Head or kgN2O/tN)"]=output_df["Intensity"].values*t_to_kg
    output_df["EI 2010 (kgN2O/Head or kgN2O/tN)"]=output_ref_df["Intensity"].values*t_to_kg
    mask=output_df["EI 2010 (kgN2O/Head or kgN2O/tN)"]>0
    output_df["EI index (2050 relative to 2010)"]=0
    output_df.loc[mask,"EI index (2050 relative to 2010)"]=output_df.loc[mask,"EI 2050 (kgN2O/Head or kgN2O/tN)"]/output_df.loc[mask,"EI 2010 (kgN2O/Head or kgN2O/tN)"]
    table = pd.pivot_table(output_df, values=['EI 2010 (kgN2O/Head or kgN2O/tN)','EI 2050 (kgN2O/Head or kgN2O/tN)','EI index (2050 relative to 2010)'], index=['Country','Item',"Emission"],aggfunc='first')
    table.index.name=None
    table.to_excel("output/table_N2O_EI.xlsx",index_label=None,float_format = "%0.5f")
