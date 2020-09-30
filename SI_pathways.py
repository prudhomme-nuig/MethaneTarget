#! /bin/python

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from common_methane import read_FAOSTAT_df

def milk_yield(X,GAEZ):

    if GAEZ=="Temperate":

        GAEZ_coef= 0

    else:

        GAEZ_coef= 1

    coefficient_milk_yield_df=pd.read_csv("output/coefficients_milk_yield_concentrate_relation.csv",sep=",",index_col=0)

    milk_yield= np.exp(coefficient_milk_yield_df.iloc[0,0] + coefficient_milk_yield_df.iloc[0,1]*X + coefficient_milk_yield_df.iloc[0,2]*(X**2) +coefficient_milk_yield_df.iloc[0,3]*GAEZ_coef)

    return milk_yield

def growth_rate(X,GAEZ):

    if GAEZ=="Temperate":

        GAEZ_coef= 0

    else:

        GAEZ_coef= 1

    coefficient_carcass_weight_df=pd.read_csv("output/coefficients_weight_intake_no_dairy_relation.csv",sep=",",index_col=0)

    growth_rate= coefficient_carcass_weight_df.iloc[0,0] + coefficient_carcass_weight_df.iloc[0,1]*X +coefficient_carcass_weight_df.iloc[0,2]*GAEZ_coef

    return growth_rate

def growth_rate_max(GAEZ):

    if GAEZ=="Temperate":

        GAEZ_coef= 0

    else:

        GAEZ_coef= 1

    coefficient_carcass_weight_df=pd.read_csv("output/coefficients_weight_intake_no_dairy_relation.csv",sep=",",index_col=0)

    growth_rate_df=pd.read_csv("output/meat_intake_non_dairy.csv",sep=";",index_col=0)

    growth_rate_df["Production_rate"]=growth_rate_df["Production"]/growth_rate_df["Number"]
    growth_rate_df["Total_intake_rate"]=growth_rate_df["Total_intake"]/growth_rate_df["Number"]
    growth_rate_df.loc[growth_rate_df["Number"]>0,"Production_rate"]=growth_rate_df.loc[growth_rate_df["Number"]>0,"Production"]/growth_rate_df.loc[growth_rate_df["Number"]>0,"Number"]

    production_rate_nineth_quantile = growth_rate_df["Production_rate"].quantile([0.9], interpolation='nearest').values[0]

    intake_rate_nineth_quantile = growth_rate_df.loc[growth_rate_df["Production_rate"]==production_rate_nineth_quantile,"Total_intake_rate"].values[0]

    growth_rate= coefficient_carcass_weight_df.iloc[0,0] + coefficient_carcass_weight_df.iloc[0,1]*intake_rate_nineth_quantile +coefficient_carcass_weight_df.iloc[0,2]*GAEZ_coef

    return growth_rate

def intake_for_growth_rate_max(GAEZ):

    growth_rate_df=pd.read_csv("output/meat_intake_non_dairy.csv",sep=";",index_col=0)

    growth_rate_df["Production_rate"]=growth_rate_df["Production"]/growth_rate_df["Number"]
    growth_rate_df["Total_intake_rate"]=growth_rate_df["Total_intake"]/growth_rate_df["Number"]
    growth_rate_df.loc[growth_rate_df["Number"]>0,"Production_rate"]=growth_rate_df.loc[growth_rate_df["Number"]>0,"Production"]/growth_rate_df.loc[growth_rate_df["Number"]>0,"Number"]

    production_rate_nineth_quantile = growth_rate_df["Production_rate"].quantile([0.9], interpolation='nearest').values[0]

    intake_rate_nineth_quantile = growth_rate_df.loc[growth_rate_df["Production_rate"]==production_rate_nineth_quantile,"Total_intake_rate"].values[0]

    return intake_rate_nineth_quantile

