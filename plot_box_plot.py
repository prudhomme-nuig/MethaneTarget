#! /bin/python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy
import matplotlib.cm as cm
import seaborn as sns
import argparse
from common_data import read_FAOSTAT_df

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
            ax[0][0].scatter(rule+1,reference_df[reference_df['Area']==country_list[0]]['Value'].values[0], c='red')
            ax[0][1].scatter(rule+1,reference_df[reference_df['Area']==country_list[1]]['Value'].values[0], c='red')
            ax[1][0].scatter(rule+1,reference_df[reference_df['Area']==country_list[2]]['Value'].values[0], c='red')
            ax[1][1].scatter(rule+1,reference_df[reference_df['Area']==country_list[3]]['Value'].values[0], c='red')
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
                    if rule!=allocation_list[0]:
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
        plt.tight_layout()
        fig.savefig(file_name)
        plt.close('all')

def plot_boxplot_quota_with_sns(df_to_plot,country_list,y_column_name,allocation_column_name,y_label,file_name,item_column_name=None,ref_column_name=None,reference_df=None,plot_points=False,subplot=None):
    fig, axes = plt.subplots(2*subplot[0], subplot[1],figsize=(11.7, 8.27),gridspec_kw = {'height_ratios':[1/(5*subplot[0]),4/(5*subplot[0])]*subplot[0]})
    index_country=0;ax_index_list=[];ax_value_list=[];y_label_list=[]
    for row_index in range(subplot[0]):
        ax_value_list.extend([axes[row_index*2][index] for index in range(subplot[1])])
        ax_index_list.extend([axes[row_index*2+1][index] for index in range(subplot[1])])
        y_label_list.extend([True,False])
    for (ax_value,ax_index,country,y) in zip(ax_value_list,ax_index_list,country_list,y_label_list):
        country_mask=(df_to_plot['Country']==country)
        sns.swarmplot(item_column_name, ref_column_name, data=df_to_plot[country_mask],ax=ax_value,size=5)
        ax_value.set_title(country)
        plt.subplots_adjust(top = 0.9,hspace = 1.)
        if not y:
                ax_value.yaxis.label.set_visible(False)
        with sns.axes_style(style='ticks'):
            sns.catplot(item_column_name, y_column_name, data=df_to_plot[country_mask], kind="box",height=8.27, aspect=11.7/8.27,ax=ax_index)            
            if not y:
                ax_index.yaxis.label.set_visible(False)
            ax_index.tick_params(axis = 'x', which = 'major', labelsize = 12)
            ax_index.spines["top"].set_visible(False)
            ax_index.spines["right"].set_visible(False)
            ax_index.xaxis.label.set_visible(False)
            index_country+=1
            plt.subplots_adjust(wspace =0.,top = 0.9,hspace = 0.)
    plt.tight_layout()
    fig.savefig(file_name)
    plt.close('all')

def compute_CO2_equivalent(input_df,rule,emission_ref_year,country,ponderation_in_GWP_star=None,offset_change_world=None):
    output_df=deepcopy(input_df)
    is_GWP100=False
    Horizon=100.
    if rule=='Grand-fathering':
        emission_ref=emission_ref_year
    elif rule=='Debt':
        emission_ref=input_df.values-ponderation_in_GWP_star[country].values[0]*offset_change_world
    elif rule=='GDP':
        emission_ref=input_df.values-ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']==country]['2010'].values[0]/ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']=='World']['2010'].values[0]*offset_change_world
    elif rule=='Population':
        emission_ref=emission_ref_year*ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']==country]['2010'].values[0]/ponderation_in_GWP_star[ponderation_in_GWP_star['Country Name']=='World']['2010'].values[0]
    elif rule=='Protein':
        emission_ref=emission_ref_year*ponderation_in_GWP_star[country].values[0]
    elif rule=='GWP100':
        is_GWP100=True
    else:
        print('Unknown method. Code it!')
    if is_GWP100:
        output_df=input_df*GWP100_CH4
    else:
        output_df=(input_df.values-emission_ref)*(GWP100_CH4*Horizon)/40.
    return output_df

#Load impacts for different scenarios
activity_df=pd.read_csv("output/impact_2050"+file_name_suffix+".csv")
#Change name of rice for esthetic in graph
activity_df=activity_df.rename(columns = {'Production Rice, paddy':'Rice'})
activity_df=activity_df.rename(columns = {'Production Rice, paddy 2010':'Rice 2010'})
for country in country_list:
    activity_df.loc[activity_df['Country']==country,'National methane 2010']=methane_emissions_pd.loc[methane_emissions_pd['Area']==country,'Value'].values[0]

