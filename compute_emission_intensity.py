#! /bin/python

import pandas as pd
import numpy as np
from copy import deepcopy

scenarios_df=pd.read_csv('ipcc1p5_scenarios.csv',delimiter=',')

#CH4_intensity_list=[np.nan]*len(scenarios_df[(scenarios_df['Variable']=='Emissions|CH4|AFOLU')].values)
#CH4_intensity_df=pd.DataFrame(CH4_intensity_list,columns=['Intensity'])

#Add missing rows
scenarios_df['good_scenario']=scenarios_df['Scenario']=='Remi'
for (model,scenario) in zip(scenarios_df['Model'].values,scenarios_df['Scenario'].values):
    variable_list=scenarios_df[(scenarios_df['Scenario']==scenario) & (scenarios_df['Model']==model)]['Variable'].values
    if ('Agricultural Demand' not in variable_list) & ('Agricultural Demand|Crops' in variable_list) & ('Emissions|CH4|AFOLU' in variable_list):
        agricultural_demand=scenarios_df[(scenarios_df['Scenario']==scenario) & (scenarios_df['Model']==model) & (scenarios_df['Variable']=='Agricultural Demand|Livestock')][scenarios_df.columns[5:-1]].values+scenarios_df[(scenarios_df['Scenario']==scenario) & (scenarios_df['Model']==model) & (scenarios_df['Variable']=='Agricultural Demand|Crops')][scenarios_df.columns[5:-1]].values
        row=[model,scenario,'World','Agricultural Demand','million t DM/yr']
        row.extend(np.ndarray.tolist(agricultural_demand)[0])
        row.append(True)
        scenarios_df.loc[len(scenarios_df)] = row
    elif ('Agricultural Demand' in variable_list) & ('Emissions|CH4|AFOLU' in variable_list):
        for index in scenarios_df[(scenarios_df['Scenario']==scenario) & (scenarios_df['Model']==model)]['good_scenario'].index:
            if scenarios_df.loc[index,'Variable']=='Agricultural Demand':
                scenarios_df.loc[index,'good_scenario']=True
    # elif ('Agricultural Demand' not in variable_list) & ('Agricultural Demand|Crops' not in variable_list) & ('Emissions|CH4|AFOLU' in variable_list) :
    #     row=[model,scenario,'World','Agricultural Demand','million t DM/yr']
    #     row.extend([np.nan]*len(scenarios_df.columns[5:105]))
    #     scenarios_df.loc[len(scenarios_df)] = row

CH4_intensity_df=deepcopy(scenarios_df[scenarios_df['good_scenario']])
CH4_index_df=deepcopy(scenarios_df[scenarios_df['good_scenario']])
production_df=deepcopy(scenarios_df[scenarios_df['good_scenario']])
CH4_df=pd.DataFrame(columns=scenarios_df.columns.values)
for index in list(CH4_intensity_df.index):
    model=CH4_intensity_df.loc[index,'Model']
    scenario=CH4_intensity_df.loc[index,'Scenario']
    index_emission=scenarios_df.index[(scenarios_df['Model'] == model) & (scenarios_df['Scenario'] == scenario) & (scenarios_df['Variable'] == 'Emissions|CH4|AFOLU')][0]
    CH4_intensity_df.loc[index,'Variable']='Intensity'
    CH4_index_df.loc[index,'Variable']='Index'
    CH4_intensity_df.loc[index,scenarios_df.columns[5:-1]]=scenarios_df.loc[index_emission,scenarios_df.columns[5:-1]].values/scenarios_df.loc[index,scenarios_df.columns[5:-1]].values
    CH4_index_df.loc[index,scenarios_df.columns[5:-1]]=scenarios_df.loc[index_emission,scenarios_df.columns[5:-1]].values/scenarios_df.loc[index_emission,scenarios_df.columns[15]]
    production_df.loc[index,:]=scenarios_df.loc[index,:].values
    production_df.loc[index,'Variable']='Agricultural_Demand'
    CH4_df.loc[index_emission,:]=scenarios_df.loc[index_emission,:].values
    CH4_df.loc[index_emission,'Variable']='CH4'

import matplotlib.pyplot as plt

color_list=[20,40]
label_list=['2010','2050']
colors = {'2010':'red', '2050':'blue'}
fig, ax = plt.subplots()
ax.scatter(production_df[label_list[0]],CH4_index_df[label_list[0]],c=colors[label_list[0]],label=label_list[0])
ax.scatter(production_df[label_list[1]],CH4_index_df[label_list[1]],c=colors[label_list[1]],label=label_list[1])
plt.show()
