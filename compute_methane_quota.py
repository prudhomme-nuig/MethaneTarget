#! /bin/python

'''
Compute national methane quota for different rules: methane debt, protein production, gdp, population
'''

import pandas as pd
import numpy as np
from copy import deepcopy
from common_data import read_FAOSTAT_df

#Country in this study
country_list=["Brazil","France","India","Ireland"]

#Select only 1.5 degres scenarios with low overshoot or below 1.5 and years 2010,2050 and 2100
methane_df=pd.read_csv('output/methane_1p5_low_overshoot.csv',delimiter=',')
methane_df=methane_df.drop(columns=list(methane_df.columns.values[16:26]))
methane_df=methane_df.drop(columns=list(methane_df.columns.values[8:15]))
methane_df=methane_df.drop(columns=list(methane_df.columns.values[5:7]))
methane_df=methane_df.drop(columns=list(methane_df.columns.values[2:4]))

# Convert Mt in t
methane_df['2010']=methane_df['2010']*1E6
methane_df['2050']=methane_df['2050']*1E6

#Select only 1.5 degres scenarios with low overshoot or below 1.5 and years 2010,2050 and 2100
production_df=pd.read_csv('output/production_1p5_low_overshoot.csv',delimiter=',')
production_df=production_df.drop(columns=list(production_df.columns.values[16:25]))
production_df=production_df.drop(columns=list(production_df.columns.values[8:15]))
production_df=production_df.drop(columns=list(production_df.columns.values[5:7]))

#Read global and national production computed from FAOSTAT
production_ref_df=pd.read_csv('output/production_2010.csv',delimiter=',',index_col=0)*0.9*1E-3 #conversion to DM and from 1E3t to 1E6t

#Read global and national biogenic methane emissions computed from FAOSTAT
methane_reference_df=read_FAOSTAT_df('data/FAOSTAT_methane_reference.csv',delimiter=',')

#Select scenario with are in the confidence intervall 95%
#methane_df['Production IPCC 2050']=np.nan
#methane_df['Production IPCC 2010']=np.nan
#methane_df['good_scenario']=False
#for (model,scenario) in zip(production_df.loc[production_df['Variable']=='Agricultural Production','Model'].values,production_df.loc[production_df['Variable']=='Agricultural Production','Scenario'].values):
#    methane_df.loc[(methane_df['Model']==model) & (methane_df['Scenario']==scenario),'Production IPCC 2050']=production_df.loc[(production_df['Model']==model) & (production_df['Scenario']==scenario) & (production_df['Variable']=='Agricultural Production'),'2050'].values[0]
#    methane_df.loc[(methane_df['Model']==model) & (methane_df['Scenario']==scenario),'Production IPCC 2010']=production_df.loc[(production_df['Model']==model) & (production_df['Scenario']==scenario) & (production_df['Variable']=='Agricultural Production'),'2010'].values[0]
#    methane_df.loc[(methane_df['Model']==model) & (methane_df['Scenario']==scenario),'good_scenario']=True
#methane_df=deepcopy(methane_df[methane_df['good_scenario']])

#Add production in methane_df
#methane_df.loc[:,'Production']=np.nan
country_and_world_list=deepcopy(country_list)
country_and_world_list.append('World')
for country in ['World']:
    #methane_df.loc[:,country+' Production FAO 2010']=np.nan
    methane_df.loc[:,country+' Emission FAO 2010']=np.nan
for index in methane_df.index.values:
    for country in ['World']:
        #methane_df.loc[index,country+' Production FAO 2010']=production_ref_df.loc[country,'2010']/1000
        methane_df.loc[index,country+' Emission FAO 2010']=methane_reference_df.loc[methane_reference_df['Area']==country,'Value'].values[0]

#Fix global methane emissions in IPCC scenarios to the same baseline FAO
methane_df.loc[:,'2050']=methane_df.loc[:,'2050']*methane_df.loc[:,'World Emission FAO 2010']/methane_df.loc[:,'2010']
methane_df.loc[:,'2010']=methane_df.loc[:,'World Emission FAO 2010']

#Load data for allocation rules
methane_debt_df=pd.read_csv('output/FAOSTAT_methane_debt.csv',delimiter=',')
methane_debt_df.name='debt_methane_df'
protein_production_df=pd.read_csv('output/FAOSTAT_protein_production.csv',delimiter=',')
protein_production_df.name='protein_production_df'
population_reference_df=pd.read_csv('data/WB_population_reference.csv',delimiter=',')
population_reference_df.name='population_reference_df'
GDP_reference_df=pd.read_csv('data/WB_GDP_reference.csv',delimiter=',')
GDP_reference_df.name='GDP_reference_df'

methane_df.loc[:,'Share']=np.nan
methane_df.loc[:,'Allocation rule']=np.nan
methane_df.loc[:,'National quota']=np.nan
methane_df.loc[:,'Country']=np.nan
methane_tmp_df=pd.DataFrame(columns=methane_df.columns.values)
WB_df=['population_reference_df','GDP_reference_df']
index_list=deepcopy(list(methane_df.index))
index_new=0
for country in country_list:
    for index in index_list:
        for df in [population_reference_df,GDP_reference_df,methane_debt_df,protein_production_df]:
            methane_tmp_df.loc[index_new,:]=deepcopy(methane_df.loc[index,:])
            if df.name=="population_reference_df":
                methane_tmp_df.loc[index_new,'Share']=df.loc[df['Country Name']==country,'2010'].values[0]/df.loc[df['Country Name']=='World','2010'].values[0]
            elif df.name=="GDP_reference_df":
                methane_tmp_df.loc[index_new,'Share']=df.loc[df['Country Name']==country,'2010'].values[0]/df.loc[df['Country Name']=='World','2010'].values[0]
            elif df.name=="debt_methane_df":
                methane_tmp_df.loc[index_new,'Share']=df.loc[0,country]
            elif df.name:
                methane_tmp_df.loc[index_new,'Share']=df.loc[0,country]
            else:
                methane_tmp_df.loc[index_new,'Share']=df.loc[df['Area']==country,'Value'].values[0]/df.loc[df['Area']=='World','Value'].values[0]
            methane_tmp_df.loc[index_new,'Allocation rule']=df.name[:3]
            if (df.name=="population_reference_df") | (df.name=="protein_production_df"):
                methane_tmp_df.loc[index_new,'National quota']=methane_tmp_df.loc[index_new,'Share']*methane_tmp_df.loc[index_new,'2050']
            else:
                methane_tmp_df.loc[index_new,'National quota']=np.maximum(methane_tmp_df.loc[index_new,'Share']*(methane_tmp_df.loc[index_new,'2050']-methane_tmp_df.loc[index_new,'2010'])+methane_reference_df.loc[methane_reference_df['Area']==country,'Value'].values[0],1E-6)
            methane_tmp_df.loc[index_new,'Country']=country
            index_new+=1

methane_df=deepcopy(methane_tmp_df)
#Plot global,national methane emissions for 3 allocation rule
methane_df.loc[methane_df['Allocation rule']=='deb','Allocation rule']='Debt'
methane_df.loc[methane_df['Allocation rule']=='pro','Allocation rule']='Protein'
methane_df.loc[methane_df['Allocation rule']=='met','Allocation rule']='Grand-parenting'
methane_df.loc[methane_df['Allocation rule']=='pop','Allocation rule']='Population'
methane_df.loc[methane_df['Allocation rule']=='gdp','Allocation rule']='GDP'

rule_list=['Debt','Population','GDP','Protein']

methane_df.to_csv('output/methane_quota.csv',index=False)