def methane_intensity_milk_yield(X,GAEZ):

    if GAEZ=="Temperate":

        GAEZ_coef= 0

    else:

        GAEZ_coef= 1

    coefficient_methane_intensity_df=pd.read_csv("output/coefficients_methane_intensity_concentrate_relation.csv",sep=",",index_col=0)

    methane_intensity= coefficient_methane_intensity_df.iloc[0,0] + coefficient_methane_intensity_df.iloc[0,1]*X + coefficient_methane_intensity_df.iloc[0,2]*X**2 + coefficient_methane_intensity_df.iloc[0,3]*GAEZ_coef

    return methane_intensity

def methane_intensity(X,GAEZ,production,emission_type,concentrate_change=1):

    if emission_type=="enteric":

        if production=='Milk, Total':
            #Effect of intensification on enteric methane intensity of milk
            methane_intensity=methane_intensity_milk_yield(X*1E-3,GAEZ)
        elif (production=='Beef and Buffalo Meat'):
            methane_intensity=methane_intensity_meat_non_dairy(X*1E3,GAEZ)*1E-3
        elif (production=='Eggs Primary') | (production=='Meat, Poultry') | (production=='Meat, pig'):
            #No effect of intensification on enteric methane intensity of poultry and pigs products
            methane_intensity=1
        else:
            #No effect of intensification on enteric methane intensity of Beef products
            print("No change in methane intensity of for "+production)
            methane_intensity=1
    elif emission_type=="manure":
        #No effect of intensification on methane intensity of manure
        methane_intensity= concentrate_change
    else:
        methane_intensity= 1
    return methane_intensity


def milk_yield_max(GAEZ):

    concentrate_for_milk_yield_max = minimize(lambda x: -methane_intensity_milk_yield(x,GAEZ), 0.5)

    return concentrate_for_milk_yield_max.x[0]

def intake_for_milk_yield_max(GAEZ):

    concentrate_for_milk_yield_max = minimize(lambda x: -methane_intensity_milk_yield(x,GAEZ), 0.5)

    return concentrate_for_milk_yield_max.x[0]

def methane_intensity_max(GAEZ):

    concentrate_for_methane_intensity_max = minimize(lambda x: -methane_intensity_milk_yield(x,GAEZ), 0)

    return concentrate_for_methane_intensity_max.x[0]

def intake_for_methane_intensity_max(GAEZ):

    concentrate_for_methane_intensity_max = minimize(lambda x: -methane_intensity_milk_yield(x,GAEZ), 0)

    return concentrate_for_methane_intensity_max.x[0]

def methane_intensity_meat_non_dairy(X,GAEZ):

    if GAEZ=="Temperate":

        GAEZ_coef= 0

    else:

        GAEZ_coef= 1

    coefficient_methane_intensity_df=pd.read_csv("output/coefficients_weight_intake_no_dairy_relation.csv",sep=",",index_col=0)


    return coefficient_methane_intensity_df.iloc[0,0] + coefficient_methane_intensity_df.iloc[0,1]*X + coefficient_methane_intensity_df.iloc[0,2]*GAEZ_coef

def weight_swine(X):

    coefficient_weight_df=pd.read_csv("output/coefficients_weight_intake_pigs_relation.csv",sep=",",index_col=0)

    return coefficient_weight_df.iloc[0,0] + coefficient_weight_df.iloc[0,1]*X.values[0]

def weight_swine_max():

    df_weight_swine = pd.read_csv("output/pigs_meat_emission_intake.csv",sep=",",index_col=0)

    df_weight_swine.dropna(inplace=True)

    kg_to_t=1E-3

    df_weight_swine["Meat yield"]=df_weight_swine["Meat"]/df_weight_swine["Number"]

    total_production_nineth_quantile = df_weight_swine["Meat yield"].quantile([0.9], interpolation='nearest').values[0]

    return total_production_nineth_quantile*kg_to_t

