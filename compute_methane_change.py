#! /bin/python

import pandas as pd
import numpy as np
from copy import deepcopy

#Select only 1.5 degres scenarios with low overshoot or below 1.5
scenarios_df=pd.read_csv('ipcc1p5_scenarios_low_overshoot.csv',delimiter=',')

scenarios_df['good_scenario']=scenarios_df['Scenario']=='Remi'
for (model,scenario) in zip(scenarios_df['Model'].values,scenarios_df['Scenario'].values):
    variable_list=scenarios_df[(scenarios_df['Scenario']==scenario) & (scenarios_df['Model']==model)]['Variable'].values
    if ('Emissions|CH4|AFOLU' in variable_list):
        for index in scenarios_df[(scenarios_df['Scenario']==scenario) & (scenarios_df['Model']==model)]['good_scenario'].index:
            if scenarios_df.loc[index,'Variable']=='Emissions|CH4|AFOLU':
                scenarios_df.loc[index,'good_scenario']=True

CH4_index_df=deepcopy(scenarios_df[scenarios_df['good_scenario']])
for index in list(CH4_index_df.index):
    model=CH4_index_df.loc[index,'Model']
    scenario=CH4_index_df.loc[index,'Scenario']
    index_emission=scenarios_df.index[(scenarios_df['Model'] == model) & (scenarios_df['Scenario'] == scenario) & (scenarios_df['Variable'] == 'Emissions|CH4|AFOLU')][0]
    CH4_index_df.loc[index,'Variable']='Index'
    CH4_index_df.loc[index,scenarios_df.columns[5:-1]]=scenarios_df.loc[index_emission,scenarios_df.columns[5:-1]].values/scenarios_df.loc[index_emission,scenarios_df.columns[7]]

CH4_index_df.to_csv(path_or_buf = 'output/methane_index_1p5_low_overshoot.csv',index=False)

import matplotlib.pyplot as plt

boxplot = CH4_index_df.boxplot(column=['2050', '2100'])
plt.ylabel('Methane emissions compared to 2010 level')
plt.xlabel('Years')
plt.show()
plt.savefig('Figs/methane_index_bar_plot.pdf')
plt.savefig('Figs/methane_index_bar_plot.png')
