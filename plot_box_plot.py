#! /bin/python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy
import matplotlib.cm as cm
import seaborn as sns
import argparse

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
country_list=["Ireland","France","India","Brazil"]
rule_list=["Grand-fathering","Population","GDP"]
grassland_list=["Land under temp. meadows and pastures","Land with temporary fallow","Land under perm. meadows and pastures"]
item_dict={"cattle":"Cattle","Sheep and Goats":"Sheep and Goats"}
climatic_region={"Tropical":["India","Brazil"],"Temperate":["Ireland","France"]}
carbon_growth_rate={"Tropical":4.86*48./12.,"Temperate":2.8*48./12.}
ha_2_Mha=1E-6
kha_2_Mha=1E-3
t_2_Mt=1E-6
t_2_kt=1E-3
kt_2_Mt=1E-3

ponderation_dict={}
ponderation_dict['Population']=pd.read_csv('data/WB_population_reference.csv',delimiter=',')
ponderation_dict['GDP']=pd.read_csv('data/WB_GDP_reference.csv',delimiter=',')
ponderation_dict['Grand-fathering']=None
methane_emissions_pd=pd.read_csv('data/FAOSTAT_methane.csv')
for country in country_list:
    methane_emissions_pd.loc[methane_emissions_pd['Area']==country,'Value']=methane_emissions_pd.loc[methane_emissions_pd['Area']==country,'Value'].values[0]*t_2_kt

def plot_boxplot(df_to_plot,country_list,y_label,file_name,reference_df=None):
    fig, ax = plt.subplots(2, 2, figsize=(10, 5))
    df_to_plot.boxplot(country_list[0],by=["Allocation rule"], ax=ax[0][0],patch_artist=True)
    df_to_plot.boxplot(country_list[1],by=["Allocation rule"], ax=ax[0][1],patch_artist=True)
    df_to_plot.boxplot(country_list[2],by=["Allocation rule"], ax=ax[1][0],patch_artist=True)
    df_to_plot.boxplot(country_list[3],by=["Allocation rule"], ax=ax[1][1],patch_artist=True)
    ax[0][0].set_ylabel(y_label)
    ax[1][0].set_ylabel(y_label)
    if reference_df is not None:
        for rule in range(len(np.unique(df_to_plot["Allocation rule"]))):
            ax[0][0].scatter(rule,reference_df[reference_df['Area']==country_list[0]]['Value'].values[0], c='red')
            ax[0][1].scatter(rule,reference_df[reference_df['Area']==country_list[1]]['Value'].values[0], c='red')
            ax[1][0].scatter(rule,reference_df[reference_df['Area']==country_list[2]]['Value'].values[0], c='red')
            ax[1][1].scatter(rule,reference_df[reference_df['Area']==country_list[3]]['Value'].values[0], c='red')
    plt.tight_layout()
    plt.suptitle("")
    plt.savefig(file_name)
    plt.close()