def intake_for_weight_swine_max():

    df_weight_swine = pd.read_csv("output/pigs_meat_emission_intake.csv",sep=",",index_col=0)

    df_weight_swine.dropna(inplace=True)

    kg_to_t=1E-3

    df_weight_swine["Meat yield"]=df_weight_swine["Meat"]/df_weight_swine["Number"]
    df_weight_swine["Grain intake rate"]=df_weight_swine["Grain_intake"]/df_weight_swine["Number"]

    total_production_nineth_quantile = df_weight_swine["Meat yield"].quantile([0.9], interpolation='nearest').values[0]

    return df_weight_swine.loc[df_weight_swine["Meat yield"]==total_production_nineth_quantile,"Grain intake rate"]*kg_to_t

# def weight_poultry(X,country):
#
#     coefficient_weight_df=pd.read_csv("output/coefficients_weight_intake_poultry_relation.csv",sep=",",index_col=0)
#
#     df_weight_poultry = pd.read_csv("output/FAOSTAT_meat_eggs_intake_poultry.csv",sep=",",index_col=0)
#
#     meat_share = df_weight_poultry.loc[country,"Meat share"]
#
#     return (coefficient_weight_df.iloc[0,0] + coefficient_weight_df.iloc[0,1]*X ) * meat_share
#
# def eggs_poultry(X,country):
#
#     coefficient_weight_df=pd.read_csv("output/coefficients_eggs_intake_poultry_relation.csv",sep=",",index_col=0)
#
#     df_weight_poultry = pd.read_csv("output/FAOSTAT_meat_eggs_intake_poultry.csv",sep=",",index_col=0)
#
#     meat_share = df_weight_poultry.loc[country,"Meat share"]
#
#     return (coefficient_weight_df.iloc[0,0] + coefficient_weight_df.iloc[0,1]*X ) * (1 - meat_share)

def weight_poultry_max():

    df_weight_poultry_gleam = pd.read_csv("output/poultry_meat_eggs_emission_intake.csv",sep=",",index_col=0)

    df_weight_poultry_gleam.dropna(inplace=True)

    df_weight_poultry_gleam["Meat yield"]=df_weight_poultry_gleam["Meat"]/df_weight_poultry_gleam["Number"]
    df_weight_poultry_gleam["Grain_intake_poultry_rate"]=df_weight_poultry_gleam["Grain_intake_poultry"]/df_weight_poultry_gleam["Number"]

    df_weight_poultry_gleam = df_weight_poultry_gleam.query("Grain_intake_poultry_rate <= 0.06")

    yield_nineth_quantile = df_weight_poultry_gleam["Meat yield"].quantile([0.9], interpolation='nearest').values[0]

    return yield_nineth_quantile

def intake_for_weight_poultry_max():

    df_weight_poultry_gleam = pd.read_csv("output/poultry_meat_eggs_emission_intake.csv",sep=",",index_col=0)

    df_weight_poultry_gleam.dropna(inplace=True)

    df_weight_poultry_gleam["Meat yield"]=df_weight_poultry_gleam["Meat"]/df_weight_poultry_gleam["Number"]

    df_weight_poultry_gleam["Grain_intake_poultry_rate"]=df_weight_poultry_gleam["Grain_intake_poultry"]/df_weight_poultry_gleam["Number"]

    df_weight_poultry_gleam = df_weight_poultry_gleam.query("Grain_intake_poultry_rate <= 0.06")

    total_production_nineth_quantile = df_weight_poultry_gleam["Meat yield"].quantile([0.9], interpolation='nearest').values[0]

    return df_weight_poultry_gleam.loc[df_weight_poultry_gleam["Meat yield"]==total_production_nineth_quantile,"Grain_intake_poultry_rate"].values[0]

