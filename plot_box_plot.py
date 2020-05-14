#! /bin/python

'''
PLot boxplot of national AFOLU balance following the national methane quota
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy
import matplotlib.cm as cm
import seaborn as sns
import argparse
from common_data import read_FAOSTAT_df
from common_methane import compute_CO2_equivalent

parser = argparse.ArgumentParser('Box plot of methane quotas,production, areas, emissions...')
parser.add_argument('--sensitivity-analysis', help='Yields can be +50 or -50')

args = parser.parse_args()

if args.sensitivity_analysis is not None:
    yield_change=float(args.sensitivity_analysis)/100.
    file_name_suffix='_yield'+args.sensitivity_analysis
else:
    yield_change=0
    file_name_suffix=''

cmap = cm.ScalarMappable(cmap='rainbow')
rumi_dict={"cattle":"cattle","smallrum":"Sheep and Goats"}
country_list=["Brazil","France","India","Ireland"]
grassland_list=["Land under temp. meadows and pastures","Land with temporary fallow","Land under perm. meadows and pastures"]
item_dict={"cattle":"Cattle","Sheep and Goats":"Sheep and Goats"}
climatic_region={"Tropical":["India","Brazil"],"Temperate":["Ireland","France"]}
carbon_growth_rate={"Tropical":4.86*48./12.,"Temperate":2.8*48./12.}
ha_2_Mha=1E-6
kha_2_Mha=1E-3
t_2_Mt=1E-6
t_2_kt=1E-3
kt_2_Mt=1E-3
t_to_Mt=1E-6
t_to_kt=1E-3
GWP100_CH4=34. #GWP100 for methane in last IPCC method

ponderation_dict={}
ponderation_dict['Population']=pd.read_csv('data/WB_population_reference.csv',delimiter=',')
ponderation_dict['GDP']=pd.read_csv('data/WB_GDP_reference.csv',delimiter=',')
ponderation_dict['Grand-fathering']=None
ponderation_dict['Debt']=pd.read_csv('output/FAOSTAT_methane_debt.csv',delimiter=',')
ponderation_dict['Protein']=pd.read_csv('output/FAOSTAT_protein_production.csv',delimiter=',')
methane_emissions_pd=read_FAOSTAT_df('data/FAOSTAT_methane.csv')
for country in country_list:
    methane_emissions_pd.loc[methane_emissions_pd['Area']==country,'Value']=methane_emissions_pd.loc[methane_emissions_pd['Area']==country,'Value'].values[0]

sns.set(font_scale=1.5)
sns.set_style("whitegrid")

#Load impacts for different scenarios
activity_df=pd.read_csv("output/impact_2050"+file_name_suffix+".csv")
#Change name of rice for esthetic in graph
activity_df=activity_df.rename(columns = {'Production Rice, paddy':'Rice'})
activity_df=activity_df.rename(columns = {'Production Rice, paddy 2010':'Rice 2010'})
for country in country_list:
    activity_df.loc[activity_df['Country']==country,'National methane 2010']=methane_emissions_pd.loc[methane_emissions_pd['Area']==country,'Value'].values[0]

activity_df.loc[:,'National methane index']=activity_df.loc[:,'National quota']/activity_df.loc[:,'National methane 2010']
activity_df.loc[activity_df['National methane 2010']==0,'National methane index']=0

#Read methane Debt
methane_debt_df=pd.read_csv("output/FAOSTAT_methane_debt_value.csv")

#Print methane quota
df_to_plot=activity_df.loc[:,['Country','Pathways',"National methane 2010","National methane index","National quota","Allocation rule"]]
df_to_plot.loc[:,"Methane 2010 (ktCH4)"]=df_to_plot.loc[:,"National methane 2010"].values*t_to_Mt
df_to_plot.loc[:,"Methane 2050 (ktCH4)"]=df_to_plot.loc[:,"National quota"].values*t_to_Mt
df_to_plot=df_to_plot.rename(columns = {'National methane index':'Methane index'})
g = sns.catplot(x="Country", y="Methane index", hue="Allocation rule",
                height=3.5, aspect=1.5,
                kind="point", legend=False, data=df_to_plot,join=False);
g.add_legend(title="Allocation rule")
g.set_axis_labels("", "Methane index\n(in 2050 relative to 2010)")
#plt.show()+
#g.set(yticklabels=["Thursday", "Friday", "Saturday", "Sunday"])
#g.despine(trim=True)
g.fig.set_size_inches(6.5, 3.5)
g.fig.savefig('Figs/methane_quota_bar_plot_test.png', dpi=100)
table = pd.pivot_table(df_to_plot, values=['Methane 2010 (ktCH4)','Methane 2050 (ktCH4)'], index=['Country'],columns=["Allocation rule"],aggfunc=np.mean)
table.index.name=None
table.to_excel("output/table_methane_quotas.xlsx",index_label=None,float_format = "%0.1f")
print("Print methane quota with different metrics...")

#Print production indicators for different quota
# Livestock production
production_list=['Milk','Meat','Eggs','Rice']
df_with_all_prod_to_plot=pd.DataFrame(columns=['Production index','Allocation rule','Production in 2010 (Mt)','Production','Country','Item'])
for production in production_list:
    activity_df[production+' index']=activity_df[production]/activity_df[production+' 2010']
    activity_df.loc[activity_df[production+' 2010']==0,production+' index']=0
#    df_to_plot=activity_df.loc[:,['Country',production,"Allocation rule"]].pivot(columns="Country")
#    df_to_plot=pd.concat([df_to_plot[production],activity_df["Allocation rule"]],axis=1)
#    plot_boxplot(df_to_plot,country_list,"Production","Figs/production_"+production.lower().replace(" ","_")+"_bar_plot_countries.png")
#    plot_boxplot(df_to_plot,country_list,"Production","Figs/production_"+production.lower().replace(" ","_")+"_bar_plot_countries.pdf")
#    print("Print production with different metrics...")
    df_to_concat=pd.concat([activity_df[['Country','Pathways',production+' 2010',production+' index',production,"Allocation rule"]],pd.DataFrame([production]*len(activity_df['Country']),columns=['Item'])],axis=1,sort=True)
    df_to_concat=df_to_concat.rename(columns = {production+' index':'Production index (relative to 2010)'})
    df_to_concat=df_to_concat.rename(columns = {production+' 2010':'Production in 2010 (Mt)'})
    df_to_concat=df_to_concat.rename(columns = {production:'Production'})
    df_with_all_prod_to_plot=pd.concat([df_with_all_prod_to_plot,df_to_concat],axis=0,sort=True)

df_with_all_prod_to_plot.loc[df_with_all_prod_to_plot['Country']!=df_with_all_prod_to_plot['Pathways'],'Pathway']='Improved'
df_with_all_prod_to_plot.loc[df_with_all_prod_to_plot['Country']==df_with_all_prod_to_plot['Pathways'],'Pathway']='Current'
df_with_all_prod_to_plot['Production in 2010 (Mt)']=df_with_all_prod_to_plot['Production in 2010 (Mt)']*t_to_Mt
df_with_all_prod_to_plot['Production in 2050 (Mt)']=df_with_all_prod_to_plot['Production']*t_to_Mt
df_with_all_prod_to_plot=df_with_all_prod_to_plot.reset_index()
g = sns.catplot(x="Item", y="Production index (relative to 2010)", hue="Allocation rule",col="Country",
                height=3.5, aspect=1.5,sharey=True,col_wrap=2,
                kind="point", data=df_with_all_prod_to_plot,join=False)
g.add_legend(title="Allocation rule")
g.set_axis_labels("", "Production index\n(in 2050 relative to 2010)")
g.set_titles("{col_name}")
g.fig.savefig('Figs/production_bar_plot.png', dpi=100)
plt.close("all")
#plot_boxplot_with_sns(df_with_all_prod_to_plot,country,"Production index (relative to 2010)","Allocation rule","Production index (relative to 2010)",'Figs/production_bar_plot_'+country.lower().replace(' ','_')+file_name_suffix+'.png',item_column_name='Item',ref_column_name='Production in 2010 (Mt)',reference_df=None,plot_points=True)
table = pd.pivot_table(df_with_all_prod_to_plot, values=['Production in 2010 (Mt)','Production in 2050 (Mt)'], index=['Country','Item'],columns=["Allocation rule"],aggfunc=np.mean)
table.index.name=None
table.to_excel("output/table_production.xlsx",index_label=None,float_format = "%0.1f")
print("Print all production with different metrics...")

#Print unit of production of each methane intensive production
item_list=['Cattle, dairy','Cattle, non-dairy','Swine','Poultry Birds','Chickens, layers','Sheep and Goats'] #'Rice, paddy'
df_with_all_prod_to_plot=pd.DataFrame(columns=['UP','UP index','Allocation rule','UP 2010','Country','Item'])
for item in item_list:
    activity_df['UP index '+item]=activity_df['UP '+item].values/activity_df['UP 2010 '+item].values
    df_to_concat=pd.concat([activity_df[['Country','Pathways','UP 2010 '+item,'UP index '+item,'UP '+item,"Allocation rule"]],pd.DataFrame([item]*len(activity_df['Country']),columns=['Item'])],axis=1,sort=True)
    df_to_concat=df_to_concat.rename(columns = {'UP 2010 '+item:'UP 2010'})
    df_to_concat=df_to_concat.rename(columns = {'UP '+item:'UP'})
    df_to_concat=df_to_concat.rename(columns = {'UP index '+item:'UP index'})
    df_with_all_prod_to_plot=pd.concat([df_with_all_prod_to_plot,df_to_concat],axis=0,sort=True)
table = pd.pivot_table(df_with_all_prod_to_plot, values=['UP 2010','UP','UP index'], index=['Country','Item'],columns=["Allocation rule"],aggfunc=np.mean)
table.index.name=None
table.to_excel("output/table_UP.xlsx",index_label=None,float_format = "%0.2f")
print("Print all UP index with different metrics...")

#Print area change for different quota
df_to_plot=pd.DataFrame(columns=['Area index','Allocation rule','Area 2010','Area 2050','Country','Item'])
for item in ['Grass','Feed','Rice','Total']:
    df_to_concat=pd.concat([activity_df[['Country','National '+item+' area index','National '+item+' area 2010','National '+item+' area',"Allocation rule"]],pd.DataFrame([item]*len(activity_df['Country']),columns=['Item'])],axis=1,sort=True)
    df_to_concat=df_to_concat.rename(columns = {'National '+item+' area index':'Area index'})
    df_to_concat=df_to_concat.rename(columns = {'National '+item+' area 2010':'Area 2010'})
    df_to_concat=df_to_concat.rename(columns = {'National '+item+' area':'Area 2050'})
    df_to_plot=pd.concat([df_to_plot,df_to_concat],axis=0,sort='True')

ha_2_Mha=1E-6
df_to_plot['Area in 2050 (Mha)']=df_to_plot['Area 2050']*ha_2_Mha
df_to_plot['Area in 2010 (Mha)']=df_to_plot['Area 2010']*ha_2_Mha
g = sns.catplot(x="Item", y="Area index", hue="Allocation rule",col="Country",
                height=3.5, aspect=1.5,sharey=True,legend=False,
                kind="point", data=df_to_plot,join=False)
g.set_axis_labels("", "Area index\n(2050 relative to 2010)")
g.set_titles("{col_name}")
g.add_legend(title="Allocation rule")
g.fig.savefig('Figs/area_bar_plot.png', dpi=100)
plt.close("all")
table = pd.pivot_table(df_to_plot, values=['Area in 2010 (Mha)','Area in 2050 (Mha)'], index=['Country','Item'],columns=["Allocation rule"],aggfunc=np.mean)
table.index.name=None
table.to_excel("output/table_area.xlsx",index_label=None,float_format = "%0.1f")
print("Print all area index with different metrics...")

#Compute N2O emissions from manure
df_to_plot=pd.DataFrame(columns=['N2O emissions','Allocation rule','Country','Item'])
for item in ['manure','fert']:
    df_to_concat=pd.concat([activity_df[['Country','N2O '+item+' index', 'N2O '+item+' 2010','N2O '+item,"Allocation rule"]],pd.DataFrame([item]*len(activity_df['Country']),columns=['Item'])],axis=1,sort=True)
    df_to_concat=df_to_concat.rename(columns = {'N2O '+item+' 2010':'N2O emissions in 2010'})
    df_to_concat=df_to_concat.rename(columns = {'N2O '+item+' index':'N2O index (2050 relative to 2010)'})
    df_to_concat=df_to_concat.rename(columns = {'N2O '+item:'N2O emissions in 2050'})
    df_to_plot=pd.concat([df_to_plot,df_to_concat],axis=0,sort='True')

df_to_plot['N2O emissions\nin 2010 (ktN2O)']=df_to_plot['N2O emissions in 2010']*t_to_kt
df_to_plot['N2O emissions\nin 2050 (ktN2O)']=df_to_plot['N2O emissions in 2050']*t_to_kt
g = sns.catplot(x="Item", y="N2O index (2050 relative to 2010)", hue="Allocation rule",col="Country",
                height=3.5, aspect=1.5,sharey=True,
                kind="point", data=df_to_plot,join=False)
g.add_legend(title="Allocation rule")
g.set_axis_labels("", "N2O index\n(2050 relative to 2010)")
g.set_titles("{col_name}")
g.fig.savefig('Figs/N2O_bar_plot.png', dpi=100)
plt.close("all")
table = pd.pivot_table(df_to_plot, values=['N2O emissions\nin 2010 (ktN2O)','N2O emissions\nin 2050 (ktN2O)'], index=['Country','Item'],columns=["Allocation rule"],aggfunc=np.mean)
table.index.name=None
table.to_excel("output/table_N2O.xlsx",index_label=None,float_format = "%0.1f")
print("Print N2O with different metrics...")

#Compute negative emissions of CO2
df_to_plot=pd.DataFrame(columns=['CO2 offset','Allocation rule','Country','Item'])
for item in ['Grass','Feed','Rice','Total']:
    df_to_concat=pd.concat([activity_df[['Country','Pathways',item+' offset',"Allocation rule"]],pd.DataFrame([item]*len(activity_df['Country']),columns=['Item'])],axis=1,sort=True)
    df_to_concat=df_to_concat.rename(columns = {item+' offset':'CO2 offset'})
    df_to_plot=pd.concat([df_to_plot,df_to_concat],axis=0,sort='True')

df_to_plot['CO2 offset (MtCO2)']=df_to_plot['CO2 offset']*t_to_Mt
g = sns.catplot(x="Item", y="CO2 offset (MtCO2)", hue="Allocation rule",col="Country",
                height=3.5, aspect=1.5,sharey=False,
                kind="point", legend=False, data=df_to_plot,join=False);
g.add_legend(title="Allocation rule")
g.set_axis_labels("", "CO2 offset (MtCO2)")
g.set_titles("{col_name}")
g.fig.savefig('Figs/CO2_bar_plot.png', dpi=100)
table = pd.pivot_table(df_to_plot, values=['CO2 offset (MtCO2)'], index=['Country','Item'],columns=["Allocation rule"],aggfunc=np.mean)
table.index.name=None
table.to_excel("output/table_CO2.xlsx",index_label=None,float_format = "%0.1f")
print("Print CO2 offset with different metrics...")

#Compute AFOLU balance
GWP100_N2O=298
activity_df['CO2 offset world']=(activity_df['2050']-activity_df['2010'])
df_to_plot=pd.DataFrame(columns=['GWP (MtCO2eq)','Allocation rule','Country','Item'])
for country in country_list:
    emission_ref_year=methane_emissions_pd['Value'][methane_emissions_pd['Area']==country].values[0]
    for rule in np.unique(activity_df['Allocation rule']):
        country_rule_mask=(activity_df['Allocation rule']==rule) & (activity_df["Country"]==country)
        N2O_emissions=activity_df.loc[country_rule_mask,'N2O']*t_2_Mt*GWP100_N2O
        CO2_equivalent=compute_CO2_equivalent(activity_df.loc[country_rule_mask,'National quota'],rule,emission_ref_year,country,ponderation_in_GWP_star=ponderation_dict[rule],methane_debt=methane_debt_df)
        methane_emissions_pd['Value'][methane_emissions_pd['Area']==country].values[0]
        for gaz in ["CO2","CH4","N2O","AFOLU"]:
            df_tmp=pd.DataFrame(columns=['GWP (MtCO2eq)','Allocation rule','Country'])
            if gaz=="CO2":
                df_tmp.loc[:,'GWP (MtCO2eq)']=-activity_df.loc[country_rule_mask,"Total offset"].values*t_to_Mt
            elif gaz=="CH4":
                df_tmp.loc[:,'GWP (MtCO2eq)']=CO2_equivalent*t_to_Mt
            elif gaz=="N2O":
                df_tmp.loc[:,'GWP (MtCO2eq)']=N2O_emissions.values
            elif gaz=="AFOLU":
                df_tmp.loc[:,'GWP (MtCO2eq)']=-activity_df.loc[country_rule_mask,"Total offset"].values*t_to_Mt+CO2_equivalent*t_to_Mt+N2O_emissions.values
            df_tmp['Country']=country
            df_tmp['Allocation rule']=rule
            df_to_concat=pd.concat([df_tmp[['Country','GWP (MtCO2eq)',"Allocation rule"]],pd.DataFrame([gaz]*len(df_tmp['Country']),columns=['Item'])],axis=1,sort=True)
            #df_to_concat=df_to_concat.rename(columns = {"GWP "+gaz+' (MtCO2eq)':'GWP (MtCO2eq)'})
            df_to_plot=pd.concat([df_to_plot,df_to_concat],axis=0,sort=False)
        df_tmp=pd.DataFrame(columns=['GWP (MtCO2eq)','Allocation rule','Country',"Item"])
        df_tmp["GWP (MtCO2eq)"]=activity_df.loc[country_rule_mask,'International Feed offset'].values*t_2_Mt
        df_tmp["Country"]=country
        df_tmp["Allocation rule"]=rule
        df_tmp["Item"]="Import"
        df_to_plot=pd.concat([df_to_plot,df_tmp],axis=0,sort=False)

g = sns.catplot(x="Item", y="GWP (MtCO2eq)", hue="Allocation rule",col="Country",
                height=3.5, aspect=1.5,sharey=False,col_wrap=2,
                kind="point", legend=False, data=df_to_plot,join=False);
g.add_legend(title="Allocation rule")
g.set_axis_labels("", "GWP (MtCO2eq)")
g.set_titles("{col_name}")
g.fig.savefig('Figs/AFOLU_bar_plot.png', dpi=100)
table = pd.pivot_table(df_to_plot, values=['GWP (MtCO2eq)'], index=['Country','Item'],columns=["Allocation rule"],aggfunc=np.mean)
table.index.name=None
table.to_excel("output/table_GWP.xlsx",index_label=None,float_format = "%0.1f")
#plot_boxplot(df_to_plot,country_list,"AFOLU balance(MtCO2eq)","Figs/AFOLU_balance_bar_plot_countries"+file_name_suffix+".png")
#plot_boxplot(df_to_plot,country_list,"Net AFOLU balance (MtCH4)","Figs/CH4_net_bar_plot_countries.pdf")
print("Print net AFOLU balance with different metrics...")
