#! /bin/python

import csv
from copy import deepcopy
from common_data import GWP100_N2O,GWP100_CH4,read_FAOSTAT_df
import pandas as pd
import numpy as np

def read_FAO_file(fname,country,element,item=None,delimiter=','):
    table_dict={}
    file=open(fname, 'r')
    csv_input = csv.reader(file,delimiter=delimiter)
    index=0
    for row in csv_input:
        if index==0:
            header=row
            item_index=header.index('Item')
            element_index=header.index('Element')
            country_index=header.index('Area')
            value_index=header.index('Value')
        else:
            if row[country_index] not in table_dict.keys():
                table_dict[row[country_index]]={row[element_index]:{row[item_index]:float(row[value_index])}}
            else:
                if row[element_index] not in table_dict[row[country_index]].keys():
                    table_dict[row[country_index]][row[element_index]]={row[item_index]:float(row[value_index])}
                else:
                    if row[item_index] not in table_dict[row[country_index]][row[element_index]]:
                        table_dict[row[country_index]][row[element_index]][row[item_index]]=float(row[value_index])
        index+=1
    return table_dict

def print_table_results(activity_df,country_list,column_name_to_variable_name_dict):
    print_table_dict={}
    print_table_df=pd.DataFrame(columns=column_name_to_variable_name_dict.keys())
    for header_1 in column_name_to_variable_name_dict.keys():
        print_table_dict[header_1]={}
        for header_2 in column_name_to_variable_name_dict[header_1].keys():
            column_name_list=["2010"]
            column_name_list.extend(list(np.unique(activity_df['Allocation rule'])))
            print_table_dict[header_1][header_2]=pd.DataFrame(columns=column_name_list)
        print_table_dict[header_1]=pd.concat(print_table_dict[header_1], axis=1)
    print_table_df=pd.concat(print_table_dict, axis=1)
    print_table_df=pd.DataFrame(print_table_df,index=country_list)
    for country in country_list:
        activity_country_df=activity_df.loc[activity_df["Country"]==country,:]
        for header_1 in column_name_to_variable_name_dict.keys():
            for header_2 in column_name_to_variable_name_dict[header_1].keys():
                for allocation in column_name_list:
                    if allocation=="2010":
                        variable_name_suffix=" 2010"
                        allocation_mask=(activity_country_df["Allocation rule"]!=np.nan)
                    else:
                        allocation_mask=activity_country_df["Allocation rule"]==allocation
                        variable_name_suffix=""
                    if (header_1=="Methane quota") & (allocation=="2010"):
                        variable_tmp=activity_country_df["2010"]*activity_country_df["Share"]
                    elif (header_1=="CO2 offset") & (allocation=="2010"):
                        variable_tmp=pd.Series([0,0])
                    else:
                        variable_tmp=np.sum([activity_country_df.loc[allocation_mask,variable_name+variable_name_suffix] for variable_name in column_name_to_variable_name_dict[header_1][header_2]],axis=0)
                    print_table_df.loc[country,(header_1,header_2,allocation)]=variable_tmp.mean()
    return print_table_df

def compute_CO2_equivalent(input_df,rule,emission_ref_year,country,ponderation_in_GWP_star=None,methane_debt=None):
    output_df=deepcopy(input_df)
    is_GWP100=False
    Horizon=100.
    if rule=='Grand-fathering':
        emission_ref=emission_ref_year
    elif rule=='Debt':
        emission_ref=np.max([methane_debt[country].values[0],0])
    elif rule=='GDP':
        emission_ref=np.max([methane_debt[country].values[0],0])
    elif rule=='Population':
        emission_ref=emission_ref_year*ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']==country]['2010'].values[0]/ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']=='World']['2010'].values[0]
    elif rule=='Protein':
        emission_ref=emission_ref_year*ponderation_in_GWP_star[country].values[0]
    elif rule=='GWP100':
        is_GWP100=True
    else:
        print('Unknown method. Code it!')
    if is_GWP100:
        output_df=input_df*GWP100_CH4
    else:
        output_df=(input_df.values-emission_ref)*(GWP100_CH4*100.)/40.
    return output_df

