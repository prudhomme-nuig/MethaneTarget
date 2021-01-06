#! /bin/python

'''
Compute national nitrous oxyde intensity of manure and fertilization
'''

import pandas as pd
import numpy as np
from common_data import read_FAOSTAT_df
import argparse
from common_methane import compute_emission_intensity
from copy import deepcopy
import SI_pathways

parser = argparse.ArgumentParser('Compute national nitrous oxyde intensity of manure and fertilization')
parser.add_argument('--no-mitigation', action='store_true', help='No mitigation option')
parser.add_argument('--print-table', action='store_true', help='Print table')
parser.add_argument('--mitigation',  help='Change mitigation option')

args = parser.parse_args()

country_list=["France","Ireland","Brazil","India"]

animal_list=["Cattle, non-dairy","Cattle, dairy","Chickens, layers","Poultry Birds","Sheep and Goats","Swine"]

element_list=["Stocks","Emissions (N2O)"]

pathway_dict={"Ireland":["Ireland","Intensified"],#,"Intensification"
            "France":["France","Intensified"],#,"Intensified"
            "India":["India","Intensified"],#,"Intensified"
            "Brazil":["Brazil","Intensified"]}#,"Intensified"

production_dict={'Cattle, dairy':['Milk, Total','Beef and Buffalo Meat'],'Cattle, non-dairy':['Beef and Buffalo Meat'],'Rice, paddy':['Rice, paddy'],'Swine':['Meat, pig'],'Poultry Birds':['Meat, Poultry'],'Chickens, layers':['Eggs Primary'],'Sheep and Goats':['Sheep and Goat Meat'],'Synthetic Nitrogen fertilizers':['Synthetic Nitrogen fertilizers']}

#Mitigation potential and cost
# fom national MAC curves
#Option with or without mitigation aplied in 2050 for N2O and methane
if args.no_mitigation:
    mitigation_potential_df=pd.read_csv("data/no_mitigation.csv",dtype={"Mitigation potential":np.float64})
    file_name_suffix='_no_mitigation'
else:
    mitigation_potential_df=pd.read_csv("data/national_mitigation_mac.csv",dtype={"Mitigation potential":np.float64})
    file_name_suffix=''

if args.mitigation is not None:
    file_name_suffix+='_mitigation'+args.mitigation
else:
    file_name_suffix=''

item_of_df={"manure":animal_list,
            "fertilizer":['Synthetic Nitrogen fertilizers'],}

share_methane_df=pd.read_csv("output/Share_methane.csv")
share_N2O_df=pd.DataFrame(columns=share_methane_df.columns)
for index in share_methane_df.index:
    share_N2O_df.loc[index,:]=share_methane_df.loc[index,:]
    share_N2O_df.loc[index,'Value']=1-share_methane_df.loc[index,'Value']

N2O_fertilizer_df=read_FAOSTAT_df("data/FAOSTAT_N2O_fertilizer.csv",delimiter="|")
N2O_fertilizer_df.name="fertilizer"
nutrious_Man_df=pd.DataFrame(columns=["Area","Element","Item","Year","Value"])
index=0
item_list=deepcopy(animal_list)
item_list.append("Cattle")
for country in country_list:
    for item in item_list:
        for element in ["Emissions (N2O)","Stocks"]:
            nutrious_Man_df.loc[index,:]=[country,element,item,2010,0]
            for manure in ['management','application','left']:
                man_df=read_FAOSTAT_df("data/FAOSTAT_N2O_manure_"+manure+".csv",delimiter="|")
                if element=="Emissions (N2O)":
                    nutrious_Man_df.loc[index,'Value']+=man_df.loc[(man_df['Area']==country) & (man_df["Element"].str.contains(pat="Emissions \(N2O")) & (man_df['Item']==item),'Value'].values[0]
                elif element=="Stocks":
                    if nutrious_Man_df.loc[index,'Value']==0:
                        nutrious_Man_df.loc[index,'Value']+=man_df.loc[(man_df['Area']==country) & (man_df["Element"].str.contains(pat=element)) & (man_df['Item']==item),'Value'].values[0]
            index+=1
        nutrious_Man_df.loc[index,:]=[country,"Implied emission factor for N2O",item,2010,0]
        nutrious_Man_df.loc[index,'Value']=nutrious_Man_df.loc[index-2,'Value']/nutrious_Man_df.loc[index-1,'Value']
        index+=1
