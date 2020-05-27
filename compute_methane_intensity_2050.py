#! /bin/python

'''
Compute methane intensity per unit of production in 2050 for each intensification pathway, with and without mitigation
'''

import pandas as pd
import numpy as np
from common_data import read_FAOSTAT_df
import argparse
from common_methane import compute_emission_intensity
from copy import deepcopy

parser = argparse.ArgumentParser('Compute methane intensity per unit of production in 2050 for each intensification pathway')
parser.add_argument('--mitigation',  help='Change mitigation option')
parser.add_argument('--print-table', action='store_true', help='Print table')
parser.add_argument('--no-mitigation', action='store_true', help='No mitigation option')

args = parser.parse_args()

country_list=["France","Ireland","Brazil","India"]
# country_pd=pd.read_csv("output/model_country.csv",index_col=0)
# country_list=list(np.unique(country_pd.values))
# country_list.extend(list(country_pd.columns))

animal_list=["Cattle, non-dairy","Cattle, dairy","Chickens, layers","Poultry Birds","Sheep and Goats","Swine"]
GWP100_CH4=34
GWP100_N2O=298

#Mitigation potential and cost
# fom national MAC curves
#Option with or without mitigation applied in 2050 for methane
if args.no_mitigation:
    mitigation_potential_df=pd.read_csv("data/no_mitigation.csv",dtype={"Mitigation potential":np.float64})
    file_name_suffix='_no_mitigation'
else:
    mitigation_potential_df=pd.read_csv("data/national_mitigation_mac.csv",dtype={"Mitigation potential":np.float64})
    file_name_suffix=""

# Stronger mitigation option than ones computed in MAC curves
if args.mitigation is not None:
    mitigation_strength=1+float(args.mitigation)/100
    file_name_suffix+='_mitigation'+args.mitigation
else:
    mitigation_strength=1
    file_name_suffix+=""

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
share_methane_df.to_csv("output/Share_methane.csv",index=False)
#item_to_product_dict={'Cattle':['Milk, Total','Beef and Buffalo Meat'],'Swine':['Meat, pig'],'Chickens':['Meat, Poultry','Eggs Primary'],'Poultry Birds':['Meat, Poultry'],'Sheep and Goats':['Sheep and Goat Meat']}

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
            if len(emission_df.loc[(emission_df['Item']==item) & (["Implied emission factor for CH4" in list_element for list_element in emission_df["Element"]]),'Value'].values)==0:
                name_tmp=deepcopy(emission_df.name)
                emission_tmp_df=emission_df.loc[(emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),:]
                emission_tmp_df.loc[:,"Element"]="Implied emission factor for CH4"
                if "Rice" in item:
                    element_name="Area harvested"
                else:
                    element_name="Stocks"
                emission_tmp_df.loc[:,"Value"]=emission_df.loc[(emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),'Value'].values/emission_df.loc[(emission_df['Item']==item) & ([element_name in list_element for list_element in emission_df["Element"]]),'Value'].values
                emission_df=pd.concat([emission_df,emission_tmp_df],axis=0,ignore_index=True)
                emission_df.name=name_tmp
            if emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]==0:
                output_df.loc[index,:]=[country,emission_df.name,item,0]
            else:
                if emission_df.name in mitigation_potential_df.loc[mitigation_potential_df["Country"]==country,"Emission"].values:
                    emission_intensity=compute_emission_intensity(mitigation_potential_df.loc[mitigation_potential_df["Country"]==country,:],emission_df,country,item,share_methane_df,"CH4")
                    output_df.loc[index,:]=[country,emission_df.name,item,mitigation_strength*emission_intensity]
                else:
                    if emission_df.name in ['manure','enteric']:
                        intensity=mitigation_strength*emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]/emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Stocks" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                    else:
                        intensity=mitigation_strength*emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]/emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Area harvested" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                    output_df.loc[index,:]=[country,emission_df.name,item,intensity]
            # activity=compute_activity(mitigation_potential_df,emission_df,country,item)
            # output_activity_df.loc[index,:]=[country,emission_df.name,item,activity]
            index+=1
output_df.to_csv('output/emission_intensity_2050'+file_name_suffix+'.csv',index=False)

if args.print_table:
    output_ref_df=pd.DataFrame(columns=output_df.columns)
    for emission_df in [methane_Ent_Ferm_df,methane_rice_df,methane_Man_df]:
        for country in country_list:
            for item in item_of_df[emission_df.name]:
                if emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]==0:
                    output_ref_df.loc[index,:]=[country,emission_df.name,item,0]
                else:
                    if emission_df.name in ['manure','enteric']:
                        intensity=emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]/emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Stocks" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                    else:
                        intensity=emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (CH4)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]/emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Area harvested" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                    output_ref_df.loc[index,:]=[country,emission_df.name,item,intensity]
                index+=1
    output_df["EI 2050"]=output_df["Intensity"].values #(tCH4/Head or tCH4/ha)
    output_df["EI 2010"]=output_ref_df["Intensity"].values #(tCH4/Head or tCH4/ha)
    mask=output_df["EI 2010"]>0
    output_df["EI index"]=0
    output_df.loc[mask,"EI index"]=output_df.loc[mask,"EI 2050"]/output_df.loc[mask,"EI 2010"] # (2050 relative to 2010)
    table = pd.pivot_table(output_df, values=['EI 2010','EI 2050','EI index'], index=['Country','Item'],columns=["Emission"],aggfunc='first')
    table.index.name=None
    table.columns = table.columns.swaplevel(0, 1)
    table.sort_index(level=0, axis=1, inplace=True)
    table.to_excel("output/table_methane_EI"+file_name_suffix+".xlsx",index_label=None,float_format = "%0.3f")