def plot_boxplot_with_sns(df_to_plot,country,y_column_name,allocation_column_name,y_label,file_name,item_column_name=None,ref_column_name=None,reference_df=None,plot_points=False):
    if item_column_name==None:
        a4_dims = (11.7, 8.27)
        fig, axes = plt.subplots(len(country_list),1, figsize=a4_dims)
        for ax,country in zip(axes,country_list):
            df_to_plot.boxplot(country,by=["Allocation rule"], ax=ax,patch_artist=True)
        plt.savefig(file_name)
        plt.close()
    else:
        if plot_points:
            allocation_list=np.unique(df_to_plot['Allocation rule'])
            if ref_column_name!=None:
                fig, axes = plt.subplots(2, len(allocation_list), sharey='row',sharex='row',figsize=(11.7, 8.27),gridspec_kw = {'height_ratios':[1,4]})
                for (ax,rule) in zip(axes[0],allocation_list):
                    country_rule_mask=(df_to_plot['Country']==country) & (df_to_plot['Allocation rule']==rule)
                    sns.swarmplot(item_column_name, ref_column_name, data=df_to_plot[country_rule_mask],ax=ax,size=5)
                ax_to_plot=axes[1]
            else:
                fig, axes = plt.subplots(1, len(allocation_list), sharey='row',sharex='row',figsize=(11.7, 8.27))
                ax_to_plot=axes
            for (ax,rule) in zip (ax_to_plot,allocation_list):
                country_rule_mask=(df_to_plot['Country']==country) & (df_to_plot['Allocation rule']==rule)
                with sns.axes_style(style='ticks'):
                    sns.swarmplot(item_column_name, y_column_name,'Pathway', data=df_to_plot[country_rule_mask],ax=ax,size=3)
                    sns.catplot(item_column_name, y_column_name, data=df_to_plot[country_rule_mask], kind="box",height=8.27, aspect=11.7/8.27,ax=ax)
                    if rule!='GDP':
                        ax.get_legend().remove()
                        y_axis = ax.axes.get_yaxis()
                        y_axis.set_visible(False)
                        #ax.tick_params(axis = 'y', which = 'major', labelsize = 0.5)
                        ax.tick_params(axis = 'x', which = 'major', labelsize = 12)
                        ax.spines["top"].set_visible(False)
                        ax.spines["right"].set_visible(False)
                        ax.spines["left"].set_visible(False)
                        ax.set_xlabel(rule,fontsize='12')
                    else:
                        ax.set_ylabel(y_label,fontsize='12')
                        ax.set_xlabel(rule,fontsize='12')
                        ax.tick_params(axis = 'y', which = 'major', labelsize = 12)
                        ax.tick_params(axis = 'x', which = 'major', labelsize = 12)
                        ax.spines["top"].set_visible(False)
                        ax.spines["right"].set_visible(False)
 

                    #plt.xlabel(item_column_name,fontsize='22')
                    #plt.tight_layout()
                    plt.subplots_adjust(wspace =0.)
        else:
            fig, ax = plt.subplots()
            with sns.axes_style(style='ticks'):
                g = sns.catplot(allocation_column_name, y_column_name,item_column_name, data=df_to_plot[df_to_plot['Country']==country], legend=True, kind="box",height=8.27, aspect=11.7/8.27,ax=ax)
                g.set_axis_labels(allocation_column_name, y_label)
                g.set_xlabels(fontsize='22')
                g.set_ylabels(fontsize='22')
                g.set_xticklabels(fontsize='20')
                g.set_yticklabels(fontsize='20')
        fig.savefig(file_name)
        plt.close('all')

def compute_methane_equivalent(input_df,rule,emission_ref_year,country,ponderation_in_GWP_star=None):
    output_df=deepcopy(input_df)
    is_GWP100=False
    GWP100=34. #GWP100 for methane in last IPCC method
    Horizon=100.
    if rule=='Grand-fathering':
        emission_ref=emission_ref_year
    elif rule=='GDP':
        emission_ref=emission_ref_year*ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']==country]['2010'].values[0]/ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']=='World']['2010'].values[0]
    elif rule=='Population':
        emission_ref=emission_ref_year*ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']==country]['2010'].values[0]/ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']=='World']['2010'].values[0]
    elif rule=='GWP100':
        is_GWP100=True
    else:
        print('Unknown method. Code it!')
    if is_GWP100:
        output_df=input_df/GWP100
    else:
        output_df=input_df.values*40./(GWP100*Horizon)+emission_ref
    return output_df

def compute_CO2_equivalent(input_df,rule,emission_ref_year,country,ponderation_in_GWP_star=None):
    output_df=deepcopy(input_df)
    is_GWP100=False
    GWP100=34. #GWP100 for methane in last IPCC method
    Horizon=100.
    if rule=='Grand-fathering':
        emission_ref=emission_ref_year
    elif rule=='GDP':
        emission_ref=emission_ref_year*ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']==country]['2010'].values[0]/ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']=='World']['2010'].values[0]
    elif rule=='Population':
        emission_ref=emission_ref_year*ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']==country]['2010'].values[0]/ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']=='World']['2010'].values[0]
    elif rule=='GWP100':
        is_GWP100=True
    else:
        print('Unknown method. Code it!')
    if is_GWP100:
        output_df=input_df*GWP100
    else:
        output_df=(input_df.values-emission_ref)*(GWP100*Horizon)/40.
    return output_df

#Load impacts for different scenarios
activity_df=pd.read_csv("output/impact_2050"+file_name_suffix+".csv")
#Change name of rice for esthetic in graph
activity_df=activity_df.rename(columns = {'Production Rice, paddy':'Rice'})
activity_df=activity_df.rename(columns = {'Production Rice, paddy 2010':'Rice 2010'})

#Print methane quota
df_to_plot=activity_df.pivot(columns="Country")
df_to_plot=pd.concat([df_to_plot["National quota"],activity_df["Allocation rule"]],axis=1)
methane_quota_df=deepcopy(df_to_plot)

