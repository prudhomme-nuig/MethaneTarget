#! /bin/python

from common_data import read_FAOSTAT_df
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
import seaborn as sns

gleam_intake_df = read_FAOSTAT_df("data/GLEAM_Intake.csv",delimiter=";")
faostat_yield_df = read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")
fostat_methane_df = read_FAOSTAT_df("data/FAOSTAT_enteric_fermentation.csv",delimiter="|")
fostat_manure_df = read_FAOSTAT_df("data/FAOSTAT_N2O_manure_management.csv",delimiter="|")
fostat_manure_df.index=range(len(fostat_manure_df))
fostat_manure_df.index=fostat_manure_df["Area"]
fostat_methane_df.loc[fostat_methane_df["Area"]=="United Kingdom of Great Britain and Northern Ireland","Area"] = "United Kingdom"

fostat_methane_df.index=fostat_methane_df["Area"]
gleam_intake_df.index=gleam_intake_df["Country"]
gleam_intake_df.index.name="Area"
faostat_yield_df.index=faostat_yield_df["Area"]

country_list = list(set(gleam_intake_df["Country"]).intersection(set(faostat_yield_df["Area"])))
country_list = list(set(country_list).intersection(set(fostat_methane_df["Area"])))

#Yield df masks
fostat_yield_country_mask = faostat_yield_df["Area"].isin(country_list)
fostat_yield_element_mask = faostat_yield_df["Element"]=="Yield"
fostat_yield_item_mask = faostat_yield_df["Item"]=="Milk, Total"
fostat_meat_item_mask = faostat_yield_df["Item"]=="Beef and Buffalo Meat"
fostat_meat_element_mask = faostat_yield_df["Element"]=="Yield/Carcass Weight"
#Methane masks
fostat_methane_country_mask = fostat_methane_df["Area"].isin(country_list)
fostat_methane_emissions_mask = fostat_methane_df["Element"]=="Emissions (CH4) (Enteric)"
fostat_methane_stock_mask = fostat_methane_df["Element"]=="Stocks"
fostat_methane_item_mask = fostat_methane_df["Item"]=="Cattle, dairy"
fostat_methane_meat_item_mask = fostat_methane_df["Item"]=="Cattle, non-dairy"
#Gleam df masks
gleam_variable_mask = gleam_intake_df["Variable"].str.contains("INTAKE: Total intake - Grains")
gleam_grass_mask = gleam_intake_df["Variable"].str.contains("INTAKE: Total intake - Roughages")
gleam_total_mask = gleam_intake_df["Variable"]=="INTAKE: Total intake"
gleam_number_mask = gleam_intake_df["Variable"]=="HERD: total number of animals"
gleam_herd_type_mask= gleam_intake_df["Herd type"]=="Dairy"
gleam_non_dairy_mask= gleam_intake_df["Herd type"]=="Non-dairy"
gleam_species_mask= gleam_intake_df["Species"]=="Cattle"
gleam_country_mask= gleam_intake_df["Country"].isin(country_list)
#Manure masks
fostat_manure_emissions_mask = fostat_manure_df["Element"].str.contains("Emissions \(CH4\)")
fostat_manure_country_mask = fostat_manure_df["Area"].isin(country_list)
fostat_manure_stock_mask = fostat_manure_df["Element"]=="Stocks"
fostat_manure_dairy_mask = fostat_manure_df["Item"]=="Cattle, dairy"
fostat_manure_non_dairy_mask = fostat_manure_df["Item"]=="Cattle, non-dairy"
fostat_manure_poultry_mask = fostat_manure_df["Item"]=="Poultry Birds"
fostat_manure_chicken_mask = fostat_manure_df["Item"]=="Chickens, layers"
fostat_manure_sheep_mask = fostat_manure_df["Item"]=="Sheep and Goats"
fostat_manure_swine_mask = fostat_manure_df["Item"]=="Swine"
fostat_manure_domain_mask = fostat_manure_df["Domain"]=="Manure Management"

