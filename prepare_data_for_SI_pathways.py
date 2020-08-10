#! /bin/python

from common_data import read_FAOSTAT_df
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
import seaborn as sns

gleam_intake_df = read_FAOSTAT_df("data/GLEAM_Intake.csv",delimiter=";")
#gleam_intake_df = read_FAOSTAT_df("data/GLEAM_Intake_tropical_warm.csv",delimiter=",")
faostat_yield_df = read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")
fostat_methane_df = read_FAOSTAT_df("data/FAOSTAT_enteric_fermentation.csv",delimiter="|")

fostat_methane_df.loc[fostat_methane_df["Area"]=="United Kingdom of Great Britain and Northern Ireland","Area"] = "United Kingdom"

fostat_methane_df.index=fostat_methane_df["Area"]
gleam_intake_df.index=gleam_intake_df["Country"]
gleam_intake_df.index.name="Area"
faostat_yield_df.index=faostat_yield_df["Area"]

country_list = list(set(gleam_intake_df["Country"]).intersection(set(faostat_yield_df["Area"])))
country_list = list(set(country_list).intersection(set(fostat_methane_df["Area"])))

#country_list.remove("Mongolia")

fostat_yield_country_mask = faostat_yield_df["Area"].isin(country_list)
fostat_yield_element_mask = faostat_yield_df["Element"]=="Yield"
fostat_yield_item_mask = faostat_yield_df["Item"]=="Milk, Total"
fostat_meat_item_mask = faostat_yield_df["Item"]=="Beef and Buffalo Meat"
fostat_meat_element_mask = faostat_yield_df["Element"]=="Yield/Carcass Weight"
fostat_methane_country_mask = fostat_methane_df["Area"].isin(country_list)
fostat_methane_emissions_mask = fostat_methane_df["Element"]=="Emissions (CH4) (Enteric)"
fostat_methane_stock_mask = fostat_methane_df["Element"]=="Stocks"
fostat_methane_item_mask = fostat_methane_df["Item"]=="Cattle, dairy"
fostat_methane_meat_item_mask = fostat_methane_df["Item"]=="Cattle"
gleam_variable_mask = gleam_intake_df["Variable"].str.contains("INTAKE: Total intake - Grains")
gleam_grass_mask = gleam_intake_df["Variable"].str.contains("INTAKE: Total intake - Roughages")
gleam_total_mask = gleam_intake_df["Variable"]=="INTAKE: Total intake"
gleam_number_mask = gleam_intake_df["Variable"]=="HERD: total number of animals"
gleam_herd_type_mask= gleam_intake_df["Herd type"]=="Dairy"
gleam_species_mask= gleam_intake_df["Species"]=="Cattle"
gleam_country_mask= gleam_intake_df["Country"].isin(country_list)

df_to_plot=pd.DataFrame(columns=["Methane_intensity","Milk_yield","Concentrate_intake"])

