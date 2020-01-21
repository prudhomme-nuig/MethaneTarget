#! /bin/python

import pandas as pd
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.cm as cm

#Select only 1.5 degres scenarios with low overshoot or below 1.5
methane_df=pd.read_csv('output/methane_1p5_low_overshoot.csv',delimiter=',')
methane_df=methane_df.drop(columns=list(methane_df.columns.values[16:25]))
methane_df=methane_df.drop(columns=list(methane_df.columns.values[5:15]))

#Select only 1.5 degres scenarios with low overshoot or below 1.5
production_df=pd.read_csv('output/production_1p5_low_overshoot.csv',delimiter=',')
production_df=production_df.drop(columns=list(production_df.columns.values[16:25]))
production_df=production_df.drop(columns=list(production_df.columns.values[5:15]))

#Add production in methane_df
methane_df['Production']=np.nan
for (model,scenario,index) in zip(methane_df['Model'].values,methane_df['Scenario'].values,methane_df.index.values):
    if (model in production_df['Model'].values) & (scenario in production_df['Scenario'].values):
        methane_df.loc[index,'Production']=production_df.loc[(production_df['Model']==model) & (production_df['Scenario']==scenario),'2050'].values[0]

#Select scenario with are in the confidence intervall 95%
mean = methane_df['2050'].mean()
p025 = methane_df['2050'].quantile(0.025)
p075 = methane_df['2050'].quantile(0.975)
methane_df['good_scenario']=methane_df['good_scenario']=='Remi'
methane_df.loc[(methane_df['2050']>p025) & (methane_df['2050']<p075),'good_scenario']=True
CH4_df=methane_df[methane_df['good_scenario']==True]

#Methane emissions per country
methane_reference_df=pd.read_csv('data/FAOSTAT_methane_reference.csv',delimiter=',')
methane_reference_df.name='methane_reference_df'
population_reference_df=pd.read_csv('data/WB_population_reference.csv',delimiter=',')
population_reference_df.name='population_reference_df'
GDP_reference_df=pd.read_csv('data/WB_GDP_reference.csv',delimiter=',')
GDP_reference_df.name='GDP_reference_df'

share_df=pd.DataFrame(columns=CH4_df.columns.values)
CH4_national_df=pd.DataFrame(columns=CH4_df.columns.values)
CH4_international_df=pd.DataFrame(columns=CH4_df.columns.values)
WB_df=['population_reference_df','GDP_reference_df']
for df in [population_reference_df,GDP_reference_df,methane_reference_df]:
    CH4_national_df_tmp=deepcopy(CH4_df)
    CH4_international_df_tmp=deepcopy(CH4_df)
    share_df_tmp=deepcopy(CH4_df)
    for index in list(CH4_df.index):
        if df.name in WB_df:
            share=df[df['Country Name']=='Ireland']['2010'].values[0]/df[df['Country Name']=='World']['2010'].values[0]
        else:
            share=df[df['Area']=='Ireland']['Value'].values[0]/df[df['Area']=='World']['Value'].values[0]
        share_df_tmp.loc[index,'2050']=share
        share_df_tmp.loc[index,'Variable']=df.name[:3]
        CH4_national_df_tmp.loc[index,'2050']=share*CH4_df.loc[index,'2050']
        CH4_national_df_tmp.loc[index,'Variable']=df.name[:3]

    CH4_national_df = pd.concat([CH4_national_df,CH4_national_df_tmp])
    CH4_international_df = pd.concat([CH4_international_df,CH4_international_df_tmp])
    share_df = pd.concat([share_df,share_df_tmp])