methane_Man_df=read_FAOSTAT_df("data/FAOSTAT_manure_management.csv",delimiter="|")
nutrious_Man_df.name="manure"
GWP100_CH4=34
GWP100_N2O=298
mitigation_list=["No mitigation","MACC"]
yields_df=read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")

#Compute new emission intensity
index=0
header_list=list(nutrious_Man_df.columns.values)
header_list.extend(["Pathways","Mitigation","Production"])
aggregate_df=pd.DataFrame(columns=header_list)
for df in [nutrious_Man_df,N2O_fertilizer_df]:
    for country in country_list:
        for item in item_of_df[df.name]:
            for mitigation in mitigation_list:
                for pathway in pathway_dict[country]:
                    for production in production_dict[item]:
                        if (pathway!=country) & (item in animal_list):
                            if (args.mitigation is not None) & (mitigation!="No mitigation"):
                                mitigation_strength=1+float(args.mitigation)/100
                            else:
                                mitigation_strength=1
                            mitigation_strength=float(mitigation_strength)*SI_pathways.compute_intake_change(country,item,production,yields_df)
                        else:
                            if (args.mitigation is not None) & (mitigation!="No mitigation"):
                                mitigation_strength=1+float(args.mitigation)/100
                            else:
                                mitigation_strength=1
                        if df.name=="manure":
                            value_stock=df.loc[(df["Area"]==country) & (df["Item"]==item) & (df["Element"]=="Stocks"),"Value"].values[0]
                        elif df.name=="fertilizer":
                            value_stock=df.loc[(df["Area"]==country) & (df["Item"]=="Synthetic Nitrogen fertilizers") & (df["Element"]=="Agricultural Use in nutrients"),"Value"].values[0]
                        value_emission=deepcopy(df.loc[(df["Area"]==country) & (df["Item"]==item) & (df["Element"].str.contains(pat ="Emissions")),"Value"].values[0])
                        if len(df.loc[(df["Area"]==country) & (df["Item"]==item) & (df["Element"].str.contains(pat ="Implied emission factor for N2O")),"Value"])==0:
                            df.loc[len(df),:]=["",country,"Implied emission factor for N2O",item,2010,"gigagrams",df.loc[(df["Area"]==country) & (df["Item"]==item) & (df["Element"].str.contains(pat ="Emissions \(N2O")),"Value"].values[0]/df.loc[(df["Area"]==country) & (df["Item"]==item) & (df["Element"].str.contains(pat ="Stocks")),"Value"].values[0]]
                        if df.name=="manure":
                            df.loc[(df["Area"]==country) & (df["Item"]==item) & (df["Element"].str.contains(pat ="Implied emission factor for N2O")),"Value"]=df.loc[(df["Area"]==country) & (df["Item"]==item) & (df["Element"].str.contains(pat ="Emissions \(N2O")),"Value"].values[0]/df.loc[(df["Area"]==country) & (df["Item"]==item) & (df["Element"].str.contains(pat ="Stocks")),"Value"].values[0]
                        if (item in mitigation_potential_df.loc[mitigation_potential_df["Country"]==country,"Item"].values) | (("Cattle" in item) & ("Cattle" in mitigation_potential_df.loc[mitigation_potential_df["Country"]==country,"Item"].values)) | (("All animals" in mitigation_potential_df.loc[mitigation_potential_df["Country"]==country,"Item"].values) and (item in animal_list)):
                            if mitigation=='MACC':
                                if args.mitigation is None:
                                    value=float(mitigation_strength)*compute_emission_intensity(mitigation_potential_df.loc[mitigation_potential_df["Country"]==country,:],df,country,item,share_N2O_df,"N2O")
                                else:
                                    value=float(mitigation_strength)*df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor for N2O" in list_element for list_element in df["Element"]]),"Value"].values[0]
                            else:
                                value=float(mitigation_strength)*df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor for N2O" in list_element for list_element in df["Element"]]),"Value"].values[0]
                        else:
                            value=float(mitigation_strength)*value_emission/value_stock
                        if df.name=="manure":
                            aggregate_df.loc[index,:]=[country,"Implied emission factor",item,2010,value,pathway,mitigation,production]
                        else:
                            aggregate_df.loc[index,:]=[country,"Implied emission factor",item,2010,value,pathway,mitigation,production]
                        index+=1
                        aggregate_df.loc[index,:]=[country,"Emissions (N2O)",item,2010,value_emission,pathway,mitigation,production]
                        index+=1
                        if df.name=="manure":
                            aggregate_df.loc[index,:]=[country,"Stocks",item,2010,value_stock,pathway,mitigation,production]
                        else:
                            aggregate_df.loc[index,:]=[country,"Synthetic Nitrogen fertilizers",item,2010,value_stock,pathway,mitigation,production]
                        index+=1