df_to_plot["Milk_yield"]=faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Value"] #kg/year
df_to_plot.index=faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Area"]
df_to_plot["Methane_intensity"]=fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_emissions_mask & fostat_methane_item_mask,"Value"]*1000/fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_stock_mask & fostat_methane_item_mask,"Value"]#/(faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Value"]*1000)
no_zero_mask = gleam_intake_df.loc[gleam_total_mask,"Value"]!=0
df_to_plot["Total_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_total_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
df_to_plot["Concentrate_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_variable_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
# df_to_plot.loc[df_to_plot["Concentrate_intake"]==0,"Concentrate_intake"]=1E-3
df_to_plot["Grass_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
df_to_plot = df_to_plot.dropna()

df_to_plot["GAEZ"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"GAEZ"]

# df_to_plot["Grass_intake_average"]=np.int64(df_to_plot["Grass_intake"])
# df_to_plot["Concentrate_intake_2"]=df_to_plot["Concentrate_intake"]*df_to_plot["Concentrate_intake"]
# df_to_plot["Conversion_rate"]=df_to_plot["Methane_intensity"]/df_to_plot["Total_intake"]*1E6

# from linearmodels import PanelOLS
# from linearmodels import RandomEffects
#
# exog_vars = ["Concentrate_intake"]
# exog = sm.add_constant(df_to_plot[exog_vars])
# mod = RandomEffects(data.clscrap, exog)
# re_res = mod.fit()
# print(re_res)

df_to_plot["Grass_intake_cat"] = np.round(df_to_plot["Grass_intake"])
# df_to_plot.to_csv("output/data_for_lm.csv")
# #df_to_plot["Grass_intake"] = df_to_plot["Grass_intake"].astype("category")
# md = smf.mixedlm("Methane_intensity ~ (1 | Grass_intake) + Concentrate_intake", df_to_plot, re_formula="1", groups=df_to_plot["Grass_intake"])
# # md = sm.MixedLM(df_to_plot["Methane_intensity"],df_to_plot["Concentrate_intake"],exog_re=df_to_plot["Total_intake"])
# mdf = md.fit()
# print(mdf.summary())


# re = mdf.cov_re.iloc[0,0]
# likev = mdf.profile_re(0, 're',dist_low=0.5*re, dist_high=0.8*re)
# plt.figure(figsize=(10,8))
# plt.plot(likev[:,0], 2*likev[:,1])
# plt.xlabel("Variance of random slope", size=17)
# plt.ylabel("-2 times profile log likelihood", size=17)

# df_to_plot = df_to_plot.drop(index=["Antigua and Barbuda","Guyana","Ecuador"])
# df_to_plot["Grass_intake"] = df_to_plot["Grass_intake"].astype("category")
# df_to_plot["Total_intake_cat"] = np.around(df_to_plot["Total_intake"])
# index_list = df_to_plot.index[df_to_plot['Total_intake_cat'] == 2.].tolist()
# df_to_plot.loc[index_list,"Total_intake_cat"]=3.
# index_list = df_to_plot.index[df_to_plot['Total_intake_cat'] == 24.].tolist()
# df_to_plot.loc[index_list,"Total_intake_cat"]=11.
# index_list = df_to_plot.index[df_to_plot['Total_intake_cat'] == 17.].tolist()
# df_to_plot.loc[index_list,"Total_intake_cat"]=11.
df_to_plot["Grass_intake_cat"] = np.around(df_to_plot["Grass_intake"])
index_list = df_to_plot.index[df_to_plot['Grass_intake_cat'] == 14.].tolist()
df_to_plot.loc[index_list,"Grass_intake_cat"]=9.
index_list = df_to_plot.index[df_to_plot['Grass_intake_cat'] == 20.].tolist()
df_to_plot.loc[index_list,"Grass_intake_cat"]=9.

df_to_plot.drop(index=["Antigua and Barbuda"])
df_to_plot = df_to_plot.dropna()

df_to_plot.to_csv("output/data_dairy_for_lm.csv")

# fig = plt.figure()
# ax1 = fig.add_subplot(121)
# #df_to_plot.plot(ax=ax1,x="Total_intake", y=["Methane_intensity",], kind="scatter")
# #df_to_plot.plot(ax=ax2, x="Concentrate_intake", y='Milk_yield',color='g',kind="scatter")
# sns.lmplot(x="Concentrate_intake",y="Methane_intensity",data=df_to_plot, fit_reg=True,order=2) #,hue="GAEZ"
# ax2 = fig.add_subplot(122)
# sns.lmplot(x="Concentrate_intake",y="Milk_yield",data=df_to_plot,fit_reg=True,order=2)#,hue="GAEZ"
# #ax1.set_ylabel('Methane intensity')
# #ax1.set_ylabel('Milk_yield')
# plt.show()

# model = sm.formula.ols(formula='Methane_intensity ~ Concentrate_intake_2', data=df_to_plot)
# res = model.fit()
# print(res.summary())
# model2 = sm.formula.ols(formula='Milk_yield ~ Concentrate_intake_2', data=df_to_plot)
# res2 = model2.fit()
# print(res2.summary())
# plt.savefig("output/Methane_intensity_milk_yield_concentrate_share.png")
# #plt.show()

df_to_plot=pd.DataFrame(columns=["Methane_intensity","Meat_yield","Concentrate_intake","Grass_intake"])

gleam_herd_type_mask= gleam_intake_df["Herd type"]=="Non-dairy"

df_to_plot["Meat_yield"]=faostat_yield_df.loc[fostat_yield_country_mask & fostat_meat_element_mask & fostat_meat_item_mask,"Value"] #kg/year
df_to_plot.index=faostat_yield_df.loc[fostat_yield_country_mask & fostat_meat_element_mask & fostat_meat_item_mask,"Area"]
df_to_plot["Methane_intensity"]=fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_emissions_mask & fostat_methane_item_mask,"Value"]*1000/fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_stock_mask & fostat_methane_meat_item_mask,"Value"]#/(faostat_yield_df.loc[fostat_yield_country_mask & fostat_meat_element_mask & fostat_meat_item_mask,"Value"]*1000)
df_to_plot["Concentrate_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_variable_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
df_to_plot["Grass_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
df_to_plot["Grass_intake_cat"] = np.round(df_to_plot["Grass_intake"])
df_to_plot["GAEZ"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"GAEZ"]

# fig = plt.figure()
# ax1 = fig.add_subplot(121)
# # df_to_plot.plot(ax=ax1,x="Concentrate_intake", y=["Methane_intensity",], kind="scatter",trendline="lowess")
# # df_to_plot.scatter(ax=ax2, x="Concentrate_intake", y='Milk_yield',color='g',kind="scatter",trendline="lowess")
# sns.regplot(x="Concentrate_intake",y="Methane_intensity",data=df_to_plot, fit_reg=True,ax=ax1,order=1)
# ax2 = fig.add_subplot(122)
# sns.regplot(x="Concentrate_intake",y="Meat_yield",data=df_to_plot, fit_reg=True,ax=ax2,color="g",order=2)
# ax1.set_ylabel('Methane_intensity')
# ax2.set_ylabel('Meat_yield')
# plt.show()

df_to_plot.to_csv("output/data_non-dairy_for_lm.csv")