plot_boxplot(df_to_plot,country_list,"National CH4 quota (Mt)","Figs/methane_quota_bar_plot_countries"+file_name_suffix+".png",reference_df=methane_emissions_pd)
plot_boxplot(df_to_plot,country_list,"National CH4 quota (Mt)","Figs/methane_quota_bar_plot_countries"+file_name_suffix+".pdf",reference_df=methane_emissions_pd)
print("Print methane quota with different metrics...")

#Print production indicators for different quota
# Livestock production
production_list=['Milk','Meat','Eggs','Rice']
df_with_all_prod_to_plot=pd.DataFrame(columns=['Production index','Allocation rule','Production in 2010 (Mt)','Country','Item'])
for production in production_list:
    activity_df[production+' index']=activity_df[production]/activity_df[production+' 2010']
    activity_df.loc[activity_df[production+' 2010']==0,production+' index']=0
#    df_to_plot=activity_df.loc[:,['Country',production,"Allocation rule"]].pivot(columns="Country")
#    df_to_plot=pd.concat([df_to_plot[production],activity_df["Allocation rule"]],axis=1)
#    plot_boxplot(df_to_plot,country_list,"Production","Figs/production_"+production.lower().replace(" ","_")+"_bar_plot_countries.png")
#    plot_boxplot(df_to_plot,country_list,"Production","Figs/production_"+production.lower().replace(" ","_")+"_bar_plot_countries.pdf")
#    print("Print production with different metrics...")
    df_to_concat=pd.concat([activity_df[['Country','Pathways',production+' 2010',production+' index',"Allocation rule"]],pd.DataFrame([production]*len(activity_df['Country']),columns=['Item'])],axis=1,sort=True)
    df_to_concat=df_to_concat.rename(columns = {production+' index':'Production index'})
    df_to_concat=df_to_concat.rename(columns = {production+' 2010':'Production in 2010 (Mt)'})
    df_with_all_prod_to_plot=pd.concat([df_with_all_prod_to_plot,df_to_concat],axis=0,sort=True)

t_to_Mt=1E-6    
df_with_all_prod_to_plot.loc[df_with_all_prod_to_plot['Country']!=df_with_all_prod_to_plot['Pathways'],'Pathway']='Improved'
df_with_all_prod_to_plot.loc[df_with_all_prod_to_plot['Country']==df_with_all_prod_to_plot['Pathways'],'Pathway']='Current'
df_with_all_prod_to_plot['Production in 2010 (Mt)']=df_with_all_prod_to_plot['Production in 2010 (Mt)']*t_to_Mt
for country in country_list:
    plot_boxplot_with_sns(df_with_all_prod_to_plot,country,"Production index","Allocation rule","Production index (relative to 2010)",'Figs/production_bar_plot_'+country.lower().replace(' ','_')+file_name_suffix+'.png',item_column_name='Item',ref_column_name='Production in 2010 (Mt)',reference_df=None,plot_points=True)
print("Print all production with different metrics...")


#Print area spared for different quota
df_to_plot=pd.DataFrame(columns=['Spared area','Allocation rule','Country','Item'])
for item in ['Grassland','Feed','Rice','Total']:
    df_to_concat=pd.concat([activity_df[['Country','Pathways','Spared '+item+' area',"Allocation rule"]],pd.DataFrame([item]*len(activity_df['Country']),columns=['Item'])],axis=1,sort=True)
    df_to_concat=df_to_concat.rename(columns = {'Spared '+item+' area':'Spared area'})
    df_to_plot=pd.concat([df_to_plot,df_to_concat],axis=0,sort='True')

ha_2_Mha=1E-6
df_to_plot['Spared area']=df_to_plot['Spared area']*ha_2_Mha
df_to_plot.loc[df_to_plot['Country']!=df_to_plot['Pathways'],'Pathway']='Improved'
df_to_plot.loc[df_to_plot['Country']==df_to_plot['Pathways'],'Pathway']='Current'
for country in country_list:
    plot_boxplot_with_sns(df_to_plot,country,"Spared area","Allocation rule","Spared area (Mha)",'Figs/spared_area_bar_plot_'+country.lower().replace(' ','_')+file_name_suffix+'.png',item_column_name='Item',reference_df=None,plot_points=True)
print("Print all spared area with different metrics...")