output_df=aggregate_df.loc[aggregate_df["Element"]=="Implied emission factor",["Area","Element","Item","Value","Pathways","Mitigation","Production"]]
output_df=output_df.rename(columns = {'Area':'Country'})
output_df=output_df.rename(columns = {'Value':'Intensity'})
mask_fertilizer=output_df["Item"]=="Synthetic Nitrogen fertilizers"
mask_manure=output_df["Item"]!="Synthetic Nitrogen fertilizers"
output_df.loc[mask_fertilizer,"Element"]="fertilizer"
output_df.loc[mask_manure,"Element"]="Manure total"
output_df=output_df.rename(columns = {'Element':'Emission'})
output_df.to_csv('output/emission_intensity_N2O'+file_name_suffix+'.csv',index=False)

if args.print_table:
    output_ref_df=pd.DataFrame(columns=output_df.columns)
    nutrious_Man_df.name="manure"
    for emission_df in [nutrious_Man_df,N2O_fertilizer_df]:
        for country in country_list:
            for item in item_of_df[emission_df.name]:
                for pathway in pathway_dict[country]:
                    for mitigation in mitigation_list:
                        for production in production_dict[item]:
                            if 'manure' in emission_df.name:
                                intensity=emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Emissions (N2O)" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]/emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (["Stocks" in list_element for list_element in emission_df["Element"]]),'Value'].values[0]
                                output_ref_df.loc[index,:]=[country,emission_df.name,item,intensity,pathway,mitigation,production]
                            else:
                                intensity=emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (emission_df['Element']=="Emissions (N2O) (Synthetic fertilizers)"),'Value'].values[0]/emission_df.loc[(emission_df['Area']==country) & (emission_df['Item']==item) & (emission_df['Element']=="Agricultural Use in nutrients"),"Value"].values[0]
                                output_ref_df.loc[index,:]=[country,emission_df.name,item,intensity,pathway,mitigation,production]
                            index+=1
    t_to_kg=1000
    output_df["EI 2050"]=output_df["Intensity"].values*t_to_kg #(kgN2O/Head or kgN2O/tN)
    output_df["EI 2010"]=output_ref_df["Intensity"].values*t_to_kg
    mask=output_df["EI 2010"]>0
    output_df["EI index"]=0
    output_df.loc[mask,"EI index"]=output_df.loc[mask,"EI 2050"]/output_df.loc[mask,"EI 2010"]
    output_df["Intensification"]=np.nan
    output_df.loc[(output_df["Mitigation"]!="MACC") & (output_df["Pathways"]!="Intensified"),"Intensification"]="Base"
    output_df.loc[(output_df["Mitigation"]=="MACC") & (output_df["Pathways"]!="Intensified"),"Intensification"]="2050 MACC"
    output_df.loc[(output_df["Mitigation"]=="MACC") & (output_df["Pathways"]=="Intensified"),"Intensification"]="2050 SI"
    # output_df.loc[output_df['Country']!=output_df['Pathways'],'Pathway']='Intensified'
    # output_df.loc[output_df['Country']==output_df['Pathways'],'Pathway']='Current'
    output_df["Type of product"]=output_df[["Item","Production"]].agg('-'.join, axis=1)
    table = pd.pivot_table(output_df, values=['EI 2050'], columns=["Emission","Intensification"], index=['Country','Type of product'],aggfunc="first")
    table.index.name=None
    table.columns = table.columns.swaplevel(0, 1)
    table.sort_index(level=0, axis=1, inplace=True)
    table.to_excel("output/table_N2O_EI.xlsx",index_label=None)