df_to_plot=pd.DataFrame(columns=["Methane_intensity","Milk_yield","Concentrate_intake"])

df_to_plot["Milk_yield"]=faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Value"] #kg/year
df_to_plot.index=faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Area"]
df_to_plot["Methane_intensity"]=fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_emissions_mask & fostat_methane_item_mask,"Value"]*1000/fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_stock_mask & fostat_methane_item_mask,"Value"]#/(faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Value"]*1000)
no_zero_mask = gleam_intake_df.loc[gleam_total_mask,"Value"]!=0
df_to_plot["Total_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_total_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
df_to_plot["Concentrate_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_variable_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
# df_to_plot.loc[df_to_plot["Concentrate_intake"]==0,"Concentrate_intake"]=1E-3
df_to_plot["Grass_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
# df_to_plot["Manure_intensity"]=fostat_manure_df.loc[fostat_manure_country_mask & fostat_manure_emissions_mask & fostat_manure_dairy_mask,"Value"]*1000/fostat_manure_df.loc[fostat_manure_country_mask & fostat_manure_stock_mask & fostat_manure_dairy_mask & fostat_manure_domain_mask,"Value"]
df_to_plot = df_to_plot.dropna()

df_to_plot["GAEZ"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"GAEZ"]

df_to_plot["Grass_intake_cat"] = np.round(df_to_plot["Grass_intake"])

df_to_plot["Grass_intake_cat"] = np.around(df_to_plot["Grass_intake"])
index_list = df_to_plot.index[df_to_plot['Grass_intake_cat'] == 14.].tolist()
df_to_plot.loc[index_list,"Grass_intake_cat"]=9.
index_list = df_to_plot.index[df_to_plot['Grass_intake_cat'] == 20.].tolist()
df_to_plot.loc[index_list,"Grass_intake_cat"]=9.

df_to_plot.drop(index=["Antigua and Barbuda"])
df_to_plot = df_to_plot.dropna()

df_to_plot.to_csv("output/data_dairy_for_lm.csv")

df_to_plot=pd.DataFrame(columns=["Methane_intensity","Meat_yield","Concentrate_intake","Grass_intake"])

gleam_herd_type_mask= gleam_intake_df["Herd type"]=="Non-dairy"

df_to_plot["Meat_yield"]=faostat_yield_df.loc[fostat_yield_country_mask & fostat_meat_element_mask & fostat_meat_item_mask,"Value"] #kg/year
df_to_plot.index=faostat_yield_df.loc[fostat_yield_country_mask & fostat_meat_element_mask & fostat_meat_item_mask,"Area"]
df_to_plot["Methane_intensity"]=fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_emissions_mask & fostat_methane_meat_item_mask,"Value"]*1000/fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_stock_mask & fostat_methane_meat_item_mask,"Value"]#/(faostat_yield_df.loc[fostat_yield_country_mask & fostat_meat_element_mask & fostat_meat_item_mask,"Value"]*1000)
df_to_plot["Concentrate_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_variable_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
df_to_plot["Grass_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
df_to_plot["Grass_intake_cat"] = np.round(df_to_plot["Grass_intake"])
df_to_plot["GAEZ"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"GAEZ"]
df_to_plot["Total_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_total_mask,"Value"]


df_to_plot.to_csv("output/data_non-dairy_for_lm.csv")

faostat_animal_df = read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")
poultry_meat_mask = faostat_animal_df["Item"]=="Meat, Poultry"
yield_mask = faostat_animal_df["Element"]=="Production"
eggs_mask = faostat_animal_df["Item"]=="Eggs Primary"
#country_mask = faostat_animal_df.loc[poultry_meat_mask & yield_mask & faostat_animal_df.loc[poultry_meat_mask & yield_mask,"Area"].isin(faostat_animal_df.loc[eggs_mask & yield_mask,"Area"]),"Area"]

df_poultry_meat=pd.concat([faostat_animal_df.loc[eggs_mask & yield_mask,"Area"].reset_index(drop=True),faostat_animal_df.loc[poultry_meat_mask & yield_mask,"Value"].reset_index(drop=True),
                         faostat_animal_df.loc[eggs_mask & yield_mask,"Value"].reset_index(drop=True)],ignore_index=True,axis=1)
df_poultry_meat.columns=["Country","Meat yield","Eggs"]
df_poultry_meat.index=df_poultry_meat["Country"]

df = read_FAOSTAT_df("data/GLEAM_Intake.csv",delimiter=";")
df.index=df["Country"]

poultry_mask=df["Species"]=="Chickens"
production_system_mask=df["Production system"]=="All systems"
herd_mask=df["Variable"]=="HERD: total number of animals"
grain_mask=df["Variable"]=="INTAKE: Total intake - Grains & Food crops"
country_mask=df["Country"].isin(list(df_poultry_meat["Country"]))

df_poultry_meat["Grain intake"] = df.loc[poultry_mask & production_system_mask & grain_mask,"Value"]
df_poultry_meat["Number animal"] = df.loc[poultry_mask & production_system_mask & herd_mask,"Value"]
df_poultry_meat["Grain intake rate"] = df.loc[poultry_mask & production_system_mask & grain_mask,"Value"]/df.loc[poultry_mask & production_system_mask & herd_mask,"Value"]
df_poultry_meat["Total"] = df_poultry_meat["Meat yield"]+df_poultry_meat["Eggs"]
df_poultry_meat["Total rate"] = df_poultry_meat["Total"]/df.loc[poultry_mask & production_system_mask & herd_mask,"Value"]
fig, ax = plt.subplots()
sns.regplot(x="Grain intake rate", y="Total rate", data=df_poultry_meat,ax=ax)
# ax.set_xlim(0,6E9)
# ax.set_ylim(0,3E6)
plt.savefig("output/fig_total_production_intake_rate_poultry.png")

from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

# from statsmodels.api import OLS
# OLS(np.array(df_poultry_meat["Total rate"]).reshape(-1, 1),np.array(df_poultry_meat["Grain intake rate"]).reshape(-1, 1)).fit().summary()

regr = linear_model.LinearRegression()
df_poultry_meat.dropna(inplace=True)
regr.fit(np.array(df_poultry_meat["Grain intake rate"]).reshape(-1, 1), np.array(df_poultry_meat["Total rate"]).reshape(-1, 1))
regr.score(np.array(df_poultry_meat["Grain intake rate"]).reshape(-1, 1), np.array(df_poultry_meat["Total rate"]).reshape(-1, 1))

reg_coef=pd.DataFrame(columns=["intercept","coef1"])
reg_coef.loc[1,"coef1"] = regr.coef_[0,0]
reg_coef.loc[1,"intercept"] = regr.intercept_[0]
reg_coef.to_csv("output/coef_total_production_grain_intake_poultry.csv")

df_poultry_meat["Meat share"]=df_poultry_meat["Meat yield"]/df_poultry_meat["Total"]
df_poultry_meat.to_csv("output/FAOSTAT_meat_eggs_intake_poultry.csv")

# total = regr.predict(np.array(df_poultry_meat["Grain intake"]).reshape(-1, 1))
# # The coefficients
# print('Coefficients: \n', regr.coef_)
# # The mean squared error
# print('Mean squared error: %.2f'
#       % mean_squared_error(df_poultry_meat["Total"], total))

df_non_dairy_meat=pd.DataFrame(columns=["Total intake","Number"])
df_non_dairy_meat["Total intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_total_mask,"Value"]
df_non_dairy_meat["Number"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_number_mask,"Value"]
faostat_yield_df = read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")
faostat_yield_df.index=faostat_yield_df["Area"]
production_mask = faostat_yield_df["Element"]=="Production"
df_non_dairy_meat["Production"] = faostat_yield_df.loc[fostat_yield_country_mask & production_mask & fostat_meat_item_mask,"Value"]
df_non_dairy_meat.to_csv("output/meat_intake_non_dairy.csv")