def eggs_poultry_max():

    df_eggs_poultry = pd.read_csv("output/poultry_meat_eggs_emission_intake.csv",sep=",",index_col=0)

    df_eggs_poultry.dropna(inplace=True)

    df_eggs_poultry["Eggs yield"] = df_eggs_poultry["Eggs"]/df_eggs_poultry["Number"]
    df_eggs_poultry["Grain_intake_poultry_rate"]=df_eggs_poultry["Grain_intake_poultry"]/df_eggs_poultry["Number"]

    df_eggs_poultry = df_eggs_poultry.query("Grain_intake_poultry_rate <= 0.06")

    total_production_nineth_quantile = df_eggs_poultry["Eggs yield"].quantile([0.9], interpolation='nearest').values[0]

    return total_production_nineth_quantile

def intake_for_eggs_poultry_max():

    df_eggs_poultry = pd.read_csv("output/poultry_meat_eggs_emission_intake.csv",sep=",",index_col=0)

    df_eggs_poultry.dropna(inplace=True)

    df_eggs_poultry["Eggs yield"] = df_eggs_poultry["Eggs"]/df_eggs_poultry["Number"]
    df_eggs_poultry["Grain_intake_poultry_rate"] = df_eggs_poultry["Grain_intake_poultry"]/df_eggs_poultry["Number"]

    df_eggs_poultry = df_eggs_poultry.query("Grain_intake_poultry_rate <= 0.06")

    total_production_nineth_quantile = df_eggs_poultry["Eggs yield"].quantile([0.9], interpolation='nearest').values[0]

    return df_eggs_poultry.loc[df_eggs_poultry["Eggs yield"]==total_production_nineth_quantile,"Grain_intake_poultry_rate"].values[0]

def compute_yield_change(country,item,production,yields_df):
    yield_dict={'Milk, Total':'Yield','Beef and Buffalo Meat':'Yield/Carcass Weight','Meat, pig':'Yield/Carcass Weight','Meat, Poultry':'Yield/Carcass Weight','Eggs Primary':'Yield','Sheep and Goat Meat':'Yield/Carcass Weight'}
    climatic_region={"India":"Tropical","Brazil":"Tropical","Ireland":"Temperate","France":"Temperate"}
    yields_df=read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")
    if production=='Milk, Total':
        concentrate_for_milk_yield_max=intake_for_methane_intensity_max(climatic_region[country])
        yield_max=milk_yield(concentrate_for_milk_yield_max,climatic_region[country])
        milk_yield_current = yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==yield_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
        yield_change = np.max([yield_max/milk_yield_current,1])
    elif production=='Beef and Buffalo Meat':
        yield_max=growth_rate_max(climatic_region[country])
        yield_current_df=pd.read_csv("output/meat_intake_non_dairy.csv",delimiter=";")
        intake_rate_current=yield_current_df.loc[(yield_current_df["Area"]==country),"Total_intake"].values[0]/yield_current_df.loc[(yield_current_df["Area"]==country),"Number"].values[0]
        current_theoretical_growth_rate=growth_rate(intake_rate_current,climatic_region[country])
        # yield_current = yield_current_df.loc[(yield_current_df["Area"]==country),"Production"].values[0]/yield_current_df.loc[(yield_current_df["Area"]==country),"Number"].values[0]
        yield_change=np.max([yield_max/current_theoretical_growth_rate,1])
        # if production=='Beef and Buffalo Meat':
        # import pdb; pdb.set_trace()
    elif (production=='Eggs Primary') | (production=='Meat, Poultry'):
        if production=='Eggs Primary':
            yield_max=eggs_poultry_max()
            yield_current_df=pd.read_csv("output/poultry_meat_eggs_emission_intake.csv",delimiter=",")
            yield_current = yield_current_df.loc[(yield_current_df['Area']==country),'Eggs'].values[0]/yield_current_df.loc[(yield_current_df['Area']==country),'Number'].values[0]
            #yield_max=eggs_poultry(concentrate_for_production_max,country)
        elif production=='Meat, Poultry':
            yield_max=weight_poultry_max()
            #yield_max=eggs_poultry(concentrate_for_production_max,country)
            yield_current_df=pd.read_csv("output/poultry_meat_eggs_emission_intake.csv",delimiter=",")
            yield_current = yield_current_df.loc[(yield_current_df['Area']==country),'Meat'].values[0]/yield_current_df.loc[(yield_current_df['Area']==country),'Number'].values[0]
        yield_change = np.max([yield_max/yield_current,1])
    elif production=='Meat, pig':
        yield_max=weight_swine_max()
        #yield_max=weight_swine(concentrate_for_production_max)
        yield_current = yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==yield_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
        yield_change = np.max([yield_max/yield_current,1])
    else:
        # print("No change in yield for "+production)
        yield_change=1
    return yield_change

