#! /bin/python

import pandas as pd
import numpy as np
from copy import deepcopy

#Select only 1.5 degres scenarios with low overshoot or below 1.5
scenarios_df=pd.read_csv('data/ipcc1p5_scenarios_low_overshoot.csv',delimiter=',')

def select_scenario(input_df,variable):
    output_df=deepcopy(input_df)
    output_df['good_scenario']=output_df['Scenario']=='Remi'
    for (model,scenario) in zip(output_df['Model'].values,output_df['Scenario'].values):
        variable_list=output_df[(output_df['Scenario']==scenario) & (output_df['Model']==model)]['Variable'].values
        if ('Emissions|CH4|AFOLU' in variable_list):
            for index in output_df[(output_df['Scenario']==scenario) & (output_df['Model']==model)]['good_scenario'].index:
                if output_df.loc[index,'Variable']==variable:
                    output_df.loc[index,'good_scenario']=True
    return output_df

emissions_df=select_scenario(scenarios_df,'Emissions|CH4|AFOLU')
production_df=select_scenario(scenarios_df,'Agricultural Production')
population_df=select_scenario(scenarios_df,'Population')

CH4_index_df=deepcopy(emissions_df[emissions_df['good_scenario']])
production_index_df=deepcopy(production_df[production_df['good_scenario']])
CH4_df=deepcopy(emissions_df[emissions_df['good_scenario']])
for index in list(CH4_index_df.index):
    model=CH4_index_df.loc[index,'Model']
    scenario=CH4_index_df.loc[index,'Scenario']
    index_emission=emissions_df.index[(emissions_df['Model'] == model) & (emissions_df['Scenario'] == scenario) & (emissions_df['Variable'] == 'Emissions|CH4|AFOLU')][0]
    CH4_index_df.loc[index,'Variable']='Index'
    CH4_index_df.loc[index,emissions_df.columns[5:-1]]=emissions_df.loc[index_emission,emissions_df.columns[5:-1]].values/emissions_df.loc[index_emission,emissions_df.columns[7]]

CH4_intensity_df=deepcopy(production_index_df[production_index_df['good_scenario']])
for index in list(production_index_df.index):
    model=production_index_df.loc[index,'Model']
    scenario=production_index_df.loc[index,'Scenario']
    index_production=emissions_df.index[(emissions_df['Model'] == model) & (emissions_df['Scenario'] == scenario) & (emissions_df['Variable'] == 'Agricultural Production')][0]
    index_emission=emissions_df.index[(emissions_df['Model'] == model) & (emissions_df['Scenario'] == scenario) & (emissions_df['Variable'] == 'Emissions|CH4|AFOLU')][0]
    production_index_df.loc[index,'Variable']='Index'
    production_index_df.loc[index,emissions_df.columns[5:-1]]=emissions_df.loc[index_production,emissions_df.columns[5:-1]].values/emissions_df.loc[index_production,emissions_df.columns[7]]
    CH4_intensity_df.loc[index,'Variable']='Index'
    CH4_intensity_df.loc[index,emissions_df.columns[5:-1]]=CH4_index_df.loc[index_emission,emissions_df.columns[5:-1]].values/production_index_df.loc[index_production,emissions_df.columns[5:-1]]


CH4_index_df.to_csv(path_or_buf = 'output/methane_index_1p5_low_overshoot.csv',index=False)
CH4_df.to_csv(path_or_buf = 'output/methane_1p5_low_overshoot.csv',index=False)
production_df.to_csv(path_or_buf = 'output/production_1p5_low_overshoot.csv',index=False)
production_index_df.to_csv(path_or_buf = 'output/production_index_1p5_low_overshoot.csv',index=False)
CH4_intensity_df.to_csv(path_or_buf = 'output/intensity_index_1p5_low_overshoot.csv',index=False)
population_df.to_csv(path_or_buf = 'output/population_1p5_low_overshoot.csv',index=False)

import matplotlib.pyplot as plt

boxplot = CH4_index_df.boxplot(column=['2050', '2100'])
plt.ylabel('Methane emissions compared to 2010 level')
plt.xlabel('Years')
plt.savefig('Figs/methane_index_bar_plot.pdf')
plt.savefig('Figs/methane_index_bar_plot.png')
plt.close()

boxplot = production_index_df.boxplot(column=['2050', '2100'])
plt.ylabel('Production compared to 2010 level')
plt.xlabel('Years')
plt.savefig('Figs/production_index_bar_plot.pdf')
plt.savefig('Figs/production_index_bar_plot.png')
plt.close()

boxplot = CH4_intensity_df.boxplot(column=['2050', '2100'])
plt.ylabel('Methane emission intensity compared to 2010 level')
plt.xlabel('Years')
plt.savefig('Figs/intensity_index_bar_plot.pdf')
plt.savefig('Figs/intensity_index_bar_plot.png')
plt.close()