#Print area index for different quota
df_to_plot=pd.DataFrame(columns=['Area index','Area in 2010 (Mha)','Allocation rule','Country','Item'])
for item in ['Grassland','Feed','Rice','Total']:
    df_to_concat=pd.concat([activity_df[['Country','Pathways',item+' area index',item+' area 2010',"Allocation rule"]],pd.DataFrame([item]*len(activity_df['Country']),columns=['Item'])],axis=1,sort=True)
    df_to_concat=df_to_concat.rename(columns = {item+' area index':'Area index'})
    df_to_concat=df_to_concat.rename(columns = {item+' area 2010':'Area in 2010 (Mha)'})
    df_to_plot=pd.concat([df_to_plot,df_to_concat],axis=0,sort='True')

ha_to_Mha=1E-6
df_to_plot['Area in 2010 (Mha)']=df_to_plot['Area in 2010 (Mha)']*ha_to_Mha
df_to_plot.loc[df_to_plot['Country']!=df_to_plot['Pathways'],'Pathway']='Improved'
df_to_plot.loc[df_to_plot['Country']==df_to_plot['Pathways'],'Pathway']='Current'
for country in country_list:
    plot_boxplot_with_sns(df_to_plot,country,"Area index","Allocation rule","Area index (relative to 2010)",'Figs/area_index_bar_plot_'+country.lower().replace(' ','_')+file_name_suffix+'.png',item_column_name='Item',ref_column_name='Area in 2010 (Mha)',reference_df=None,plot_points=True)
print("Print area index with different metrics...")

#Compute negative emissions of CO2
df_to_plot=pd.DataFrame(columns=['CO2 offset','Allocation rule','Country','Item'])
for item in ['Grassland','Feed','Rice','Total']:
    df_to_concat=pd.concat([activity_df[['Country','Pathways',item+' offset',"Allocation rule"]],pd.DataFrame([item]*len(activity_df['Country']),columns=['Item'])],axis=1,sort=True)
    df_to_concat=df_to_concat.rename(columns = {item+' offset':'CO2 offset'})
    df_to_plot=pd.concat([df_to_plot,df_to_concat],axis=0,sort='True')

df_to_plot['CO2 offset']=df_to_plot['CO2 offset']*t_to_Mt
df_to_plot.loc[df_to_plot['Country']!=df_to_plot['Pathways'],'Pathway']='Improved'
df_to_plot.loc[df_to_plot['Country']==df_to_plot['Pathways'],'Pathway']='Current'
for country in country_list:
    plot_boxplot_with_sns(df_to_plot,country,"CO2 offset","Allocation rule","CO2 offset (MtCO2)",'Figs/offset_bar_plot_'+country.lower().replace(' ','_')+file_name_suffix+'.png',item_column_name='Item',reference_df=None,plot_points=True)
print("Print CO2 offset with different metrics...")

#Compute AFOLU balance
activity_df.loc[:,'AFOLU balance(MtCO2eq)']=0
df_pivot=activity_df.pivot(columns="Country")
df_offset=pd.concat([df_pivot["Total offset"],activity_df["Allocation rule"]],axis=1)
df_to_plot=pd.concat([df_pivot["AFOLU balance(MtCO2eq)"],activity_df["Allocation rule"]],axis=1)
for country in country_list:
    emission_ref_year=methane_emissions_pd['Value'][methane_emissions_pd['Area']==country].values[0]*kt_2_Mt
    for rule in np.unique(df_to_plot['Allocation rule']):
        country_rule_mak=(methane_quota_df['Allocation rule']==rule) & (~np.isnan(methane_quota_df[country]))
        CO2_equivalent=compute_CO2_equivalent(methane_quota_df.loc[country_rule_mak,country],rule,emission_ref_year,country,ponderation_in_GWP_star=ponderation_dict[rule])
        df_to_plot.loc[df_to_plot['Allocation rule']==rule,country]=-df_offset.loc[country_rule_mak,country]*t_to_Mt+CO2_equivalent*t_to_Mt
plot_boxplot(df_to_plot,country_list,"AFOLU balance(MtCO2eq)","Figs/AFOLU_balance_bar_plot_countries"+file_name_suffix+".png")
#plot_boxplot(df_to_plot,country_list,"Net AFOLU balance (MtCH4)","Figs/CH4_net_bar_plot_countries.pdf")
print("Print net AFOLU balance with different metrics...")