#Plot global,national methane emissions for 3 allocation rule
share_df.loc[share_df['Variable']=='met','Variable']='Grand-fathering'
share_df.loc[share_df['Variable']=='pop','Variable']='Population'
share_df.loc[share_df['Variable']=='gdp','Variable']='GDP'
plt.scatter(share_df['2050'],CH4_international_df['2050'],c=CH4_national_df['2050'], cmap=cm.viridis)
# plt.scatter(production_df[label_list[1]],CH4_index_df[label_list[1]],c=colors[label_list[1]],label=label_list[1])
plt.xlim([0, np.max(share_df['2050'])+np.max(share_df['2050'])/10])
plt.xticks(share_df['2050'], share_df['Variable'], size='small',rotation='vertical')
plt.colorbar(label='National CH4 in AFOLU (MtCH4/yr)')
plt.ylabel('Global CH4 in AFOLU (MtCH4/yr)')
plt.xlabel('Methane allocation method')
plt.savefig('Figs/methane_national_share_scenario.pdf',bbox_inches="tight")
plt.savefig('Figs/methane_national_share_scenario.png',bbox_inches="tight")
plt.close()

# CH4_net_national_df=pd.DataFrame(columns=CH4_national_df.columns.values)
# for offset_share in list(np.arange(0.01,1.01,0.01)):
#     CH4_net_national_df_tmp=deepcopy(CH4_national_df)
#     for index in list(CH4_national_df.index):
#         CH4_net_national_df_tmp.loc[index,'Variable']=offset_share
#     CH4_net_national_df=pd.concat([CH4_net_national_df,CH4_net_national_df_tmp])

# #Read results of goblin
# goblin_df=pd.read_csv('data/emissions_scenario.csv',delimiter=',')
#
# #Select best scenario in goblin which reach methane quota
# CH4_national_df.index=range(len(CH4_national_df.index.values))
# CH4_national_df['offset']=CH4_national_df['2050']
# CH4_national_df['net CH4']=CH4_national_df['2050']
# index_list=deepcopy(CH4_national_df.index)
# for index in index_list:
#     goblin_df['good_scenario']=goblin_df['CH4'].between(CH4_national_df.loc[index,'2050']*1000*0.995,CH4_national_df.loc[index,'2050']*1000*1.005)
#     print(index)
#     if len(goblin_df[goblin_df['good_scenario']]['Total emission'])>0:
#         CH4_national_df.loc[index,'offset']=-(goblin_df[goblin_df['good_scenario']]['Total emission'].values[0]/34-goblin_df[goblin_df['good_scenario']]['CH4'].values[0])
#         if len(goblin_df[goblin_df['good_scenario']]['Total emission'])>1:
#             for good_index in goblin_df[goblin_df['good_scenario']].index.values[1:]:
#                 CH4_national_df.loc[len(CH4_national_df),:]=CH4_national_df.loc[index,:]
#                 CH4_national_df.loc[len(CH4_national_df)-1,'offset']=-(goblin_df.loc[good_index,'Total emission']/34-goblin_df.loc[good_index,'CH4'])
#     else:
#         CH4_national_df.loc[index,'offset']=np.nan
#
# #Plot national methane depending on quota and offset potential
# plt.scatter(CH4_national_df['offset'],CH4_national_df['2050']*1000,c=CH4_national_df['2050']*1000+CH4_national_df['offset'], cmap=cm.viridis)
# plt.colorbar(label='Net national CH4 in AFOLU (MtCH4/yr)')
# plt.ylabel('National CH4 in AFOLU (MtCH4/yr)')
# plt.xlabel('Offset potential (MtCH4/yr)')
# plt.show()
# plt.savefig('Figs/methane_national_offset_quota.pdf',bbox_inches="tight")
# plt.savefig('Figs/methane_national_offset_quota.png',bbox_inches="tight")

#Read results of goblin
goblin_df=pd.read_csv('data/emissions_scenario.csv',delimiter=',')
area_df=pd.read_csv('data/area_scenario.csv',delimiter=',')

