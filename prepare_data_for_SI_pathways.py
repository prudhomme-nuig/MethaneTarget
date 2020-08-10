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
df_to_plot["Methane_intensity"]=fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_emissions_mask & fostat_methane_item_mask,"Value"]*1000/fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_stock_mask & fostat_methane_meat_item_mask,"Value"]#/(faostat_yield_df.loc[fostat_yield_country_mask & fostat_meat_element_mask & fostat_meat_item_mask,"Value"]*1000)
df_to_plot["Concentrate_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_variable_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
df_to_plot["Grass_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
df_to_plot["Grass_intake_cat"] = np.round(df_to_plot["Grass_intake"])
df_to_plot["GAEZ"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"GAEZ"]

df_to_plot.to_csv("output/data_non-dairy_for_lm.csv")
