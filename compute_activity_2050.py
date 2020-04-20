#!/usr/bin/env python

from copy import deepcopy
import numpy as np
import pandas as pd
from common_data import read_FAOSTAT_df

methane_quota_df=pd.read_csv("output/methane_quota.csv")

pathways_df={"Ireland":["Ireland","Temperate"],
            "France":["France","Temperate"],
            "India":["India","Tropical"],
            "Brazil":["Brazil","Tropical"]}

methane_intensity_df=pd.read_csv("output/emission_intensity_2050.csv")
methane_all_reference_df=read_FAOSTAT_df("data/FAOSTAT_methane_reference.csv")

country_list=["Ireland","France","India","Brazil"]

item_file_dict={'enteric':'enteric_fermentation','rice':'rice','manure':'manure_management'}
output_df=pd.DataFrame(columns=['Country','Model','Scenario','Allocation','Pathways','Intensity'])
index=0
rule_list=list(np.unique(methane_quota_df['Allocation rule'].values))
ruminant_list=['Cattle','Sheep and Goats']

#     for (model,scenario) in zip(methane_quota_df.loc[:,'Model'].values,methane_quota_df.loc[:,'Scenario'].values):
#         for rule in rule_list:
activity_2050=pd.DataFrame(columns=[]) #list(methane_quota_df.columns.values.extend(['Item quota','Item activity','Pathways','Item','Emission type']
for country in country_list:
    for pathways in pathways_df[country]:
        output_df=deepcopy(methane_quota_df.loc[methane_quota_df['Country']==country,:])
        for (emission_type,item) in zip(methane_intensity_df['Emission'],methane_intensity_df['Item']):
            if methane_intensity_df.loc[(methane_intensity_df['Country']==pathways) & (methane_intensity_df['Emission']==emission_type) & (methane_intensity_df['Item']==item),'Intensity'].values[0]==0.0:
                methane_intensity=methane_intensity_df.loc[(methane_intensity_df['Country']==country) & (methane_intensity_df['Emission']==emission_type) & (methane_intensity_df['Item']==item),'Intensity']
            else:
                methane_intensity=methane_intensity_df.loc[(methane_intensity_df['Country']==pathways) & (methane_intensity_df['Emission']==emission_type) & (methane_intensity_df['Item']==item),'Intensity']
            methane_reference_df=read_FAOSTAT_df("data/FAOSTAT_"+item_file_dict[emission_type]+".csv")
            item_share=methane_reference_df['Value'][(methane_reference_df['Area']==country) & (methane_reference_df['Item']==item) & (['Emissions (CH4)' in element for element in methane_reference_df['Element']])].values[0]/methane_all_reference_df['Value'][(methane_all_reference_df['Area']==country)].values[0]
            methane_quota=methane_quota_df.loc[methane_quota_df['Country']==country,'National quota'].values*item_share
            if methane_intensity.values[0]>0:
                output_df.loc[:,'Quota '+emission_type+' '+item]=methane_quota
                output_df.loc[:,'Activity '+emission_type+' '+item]=methane_quota/methane_intensity.values[0]
            else:
                output_df.loc[:,'Quota '+emission_type+' '+item]=0
                output_df.loc[:,'Activity '+emission_type+' '+item]=0
        output_df.loc[:,'Pathways']=pathways
        activity_2050=pd.concat([activity_2050,output_df])
        activity_2050.index=range(len(activity_2050))
activity_2050.to_csv("output/activity_2050.csv",index=False)
