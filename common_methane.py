#! /bin/python

import csv
from copy import deepcopy
from common_data import GWP100_N2O,GWP100_CH4
import pandas as pd
import numpy as np

def read_table(fname,header_name,value_name,delimiter=','):
    table_dict={}
    file=open(fname, 'r')
    csv_input = csv.reader(file,delimiter=delimiter)
    index=0
    for row in csv_input:
        if index==0:
            header=row
            header_index=header.index(header_name)
            value_index=header.index(value_name)
        else:
            print(row[header_index])
            table_dict[row[header_index]]=float(row[value_index])
        index+=1
    return table_dict

def read_aggregate_table(fname,aggregate_header,aggregated_header,delimiter='|'):
    aggregate_table_dict={}
    file=open(fname, 'r')
    csv_input = csv.reader(file,delimiter=delimiter)
    index=0
    for row in csv_input:
        if index==0:
            header=row
            aggregate_index=header.index(aggregate_header)
            aggregated_index=header.index(aggregated_header)
        else:
            if row[aggregate_index] not in aggregate_table_dict.keys():
                aggregate_table_dict[row[aggregate_index]]=[row[aggregated_index]]
            else:
                aggregate_table_dict[row[aggregate_index]].append(row[aggregated_index])
        index+=1
    return aggregate_table_dict

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
        emission_ref=methane_debt[country].values[0]
    elif rule=='GDP':
        emission_ref=methane_debt[country].values[0]
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
        #import pdb;pdb.set_trace()
        output_df=(input_df.values-emission_ref)*(GWP100_CH4*100.)/40.
    return output_df
