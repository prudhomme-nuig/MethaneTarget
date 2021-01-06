#! /bin/python

from common_data import read_FAOSTAT_df
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
import seaborn as sns

#Read data base
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

carcass_to_live_weight = 1./0.55

#Masks
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
gleam_grain_mask = gleam_intake_df["Variable"].str.contains("INTAKE: Total intake - Grains")
gleam_grass_mask = gleam_intake_df["Variable"].str.contains("INTAKE: Total intake - Roughages")
gleam_total_mask = gleam_intake_df["Variable"]=="INTAKE: Total intake"
gleam_number_mask = gleam_intake_df["Variable"]=="HERD: total number of animals"
gleam_herd_type_mask= gleam_intake_df["Herd type"]=="Dairy"
gleam_non_dairy_mask= gleam_intake_df["Herd type"]=="Non-dairy"
gleam_non_dairy_mask= gleam_intake_df["Herd type"]=="Non-dairy"
gleam_species_mask= gleam_intake_df["Species"]=="Cattle"
gleam_chicken_mask= gleam_intake_df["Species"]=="Chickens"
gleam_pigs_mask= gleam_intake_df["Species"]=="Pigs"
gleam_country_mask= gleam_intake_df["Country"].isin(country_list)
gleam_production_mask = gleam_intake_df["Variable"]=="PROD: Meat - carcass weight"
gleam_milk_mask = gleam_intake_df["Variable"]=="PROD: Meat - carcass weight"
gleam_methane_enteric_mask = gleam_intake_df["Variable"]=="EMSS: Enteric - CH4 from enteric fermentation"
gleam_methane_manure_mask = gleam_intake_df["Variable"]=="EMSS: Manure - CH4 from manure management"
gleam_n2o_manure_mask = gleam_intake_df["Variable"]=="EMSS: Manure - N2O from manure management"
production_system_mask=gleam_intake_df["Production system"]=="All systems"
production_system_layers_mask=gleam_intake_df["Production system"]=="Layers"
gleam_eggs_mask = gleam_intake_df["Variable"]=="PROD: Eggs - shell weight"

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

