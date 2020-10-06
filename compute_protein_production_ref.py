#! /bin/python

'''
Compute national protein production based on FAOSTAT data in 2010 to have an allocation rule of methane.
'''

import pandas as pd
import numpy as np
from common_data import read_FAOSTAT_df

#Country in this study
country_list=["Brazil","France","India","Ireland"]
reference_year=2010
item_list=['Bovine Meat','Mutton & Goat Meat','Pigmeat','Poultry Meat','Eggs','Milk - Excluding Butter','Rice (Milled Equivalent)','Butter, Ghee','Cream']

#Read protein supply
food_supply_df=read_FAOSTAT_df('data/FAOSTAT_protein_supply.csv',delimiter=',')

#Compute protein content
protein_content_df=pd.DataFrame(columns=item_list)
for item in item_list:
    protein_content_df.loc[0,item]=food_supply_df.loc[(food_supply_df['Item']==item) & (food_supply_df['Element']=='Protein supply quantity (g/capita/day)'),'Value'].values[0]/food_supply_df.loc[(food_supply_df['Item']==item) & (food_supply_df['Element']=='Food supply quantity (kg/capita/yr)'),'Value'].values[0]

#Read national production
production_df=read_FAOSTAT_df('data/FAOSTAT_production_FBS.csv',delimiter=',')

# Compute protein production
protein_production_df=pd.DataFrame(columns=country_list)
for country in np.unique(production_df['Area']):
    protein_production_df.loc[0,country]=0
    for item in item_list:
        production=production_df.loc[(production_df['Area']==country) & (production_df['Item']==item),'Value'].values[0]
        protein_production_df.loc[0,country]+=protein_content_df[item].values[0]*production

total_protein=np.sum(protein_production_df.values)
protein_production_df.to_csv("output/FAOSTAT_protein_production_2010.csv")
protein_production_df=protein_production_df[country_list]/total_protein

protein_production_df.to_csv('output/FAOSTAT_protein_production.csv')
