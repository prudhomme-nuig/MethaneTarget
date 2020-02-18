#! /bin/python

import pandas as pd
from copy import deepcopy
from common_methane import read_aggregate_table,read_FAO_file

aggregation_table=read_aggregate_table('data/FAOSTAT_production_aggregation_table.csv','Item Group','Item',delimiter=',')
#dry_coef=read_table('data/feed_dry_matter.csv','Item','Value',delimiter=',')

production_disaggregate_ref_dict=read_FAO_file('data/FAOSTAT_production_disaggregate_reference.csv','Ireland','Production',delimiter=',')

production_aggregate={}
country_list=["France","Ireland","Brazil","India"]
country_and_world_list=deepcopy(country_list)
country_and_world_list.append('World')
for country in country_and_world_list:
    production_aggregate[country]=0
    for item in aggregation_table['Grand Total']:
        if item in production_disaggregate_ref_dict['Ireland']['Production'].keys():
            production_aggregate[country]+=float(production_disaggregate_ref_dict[country]['Production'][item])
        else:
            print(item+' not produced in Ireland')

share_in_production={}
for country in country_and_world_list:
    production_tmp=0
    for item in ['Bovine Meat','Milk - Excluding Butter','Butter, Ghee','Cream']:
        production_tmp+=float(production_disaggregate_ref_dict[country]['Production'][item])
    share_in_production[country]=production_tmp/production_aggregate[country]

production_aggregate_df=pd.DataFrame(data=[production_aggregate[key] for key in production_aggregate.keys()],columns=['2010'],index=production_aggregate.keys())
share_df=pd.DataFrame(data=[share_in_production[key] for key in share_in_production.keys()],columns=['2010'],index=share_in_production.keys())

production_aggregate_df.to_csv(path_or_buf = 'output/production_2010.csv',index=True)
share_df.to_csv(path_or_buf = 'output/share_production_2010.csv',index=True)

# #Compute methane intensity
# methane_intensity_ref={}
# for country in ['World','Ireland']:
#     methane_intensity_ref[country]=methane_ref[country]/production_aggregate[country]