# Prepare data per cohort
# Dairy cattle
kt_to_kg=1E6
df_dairy_milk=pd.DataFrame()
# df_dairy_milk["Milk_yield"]=faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Value"]
# df_dairy_milk["Total_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_total_mask,"Value"]*kt_to_kg
# df_dairy_milk["Concentrate_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_grain_mask,"Value"]*kt_to_kg
# df_dairy_milk["Number"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_number_mask,"Value"]*1000
# df_dairy_milk["Production"] = gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_production_mask,"Value"]*1E6
# df_dairy_milk["Methane"] = gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_methane_enteric_mask,"Value"]/29*1E6
# df_dairy_milk["GAEZ"] = gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_production_mask,"GAEZ"]
# df_dairy_milk = df_dairy_milk.dropna()
# df_dairy_milk = df_dairy_milk.drop(df_dairy_milk[df_dairy_milk["Number"]==0].index)
# df_dairy_milk.to_csv("output/milk_intake_dairy.csv",sep=";")
#
df_dairy_milk["Milk_yield"]=faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Value"] #kg/year
df_dairy_milk.index=faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Area"]
df_dairy_milk["Methane_intensity"]=fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_emissions_mask & fostat_methane_item_mask,"Value"]*1000/fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_stock_mask & fostat_methane_item_mask,"Value"]#/(faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Value"]*1000)
no_zero_mask = gleam_intake_df.loc[gleam_total_mask,"Value"]!=0
df_dairy_milk["Total_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_total_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
df_dairy_milk["Concentrate_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grain_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
# df_dairy_milk.loc[df_dairy_milk["Concentrate_intake"]==0,"Concentrate_intake"]=1E-3
df_dairy_milk["Grass_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
# df_dairy_milk["Manure_intensity"]=fostat_manure_df.loc[fostat_manure_country_mask & fostat_manure_emissions_mask & fostat_manure_dairy_mask,"Value"]*1000/fostat_manure_df.loc[fostat_manure_country_mask & fostat_manure_stock_mask & fostat_manure_dairy_mask & fostat_manure_domain_mask,"Value"]
df_dairy_milk = df_dairy_milk.dropna()

df_dairy_milk["GAEZ"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"GAEZ"]

df_dairy_milk["Grass_intake_cat"] = np.round(df_dairy_milk["Grass_intake"])

df_dairy_milk["Grass_intake_cat"] = np.around(df_dairy_milk["Grass_intake"])
index_list = df_dairy_milk.index[df_dairy_milk['Grass_intake_cat'] == 14.].tolist()
df_dairy_milk.loc[index_list,"Grass_intake_cat"]=9.
index_list = df_dairy_milk.index[df_dairy_milk['Grass_intake_cat'] == 20.].tolist()
df_dairy_milk.loc[index_list,"Grass_intake_cat"]=9.

df_dairy_milk.drop(index=["Antigua and Barbuda"])
df_dairy_milk = df_dairy_milk.dropna()

df_dairy_milk.to_csv("output/milk_intake_dairy.csv",sep=";")
#
#Non dairy cattle
kt_to_kg=1E6
df_non_dairy_meat=pd.DataFrame()
df_non_dairy_meat["Total_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_total_mask,"Value"]*kt_to_kg
df_non_dairy_meat["Concentrate_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_grain_mask,"Value"]*kt_to_kg
df_non_dairy_meat["Number"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_number_mask,"Value"]*1000
df_non_dairy_meat["Production"] = gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_production_mask,"Value"]*1E6
df_non_dairy_meat["Methane"] = gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_methane_enteric_mask,"Value"]/29*1E6
df_non_dairy_meat["GAEZ"] = gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_non_dairy_mask & gleam_production_mask,"GAEZ"]
df_non_dairy_meat = df_non_dairy_meat.dropna()
df_non_dairy_meat = df_non_dairy_meat.drop(df_non_dairy_meat[df_non_dairy_meat["Number"]==0].index)
df_non_dairy_meat.to_csv("output/meat_intake_non_dairy.csv",sep=";")

#Poultry
df_chicken=pd.DataFrame()
df_chicken["Grain_intake_poultry"]=gleam_intake_df.loc[gleam_country_mask & gleam_chicken_mask & production_system_mask & gleam_grain_mask,"Value"]
df_chicken["Total_intake_poultry"]=gleam_intake_df.loc[gleam_country_mask & gleam_chicken_mask & production_system_mask & gleam_total_mask,"Value"]
df_chicken["Grain_intake_layers"]=gleam_intake_df.loc[gleam_country_mask & gleam_chicken_mask & production_system_layers_mask & gleam_grain_mask,"Value"]
df_chicken["Total_intake_layers"]=gleam_intake_df.loc[gleam_country_mask & gleam_chicken_mask & production_system_layers_mask & gleam_total_mask,"Value"]
df_chicken["Number"]=gleam_intake_df.loc[gleam_country_mask & gleam_chicken_mask & production_system_mask & gleam_number_mask,"Value"]
df_chicken["Meat"] = gleam_intake_df.loc[gleam_country_mask & gleam_chicken_mask & production_system_mask & gleam_production_mask,"Value"]
df_chicken["Eggs"] = gleam_intake_df.loc[gleam_country_mask & gleam_chicken_mask & production_system_layers_mask & gleam_eggs_mask,"Value"]
df_chicken["CH4_manure"] = gleam_intake_df.loc[gleam_country_mask & gleam_chicken_mask & production_system_mask & gleam_methane_manure_mask,"Value"]
df_chicken["N2O_manure"] = gleam_intake_df.loc[gleam_country_mask & gleam_chicken_mask & production_system_mask & gleam_n2o_manure_mask,"Value"]
df_chicken["GAEZ"] = gleam_intake_df.loc[gleam_country_mask & gleam_chicken_mask & production_system_mask & gleam_production_mask,"GAEZ"]
df_chicken = df_chicken.dropna()
df_chicken = df_chicken.drop(df_chicken[df_chicken["Number"]==0].index)
df_chicken.to_csv("output/poultry_meat_eggs_emission_intake.csv")

#Pigs
df_pigs=pd.DataFrame()
df_pigs["Grain_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_pigs_mask & production_system_mask & gleam_grain_mask,"Value"]
df_pigs["Total_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_pigs_mask & production_system_mask & gleam_total_mask,"Value"]
df_pigs["Number"]=gleam_intake_df.loc[gleam_country_mask & gleam_pigs_mask & production_system_mask & gleam_number_mask,"Value"]
df_pigs["Meat"] = gleam_intake_df.loc[gleam_country_mask & gleam_pigs_mask & production_system_mask & gleam_production_mask,"Value"]
df_pigs["CH4_manure"] = gleam_intake_df.loc[gleam_country_mask & gleam_pigs_mask & production_system_mask & gleam_methane_manure_mask,"Value"]
df_pigs["N2O_manure"] = gleam_intake_df.loc[gleam_country_mask & gleam_pigs_mask & production_system_mask & gleam_n2o_manure_mask,"Value"]
df_pigs["GAEZ"] = gleam_intake_df.loc[gleam_country_mask & gleam_pigs_mask & production_system_mask & gleam_production_mask,"GAEZ"]
df_pigs = df_pigs.dropna()
df_pigs = df_pigs.drop(df_pigs[df_pigs["Number"]==0].index)
df_pigs.to_csv("output/pigs_meat_emission_intake.csv")