def compute_emission_intensity(mitigation_potential_df,df,country,item,share_methane_df,gaz):
    GWP100={"CH4":34,"N2O":298}
    animal_list=["Cattle","Poultry Birds","Sheep and Goats","Swine"]
    all_animal_list=["Cattle","Cattle, dairy","Cattle, non-dairy","Poultry Birds","Sheep and Goats","Swine","Chickens, layers"]
    mitigation_df=mitigation_potential_df.loc[mitigation_potential_df["Emission"]==df.name,:]
    df_excreted=read_FAOSTAT_df("data/FAOSTAT_manure_excreted.csv",delimiter="|")
    if item =='Rice, paddy':
        item_name='Rice'
    elif item =='Synthetic Nitrogen fertilizers':
        item_name='Synthetic Nitrogen fertilizers'
    else:
        item_name=item
    if item in all_animal_list:
        element_name="Stocks"
    elif item=="Synthetic Nitrogen fertilizers":
        element_name="Agricultural Use in nutrients"
    elif item=='Rice, paddy':
        element_name="Area harvested"
    emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor for "+gaz in list_element for list_element in df["Element"]]),"Value"].values[0]
    for index in mitigation_df.index:
        if ((mitigation_df.loc[index,"gaz"]==gaz) | (mitigation_df.loc[index,"gaz"]=='both')) & ((mitigation_df.loc[index,"Item"] in item_name)) | ((mitigation_df.loc[index,"Item"]=='All animals') & (item_name in all_animal_list)):
            if mitigation_df.loc[index,"gaz"]=='both':
                gaz_share=share_methane_df.loc[(share_methane_df['Country']==country) & (share_methane_df['Item']==item),'Value'].values[0]/GWP100[gaz]
            elif mitigation_df.loc[index,"gaz"]=='CH4':
                gaz_share=1
            else:
                gaz_share=0
            if (mitigation_df.loc[index,"Item"]=="Cattle"):
                share_item=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010)  & (df["Element"]=="Stocks"),"Value"].values[0]/df.loc[(df["Item"]=="Cattle") & (df["Area"]==country) & (df["Year"]==2010) & (df["Element"]=="Stocks"),"Value"].values[0]
            elif (mitigation_df.loc[index,"Item"]=="All animals"):
                share_item=df_excreted.loc[(df_excreted["Item"]==item) & (df_excreted["Area"]==country) & (df_excreted["Year"]==2010),"Value"].values[0]/np.sum([df_excreted.loc[(df_excreted["Item"]==animal) & (df_excreted["Area"]==country) & (df_excreted["Year"]==2010),"Value"].values[0] for animal in animal_list])
            else:
                share_item=1
            if mitigation_df.loc[index,"Indicator"]=="share":
                emission_intensity=emission_intensity*(1-mitigation_df.loc[index,"Mitigation potential"])
            elif mitigation_df.loc[index,"Indicator"]=="mitigation":
                emission_total=-(mitigation_df.loc[index,"Mitigation potential"]*gaz_share*share_item)
                emission_intensity_change=emission_total/df.loc[(df["Area"]==country) & (df["Year"]==2010) & (df["Item"]==item) & (df["Element"]==element_name),"Value"].values[0]
                emission_intensity=emission_intensity+emission_intensity_change
            elif mitigation_df.loc[index,"Indicator"]=="mitigation per ha":
                emission_intensity=emission_intensity-(mitigation_df.loc[index,"Mitigation potential"]*gaz_share)
            elif mitigation_df.loc[index,"Indicator"]=="mitigation per head":
                emission_intensity=emission_intensity-(mitigation_df.loc[index,"Mitigation potential"]*gaz_share)
            # if item=="Swine":
            #     import pdb; pdb.set_trace()
    if emission_intensity<0:
        emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Implied emission factor for "+gaz in list_element for list_element in df["Element"]]),"Value"].values[0]*0.1
        # else:
        #     if item =='Rice, paddy':
        #         emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Emissions ("+gaz+")" in list_element for list_element in df["Element"]]),"Value"].values[0]/df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (df["Element"]=="Area harvested"),"Value"].values[0]
        #     else:
        #         emission_intensity=df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (["Emissions ("+gaz+")" in list_element for list_element in df["Element"]]),"Value"].values[0]/df.loc[(df["Item"]==item) & (df["Area"]==country) & (df["Year"]==2010) & (df["Element"]=="Stocks"),"Value"].values[0]
        #import pdb;pdb.set_trace()
    return emission_intensity