activity_df.loc[:,'National methane index']=activity_df.loc[:,'National quota']/activity_df.loc[:,'National methane 2010']
activity_df.loc[activity_df['National methane 2010']==0,'National methane index']=0

#Print methane quota
df_to_plot=activity_df.loc[:,['Country','Pathways',"National methane 2010","National methane index","Allocation rule"]]
df_to_plot.loc[:,"Methane\n2010\n(ktCH4)"]=df_to_plot.loc[:,"National methane 2010"].values*t_to_Mt
df_to_plot=df_to_plot.rename(columns = {'National methane index':'Methane index'})
plot_boxplot_quota_with_sns(df_to_plot,country_list,"Methane index","Country","Methane index (relative to 2010)",'Figs/methane_quota_bar_plot_test.png',item_column_name='Allocation rule',ref_column_name='Methane\n2010\n(ktCH4)',reference_df=None,plot_points=False,subplot=(2,2))
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
    df_to_concat=df_to_concat.rename(columns = {production+' index':'Production index (relative to 2010)'})
    df_to_concat=df_to_concat.rename(columns = {production+' 2010':'Production in 2010 (Mt)'})
    df_with_all_prod_to_plot=pd.concat([df_with_all_prod_to_plot,df_to_concat],axis=0,sort=True)

df_with_all_prod_to_plot.loc[df_with_all_prod_to_plot['Country']!=df_with_all_prod_to_plot['Pathways'],'Pathway']='Improved'
df_with_all_prod_to_plot.loc[df_with_all_prod_to_plot['Country']==df_with_all_prod_to_plot['Pathways'],'Pathway']='Current'
df_with_all_prod_to_plot['Production in 2010 (Mt)']=df_with_all_prod_to_plot['Production in 2010 (Mt)']*t_to_Mt
for country in country_list:
    plot_boxplot_with_sns(df_with_all_prod_to_plot,country,"Production index (relative to 2010)","Allocation rule","Production index (relative to 2010)",'Figs/production_bar_plot_'+country.lower().replace(' ','_')+file_name_suffix+'.png',item_column_name='Item',ref_column_name='Production in 2010 (Mt)',reference_df=None,plot_points=True)
print("Print all production with different metrics...")

#Print area change for different quota
df_to_plot=pd.DataFrame(columns=['Area change','Allocation rule','Country','Item'])
for item in ['Grass','Feed','Rice','Total']:
    df_to_concat=pd.concat([activity_df[['Country','Pathways',item+' area change',"Allocation rule"]],pd.DataFrame([item]*len(activity_df['Country']),columns=['Item'])],axis=1,sort=True)
    df_to_concat=df_to_concat.rename(columns = {item+' area change':'Area change'})
    df_to_plot=pd.concat([df_to_plot,df_to_concat],axis=0,sort='True')

ha_2_Mha=1E-6
df_to_plot['Area change']=df_to_plot['Area change']*ha_2_Mha
df_to_plot.loc[df_to_plot['Country']!=df_to_plot['Pathways'],'Pathway']='Improved'
df_to_plot.loc[df_to_plot['Country']==df_to_plot['Pathways'],'Pathway']='Current'
for country in country_list:
    plot_boxplot_with_sns(df_to_plot,country,"Area change","Allocation rule","Area change (Mha)",'Figs/changed_area_bar_plot_'+country.lower().replace(' ','_')+file_name_suffix+'.png',item_column_name='Item',reference_df=None,plot_points=True)
print("Print all change of area with different metrics...")

#Print area index for different quota
df_to_plot=pd.DataFrame(columns=['Area index','Area in 2010 (Mha)','Allocation rule','Country','Item'])
for item in ['Grass','Feed','Rice','Total']:
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

#Compute N2O emissions from manure
df_to_plot=pd.DataFrame(columns=['N2O emissions','Allocation rule','Country','Item'])
for item in ['manure','feed']:
    df_to_concat=pd.concat([activity_df[['Country','Pathways','N2O '+item+' index', 'N2O '+item+' 2010',"Allocation rule"]],pd.DataFrame([item]*len(activity_df['Country']),columns=['Item'])],axis=1,sort=True)
    df_to_concat=df_to_concat.rename(columns = {'N2O '+item+' 2010':'N2O emissions in 2010'})
    df_to_concat=df_to_concat.rename(columns = {'N2O '+item+' index':'N2O index (compared to 2010)'})
    df_to_plot=pd.concat([df_to_plot,df_to_concat],axis=0,sort='True')

