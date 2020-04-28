#! /bin/python

'''
Select the contry with the lowest Emission intensity per kg of protein of the animal product as a "model" country
or rice, take the highest yield
'''

import pandas as pd
from common_data import read_FAOSTAT_df

country_list=["France","Ireland","Brazil","India"]
country_in_same_GAEZ=pd.read_csv("output/country_in_same_GAEZ.csv",index_col=0)
country_emission_intensity_df=pd.read_csv("output/GLEAM_data_base_EI.csv",encoding="utf-8")

animal_name_dict={"Milk, Total":"Cattle","Beef and Buffalo Meat":"Cattle","Eggs Primary":"Chickens","Meat, Poultry":"Chickens","Sheep and Goat Meat":"Sheep","Meat, pig":"Pigs"}

model_country_pd=pd.DataFrame()
for country in country_list:
    country_mask=country_emission_intensity_df['Country'].isin(country_in_same_GAEZ[country])
    for item in animal_name_dict.keys():
        item_mask=country_emission_intensity_df["Species"]==animal_name_dict[item]
        if item=="Milk, Total":
            EI_mask=country_emission_intensity_df["Variable"].str.contains("milk")
        elif "Meat" in item:
            EI_mask=country_emission_intensity_df["Variable"].str.contains("meat")
        elif "Eggs" in item:
            EI_mask=country_emission_intensity_df["Variable"].str.contains("egss")
        index_best=country_emission_intensity_df.loc[country_mask & item_mask & EI_mask,"Baseline value"].idxmax(0)
        model_country_pd.loc[item,country]=country_emission_intensity_df.loc[index_best,"Country"]
model_country_pd.to_csv("output/model_country.csv")
