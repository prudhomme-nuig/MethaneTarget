# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 09:10:12 2020

@author: prudhomme
"""

import pandas as pd
import numpy as np

food_content={}
#Energy content comes from McCance & Widdowson 2019
food_content["energy"]=pd.read_csv("data/McCance_food_energy_content.csv",sep=",")
#Protein content comes from Gleam documentation
food_content["protein"]=pd.read_csv("data/Gleam_food_protein_content.csv",sep=",")

#BFM comes from Gleam documentation
bfm_fraction=pd.read_csv("data/Gleam_bfm_fraction.csv",sep=",")

food_requirement={}
#Energy requirement comes from McCance & Widdowson 2019
food_requirement["energy"]=2000*365
#Protein requirement comes from McCance & Widdowson 2019
food_requirement["protein"]=50*365

#Load impacts for different scenarios
activity_df=pd.read_csv("output/AFOLU_balance_2050.csv")
activity_df["Intensification"]=np.nan
activity_df.loc[(activity_df["Mitigation"]!="MACC") & (activity_df["Pathways"]!="Intensified"),"Intensification"]="Base"
activity_df.loc[(activity_df["Mitigation"]=="MACC") & (activity_df["Pathways"]!="Intensified"),"Intensification"]="2050 MACC"
activity_df.loc[(activity_df["Mitigation"]=="MACC") & (activity_df["Pathways"]=="Intensified"),"Intensification"]="2050 SI"
activity_df["MACC"]=np.nan
activity_df["Base"]=np.nan
activity_df["SI"]=np.nan
activity_df.loc[(activity_df["Intensification"]=="2050 SI"),"SI"]="SI"
activity_df.loc[(activity_df["Intensification"]=="Base"),"Base"]="Base"
activity_df.loc[(activity_df["Intensification"]=="2050 MACC"),"MACC"]="2050 MACC"
activity_df["Protein allocation"]=np.nan
activity_df["Population allocation"]=np.nan
activity_df["Grand-parenting allocation"]=np.nan
activity_df["GDP allocation"]=np.nan
activity_df.loc[(activity_df["Allocation rule"]=="Protein"),"Protein allocation"]="Protein"
activity_df.loc[(activity_df["Allocation rule"]=="Population"),"Population allocation"]="Population"
activity_df.loc[(activity_df["Allocation rule"]=="Grand-parenting"),"Grand-parenting allocation"]="Grand-parenting"
activity_df.loc[(activity_df["Allocation rule"]=="GDP"),"GDP allocation"]="GDP"
activity_df=activity_df.rename(columns = {'Production Rice, paddy':'Rice'})

production_list=['Milk','Ruminant Meat','Monogastric Meat','Eggs','Rice']
df_with_all_prod_to_plot=pd.DataFrame(columns=['Production index','Allocation rule','Mitigation','Production in 2010 (Mt)','Production','Country','Item'])
for production in production_list:
    if "Person fed in energy" not in activity_df.columns.values:
        activity_df["Person fed in energy"]=activity_df[production]*food_content["energy"].loc[0,production]*bfm_fraction.loc[0,production]/food_requirement["energy"]
        activity_df["Person fed in protein"]=activity_df[production]*food_content["protein"].loc[0,production]*bfm_fraction.loc[0,production]/food_requirement["protein"]
    else:
        activity_df["Person fed in energy"]+=activity_df[production]*food_content["energy"].loc[0,production]*bfm_fraction.loc[0,production]/food_requirement["energy"]
        activity_df["Person fed in protein"]+=activity_df[production]*food_content["protein"].loc[0,production]*bfm_fraction.loc[0,production]/food_requirement["protein"]

#table with all scenarios
df_with_all_prod_to_plot=activity_df[["Person fed in energy","Person fed in protein","Intensification","Country",'Allocation rule']]
table = pd.pivot_table(df_with_all_prod_to_plot, values=["Person fed in energy","Person fed in protein"], index=['Country','Allocation rule'],columns=["Intensification"],aggfunc=np.mean)
table.index.name=None
table.to_excel("output/table_person_fed.xlsx",index_label=None,float_format = "%0.1f")

#table of scenarios with AFOLU closed to C neutrality (with eGWP*)
df_with_all_prod_to_plot=activity_df.loc[np.abs(activity_df["AFOLU balance (with eGWP*)"])<1E6,["Person fed in energy","Person fed in protein","Intensification","Country",'Allocation rule']]
table = pd.pivot_table(df_with_all_prod_to_plot, values=["Person fed in energy","Person fed in protein"], index=['Country','Allocation rule'],columns=["Intensification"],aggfunc=np.mean)
table.index.name=None
table.to_excel("output/table_person_fed_C_neutrality.xlsx",index_label=None,float_format = "%0.1f")

#Table of scenarios for different AFOLU balance
country_list=["Brazil","France","India","Ireland"]
first_quantile=activity_df.groupby("Country")["AFOLU balance (with eGWP*)"].quantile(0.25)
second_quantile=activity_df.groupby("Country")["AFOLU balance (with eGWP*)"].quantile(0.5)
third_quantile=activity_df.groupby("Country")["AFOLU balance (with eGWP*)"].quantile(0.75)
activity_df["Quantile"]=np.nan
activity_df["Percent mitigation"]=np.nan
activity_df["Percent mitigation"]=np.nan
for country in country_list:
    activity_df.loc[(activity_df['Country']==country) & (activity_df['AFOLU balance (with eGWP*)']<first_quantile[country]),"Quantile"]="First"
    activity_df.loc[(activity_df['Country']==country) & (activity_df['AFOLU balance (with eGWP*)']>=first_quantile[country]) & (activity_df['AFOLU balance (with eGWP*)']<second_quantile[country]),"Quantile"]="Second"
    activity_df.loc[(activity_df['Country']==country) & (activity_df['AFOLU balance (with eGWP*)']>=second_quantile[country]) & (activity_df['AFOLU balance (with eGWP*)']<third_quantile[country]),"Quantile"]="Third"
    activity_df.loc[(activity_df['Country']==country) & (activity_df['AFOLU balance (with eGWP*)']>=third_quantile[country]),"Quantile"]="Fourth"

activity_df["Pathway"]=np.nan
activity_df.loc[(activity_df["Pathways"]!="Intensified"),"Pathway"]="Base"
activity_df.loc[(activity_df["Pathways"]=="Intensified"),"Pathway"]="Intensified"

activity_df["Methane emissions (MtCH4)"]=activity_df["National quota"]*1E-6
activity_df["CO2 offset (MtCO2)"]=-activity_df["Total CO2 emissions"]*1E-6
activity_df["Person fed in energy (Mio heads)"]=activity_df["Person fed in energy"]*1E-3
activity_df["Person fed in protein (Mio heads)"]=activity_df["Person fed in protein"]*1E-3
activity_df["AFOLU balance (with eGWP*)"]=activity_df["AFOLU balance (with eGWP*)"]/1E-6
activity_df.to_csv("output/table_AFOLU_balance_impact_person_fed.csv")

table_mean = pd.pivot_table(activity_df, values=["Person fed in energy (Mio heads)","Person fed in protein (Mio heads)","Methane emissions (MtCH4)","CO2 offset (MtCO2)","AFOLU balance (with eGWP*)"], index=['Country','Quantile'],aggfunc=np.median)
table_count_SI = pd.pivot_table(activity_df, values=["Person fed in energy (Mio heads)"],columns="Intensification", index=['Country','Quantile'],aggfunc="count")
table_count_population = pd.pivot_table(activity_df, values=["Person fed in energy (Mio heads)"],columns="Allocation rule",index=['Country',"Quantile"],aggfunc=len)
table_count_test = pd.pivot_table(activity_df, values=["Intensification"],index=['Country',"Quantile"],aggfunc="count")
table_count_SI = np.divide(table_count_SI,table_count_test)*100
table_count_population=table_count_population/136*100
table = pd.concat([table_mean,table_count_SI,table_count_population],axis=1)
table.index.name=None

table_t=table.transpose(copy=True)
table_t.style.background_gradient(cmap="coolwarm",axis=1,subset="Brazil")\
    .background_gradient(cmap="coolwarm",axis=1,subset="France")\
    .background_gradient(cmap="coolwarm",axis=1,subset="India")\
    .background_gradient(cmap="coolwarm",axis=1,subset="Ireland").to_excel("output/table_AFOLU_balance_impact.xlsx",index_label=None,float_format = "%0.1f")


import seaborn as sns
#labels, index = np.unique(activity_df.loc[activity_df["Country"]=="Ireland","Intensification"], return_inverse=True)
g = sns.relplot(x="Methane emissions (MtCH4)", y="AFOLU balance (with eGWP*)", data=activity_df.loc[activity_df["Country"]=="Ireland",:], hue="Intensification",style="Allocation rule",kind='scatter')
g.savefig("Figs/Ireland_AFOLU_balance_methane_emissions.png")

df_to_plot=activity_df[["Country","Methane emissions (MtCH4)","AFOLU balance (with GWP*)","AFOLU balance (with GWP100)","Intensification","Allocation rule"]]
df_to_plot=df_to_plot.melt(["Country","Methane emissions (MtCH4)","Intensification","Allocation rule"],var_name="Equivalent metrics",value_name='AFOLU balance')
g=sns.relplot(x="Methane emissions (MtCH4)", y="AFOLU balance", data=df_to_plot.loc[df_to_plot["Country"]=="Ireland",:], hue="Equivalent metrics",style="Allocation rule",kind='scatter')
g.savefig("Figs/Ireland_comparison_AFOLU_balance_methane_emissions_with_GWP100_GWPstar.png")
#activity_df.loc[activity_df["Country"]=="Ireland",:].plot.scatter(x="Person fed in protein (Mio heads)",y="AFOLU balance (with eGWP*)",c="Intensification")