df_to_plot['N2O emissions in 2010 (ktN2O)']=df_to_plot['N2O emissions in 2010']*t_to_kt
df_to_plot.loc[df_to_plot['Country']!=df_to_plot['Pathways'],'Pathway']='Improved'
df_to_plot.loc[df_to_plot['Country']==df_to_plot['Pathways'],'Pathway']='Current'
for country in country_list:
    plot_boxplot_with_sns(df_to_plot,country,"N2O index (compared to 2010)","Allocation rule","N2O index (compared to 2010)",'Figs/N2O_index_bar_plot_'+country.lower().replace(' ','_')+file_name_suffix+'.png',item_column_name='Item',ref_column_name='N2O emissions in 2010 (ktN2O)',reference_df=None,plot_points=True)
print("Print N2O with different metrics...")

#Compute negative emissions of CO2
df_to_plot=pd.DataFrame(columns=['CO2 offset','Allocation rule','Country','Item'])
for item in ['Grass','Feed','Rice','Total']:
    df_to_concat=pd.concat([activity_df[['Country','Pathways',item+' offset',"Allocation rule"]],pd.DataFrame([item]*len(activity_df['Country']),columns=['Item'])],axis=1,sort=True)
    df_to_concat=df_to_concat.rename(columns = {item+' offset':'CO2 offset'})
    df_to_plot=pd.concat([df_to_plot,df_to_concat],axis=0,sort='True')

df_to_plot['CO2 offset (MtCO2)']=df_to_plot['CO2 offset']*t_to_Mt
df_to_plot.loc[df_to_plot['Country']!=df_to_plot['Pathways'],'Pathway']='Improved'
df_to_plot.loc[df_to_plot['Country']==df_to_plot['Pathways'],'Pathway']='Current'
for country in country_list:
    plot_boxplot_with_sns(df_to_plot,country,"CO2 offset (MtCO2)","Allocation rule","CO2 offset (MtCO2)",'Figs/offset_bar_plot_'+country.lower().replace(' ','_')+file_name_suffix+'.png',item_column_name='Item',reference_df=None,plot_points=True)
print("Print CO2 offset with different metrics...")

#Compute AFOLU balance
GWP100_N2O=298
activity_df.loc[:,'AFOLU balance(MtCO2eq)']=0
activity_df['CO2 offset world']=(activity_df['2050']-activity_df['2010'])
df_pivot=activity_df.pivot(columns="Country")
df_offset=pd.concat([df_pivot["Total offset"],activity_df["Allocation rule"]],axis=1)
df_to_plot=pd.concat([df_pivot["AFOLU balance(MtCO2eq)"],activity_df["Allocation rule"]],axis=1)
for country in country_list:
    emission_ref_year=methane_emissions_pd['Value'][methane_emissions_pd['Area']==country].values[0]
    for rule in np.unique(df_to_plot['Allocation rule']):
        country_rule_mak=(df_pivot['Allocation rule'][country]==rule) & (~np.isnan(df_pivot['N2O'][country]))
        N2O_emissions=df_pivot['N2O'].loc[country_rule_mak,country]*t_2_Mt*GWP100_N2O
        CO2_equivalent=compute_CO2_equivalent(df_pivot['National quota'].loc[country_rule_mak,country],rule,emission_ref_year,country,ponderation_in_GWP_star=ponderation_dict[rule],offset_change_world=pd.pivot(activity_df,columns='Country')['CO2 offset world'][country][country_rule_mak])
        df_to_plot.loc[df_to_plot['Allocation rule']==rule,country]=-df_offset.loc[country_rule_mak,country]*t_to_Mt+CO2_equivalent*t_to_Mt+N2O_emissions
plot_boxplot(df_to_plot,country_list,"AFOLU balance(MtCO2eq)","Figs/AFOLU_balance_bar_plot_countries"+file_name_suffix+".png")
#plot_boxplot(df_to_plot,country_list,"Net AFOLU balance (MtCH4)","Figs/CH4_net_bar_plot_countries.pdf")
print("Print net AFOLU balance with different metrics...")
