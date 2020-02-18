#! /bin/python

import csv

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