#Select best scenario in goblin which reach methane quota
CH4_national_df.index=range(len(CH4_national_df.index.values))
CH4_national_df['offset']=CH4_national_df['2050']
CH4_national_df['CO2']=CH4_national_df['2050']
CH4_national_df['Total']=CH4_national_df['2050']
index_list=deepcopy(CH4_national_df.index);index_to_drop=[]
goblin_df['net CH4']=np.maximum(goblin_df['CH4']-np.maximum(-(goblin_df['Total emission']/34-goblin_df['CH4']),0),0)
for index in index_list:
    goblin_df['good_scenario']=goblin_df['net CH4'].between(0,CH4_national_df.loc[index,'2050']*1000)
    print(index)
    if len(goblin_df[goblin_df['good_scenario']]['Total emission'])>0:
        CH4_national_df_tmp=pd.concat([CH4_national_df.loc[index,:]]*len(goblin_df[goblin_df['good_scenario']]['Total emission']),axis=1).T
        CH4_national_df_tmp.index=range(len(CH4_national_df_tmp))
        CH4_national_df_tmp.loc[:,'offset']=goblin_df[goblin_df['good_scenario']]['CH4'].values-CH4_national_df.loc[index,'2050']*1000
        CH4_national_df_tmp.loc[:,'CO2']=-(goblin_df[goblin_df['good_scenario']]['Total emission'].values/34-goblin_df[goblin_df['good_scenario']]['CH4'].values)
        CH4_national_df_tmp.loc[:,'Total']=goblin_df[goblin_df['good_scenario']]['Total emission'].values
        CH4_national_df_tmp.loc[:,'Area']=area_df[goblin_df['good_scenario']]['Area (Mha)'].values
        CH4_national_df=CH4_national_df.append(CH4_national_df_tmp)
        CH4_national_df.index=range(len(CH4_national_df.index.values))
        index_to_drop.append(index)
    else:
        CH4_national_df.loc[index,'offset']=np.nan

for index in index_to_drop:
    CH4_national_df=CH4_national_df.drop(index)

#Plot national methane depending on quota and offset potential
plt.scatter(CH4_national_df['offset'],CH4_national_df['2050']*1000,c=CH4_national_df['2050']*1000+CH4_national_df['offset'], cmap=cm.viridis)
plt.colorbar(label='Net national CH4 in AFOLU (ktCH4/yr)')
plt.ylabel('National quota of CH4 in AFOLU (ktCH4/yr)')
plt.xlabel('Offset potential (ktCH4/yr)')
#plt.savefig('Figs/methane_national_offset_quota.pdf',bbox_inches="tight",dpi=300)
plt.savefig('Figs/methane_national_offset_quota.png',bbox_inches="tight")
plt.close()

plt.scatter(CH4_national_df['offset'],CH4_national_df['2050']*1000,c=CH4_national_df['CO2'], cmap=cm.viridis,s=2)
plt.colorbar(label='CO2 and N2O in AFOLU (MtCO2e/yr)')
plt.ylabel('National quota of CH4 in AFOLU (ktCH4/yr)')
plt.xlabel('Offset potential (ktCH4/yr)')
#plt.savefig('Figs/CO2_national_offset_quota.pdf',bbox_inches="tight",dpi=300)
plt.savefig('Figs/CO2_national_offset_quota.png',bbox_inches="tight")
plt.close()

plt.scatter(CH4_national_df['offset'],CH4_national_df['2050']*1000,c=CH4_national_df['Total'], cmap=cm.viridis,s=1)
plt.colorbar(label='Emissions in AFOLU (MtCO2e/yr)')
plt.ylabel('National quota of CH4 in AFOLU (ktCH4/yr)')
plt.xlabel('Offset potential (ktCH4/yr)')
#plt.savefig('Figs/CO2_national_offset_quota.pdf',bbox_inches="tight",dpi=300)
plt.savefig('Figs/AFOLU_national_offset_quota.png',bbox_inches="tight")
plt.close()

plt.scatter(CH4_national_df['offset'],CH4_national_df['2050']*1000,c=CH4_national_df['Area'], cmap=cm.viridis,s=2)
plt.colorbar(label='Area used for mitigation (Mha)')
plt.ylabel('National quota of CH4 in AFOLU (ktCH4/yr)')
plt.xlabel('Offset potential (ktCH4/yr)')
#plt.savefig('Figs/CO2_national_offset_quota.pdf',bbox_inches="tight",dpi=300)
plt.savefig('Figs/area_national_offset_quota.png',bbox_inches="tight")
plt.close()