def compute_intake_change(country,item,production,yields_df):
    yield_dict={'Milk, Total':'Yield','Beef and Buffalo Meat':'Yield/Carcass Weight','Meat, pig':'Yield/Carcass Weight','Meat, Poultry':'Yield/Carcass Weight','Eggs Primary':'Yield','Sheep and Goat Meat':'Yield/Carcass Weight'}
    climatic_region={"India":"Tropical","Brazil":"Tropical","Ireland":"Temperate","France":"Temperate"}
    # yields_df=read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")
    if production=='Milk, Total':
        concentrate_for_milk_yield_max=intake_for_methane_intensity_max(climatic_region[country])
        intake_current_df=pd.read_csv("output/data_for_lm.csv",delimiter=",")
        intake_rate_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Concentrate_intake"].values[0]
        intake_change = np.max([concentrate_for_milk_yield_max/intake_rate_current,1])
    elif production=='Beef and Buffalo Meat':
        intake_for_yield_max=intake_for_growth_rate_max(climatic_region[country])
        intake_current_df=pd.read_csv("output/meat_intake_non_dairy.csv",delimiter=";")
        intake_rate_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Total_intake"].values[0]/intake_current_df.loc[(intake_current_df["Area"]==country),"Number"].values[0]
        # current_theoretical_growth_rate=growth_rate(intake_rate_current,climatic_region[country])
        # yield_current = yield_current_df.loc[(yield_current_df["Area"]==country),"Production"].values[0]/yield_current_df.loc[(yield_current_df["Area"]==country),"Number"].values[0]
        intake_change=np.max([intake_for_yield_max/intake_rate_current,1])
    elif (production=='Eggs Primary') | (production=='Meat, Poultry'):
        if production=='Eggs Primary':
            concentrate_for_production_max=intake_for_eggs_poultry_max()
            intake_current_df=pd.read_csv("output/poultry_meat_eggs_emission_intake.csv",delimiter=",")
            intake_rate_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Grain_intake_poultry"].values[0]/intake_current_df.loc[(intake_current_df["Area"]==country),"Number"].values[0]
            # yield_max=eggs_poultry(concentrate_for_production_max,country)
        elif production=='Meat, Poultry':
            concentrate_for_production_max=intake_for_weight_poultry_max()
            intake_current_df=pd.read_csv("output/poultry_meat_eggs_emission_intake.csv",delimiter=",")
            intake_rate_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Grain_intake_poultry"].values[0]/intake_current_df.loc[(intake_current_df["Area"]==country),"Number"].values[0]
        intake_change = np.max([concentrate_for_production_max/intake_rate_current,1])
    elif production=='Meat, pig':
        concentrate_for_production_max=intake_for_weight_swine_max()
        intake_current_df=pd.read_csv("output/meat_intake_non_dairy.csv",delimiter=";")
        intake_rate_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Total_intake"].values[0]/intake_current_df.loc[(intake_current_df["Area"]==country),"Number"].values[0]
        intake_change = np.max([concentrate_for_production_max.values[0]/intake_rate_current,1])
    else:
        # print("No change in yield for "+production)
        intake_change=1
    return intake_change
