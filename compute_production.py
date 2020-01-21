#! /bin/python

import pandas as pd
import numpy as np
from copy import deepcopy
import csv

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
                table_dict[row[country_index]]={row[element_index]:{row[item_index]:float(row[value_index])*dry_coef[row[item_index]]}}
            else:
                if row[element_index] not in table_dict[row[country_index]].keys():
                    table_dict[row[country_index]][row[element_index]]={row[item_index]:float(row[value_index])*dry_coef[row[item_index]]}
                else:
                    if row[item_index] not in table_dict[row[country_index]][row[element_index]]:
                        table_dict[row[country_index]][row[element_index]][row[item_index]]=float(row[value_index])*dry_coef[row[item_index]]
        index+=1
    return table_dict

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

aggregation_table=read_aggregate_table('data/FAOSTAT_production_aggregation_table.csv','Item Group','Item',delimiter=',')
dry_coef=read_table('data/feed_dry_matter.csv','Item','Value',delimiter=',')
methane_ref=read_table('data/FAOSTAT_methane_reference.csv','Area','Value',delimiter=',')

production_disaggregate_ref_dict=read_FAO_file('data/FAOSTAT_production_disaggregate_reference.csv','Ireland','Production',delimiter=',')

production_aggregate={}
for country in ['Ireland','World']:
    production_aggregate[country]=0
    for item in aggregation_table['Grand Total']:
        if item in production_disaggregate_ref_dict['Ireland']['Production'].keys():
            production_aggregate[country]+=float(production_disaggregate_ref_dict[country]['Production'][item])
        else:
            print(item+' not produced in Ireland')

pd.DataFrame.from_dict(data)

# #Compute methane intensity
# methane_intensity_ref={}
# for country in ['World','Ireland']:
#     methane_intensity_ref[country]=methane_ref[country]/production_aggregate[country]
