#! /bin/python

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from common_methane import read_FAOSTAT_df

#Milk yield intensification
#milk_yield_max
def milk_yield_max(GAEZ):

    milk_yield_df=pd.read_csv("output/milk_intake_dairy.csv",sep=";",index_col=0)

    production_rate_nineth_quantile = milk_yield_df.loc[milk_yield_df["GAEZ"].str.contains(GAEZ),"Milk_yield"].quantile([0.9], interpolation='nearest').values[0]

    return production_rate_nineth_quantile

#compute_intake_for_yield_max
def intake_for_milk_yield_max(current_yield,GAEZ):

    milk_yield_max_value = milk_yield_max(GAEZ)

    coefficient_milk_yield_df=pd.read_csv("output/coefficients_milk_yield_concentrate_relation.csv",sep=",",index_col=0)

    concentrate_for_milk_yield_max = (milk_yield_max_value-current_yield)/coefficient_milk_yield_df.iloc[0,1]

    return concentrate_for_milk_yield_max

def EI_milk_yield(X,GAEZ):

    if GAEZ=="Temperate":

        GAEZ_coef= 0

    else:

        GAEZ_coef= 1

    coefficient_methane_intensity_df=pd.read_csv("output/coefficients_methane_intensity_concentrate_relation.csv",sep=",",index_col=0)

    methane_intensity= coefficient_methane_intensity_df.iloc[0,0] + coefficient_methane_intensity_df.iloc[0,1]*X + coefficient_methane_intensity_df.iloc[0,2]*X**2 + coefficient_methane_intensity_df.iloc[0,3]*GAEZ_coef

    return methane_intensity

#EI_for_milk_yield_max
def EI_change_for_milk_yield_max(concentrate_current,current_yield,GAEZ):

    intake_max = intake_for_milk_yield_max(current_yield,GAEZ)

    EI_th = EI_milk_yield(concentrate_current*1E-3,GAEZ)

    EI_change = EI_milk_yield(intake_max,GAEZ)/EI_th

    return EI_change

#-------------------------------------------------------------------------------
#Cattle meat yield intensificaation
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

    production_rate_nineth_quantile = growth_rate_df.loc[growth_rate_df["GAEZ"].str.contains(GAEZ),"Production_rate"].quantile([0.9], interpolation='nearest').values[0]

    return production_rate_nineth_quantile

def intake_for_growth_rate_max(current_yield,GAEZ):

    growth_rate_max_value=growth_rate_max(GAEZ)

    coefficient_carcass_weight_df=pd.read_csv("output/coefficients_weight_intake_no_dairy_relation.csv",sep=",",index_col=0)

    concentrate_for_growth_rate_max = (growth_rate_max_value-current_yield)/coefficient_carcass_weight_df.iloc[0,1]

    return concentrate_for_growth_rate_max

def EI_meat_non_dairy(X,GAEZ):

    if GAEZ=="Temperate":

        GAEZ_coef= 0

    else:

        GAEZ_coef= 1

    coefficient_methane_intensity_df=pd.read_csv("output/coefficients_weight_intake_no_dairy_relation.csv",sep=",",index_col=0)


    return coefficient_methane_intensity_df.iloc[0,0] + coefficient_methane_intensity_df.iloc[0,1]*X + coefficient_methane_intensity_df.iloc[0,2]*GAEZ_coef

def EI_change_for_meat_yield_max(concentrate_current,current_yield,GAEZ):

    intake_max = intake_for_growth_rate_max(current_yield,GAEZ)+concentrate_current

    EI_th = EI_meat_non_dairy(concentrate_current,GAEZ)

    EI_change = EI_meat_non_dairy(intake_max,GAEZ)/EI_th

    return EI_change

#Poultry meat
def weight_poultry_max():

    df_weight_poultry_gleam = pd.read_csv("output/poultry_meat_eggs_emission_intake.csv",sep=",",index_col=0)

    df_weight_poultry_gleam.dropna(inplace=True)

    df_weight_poultry_gleam["Meat yield"]=df_weight_poultry_gleam["Meat"]/df_weight_poultry_gleam["Number"]
    df_weight_poultry_gleam["Grain_intake_poultry_rate"]=df_weight_poultry_gleam["Grain_intake_poultry"]/df_weight_poultry_gleam["Number"]

    df_weight_poultry_gleam = df_weight_poultry_gleam.query("Grain_intake_poultry_rate <= 0.06")

    yield_nineth_quantile = df_weight_poultry_gleam["Meat yield"].quantile([0.9], interpolation='nearest').values[0]

    return yield_nineth_quantile

def intake_for_weight_poultry_max(current_yield):

    weight_poultry_max_value = weight_poultry_max()

    coefficient_weight_poultry_weight_df=pd.read_csv("output/coefficients_weight_intake_poultry_relation.csv",sep=",",index_col=0)

    concentrate_for_growth_rate_max = (weight_poultry_max_value-current_yield)/coefficient_weight_poultry_weight_df.iloc[0,1]

    return concentrate_for_growth_rate_max

#eggs
def eggs_poultry_max():

    df_eggs_poultry = pd.read_csv("output/poultry_meat_eggs_emission_intake.csv",sep=",",index_col=0)

    df_eggs_poultry.dropna(inplace=True)

    df_eggs_poultry["Eggs yield"] = df_eggs_poultry["Eggs"]/df_eggs_poultry["Number"]
    df_eggs_poultry["Grain_intake_poultry_rate"]=df_eggs_poultry["Grain_intake_poultry"]/df_eggs_poultry["Number"]

    df_eggs_poultry = df_eggs_poultry.query("Grain_intake_poultry_rate <= 0.06")

    total_production_nineth_quantile = df_eggs_poultry["Eggs yield"].quantile([0.9], interpolation='nearest').values[0]

    return total_production_nineth_quantile

def intake_for_eggs_poultry_max(current_yield):

    eggs_poultry_max_value = eggs_poultry_max()

    coefficient_eggs_poultry_weight_df=pd.read_csv("output/coefficients_eggs_intake_poultry_relation.csv",sep=",",index_col=0)

    concentrate_for_eggs_poultry_max = (eggs_poultry_max_value-current_yield)/coefficient_eggs_poultry_weight_df.iloc[0,1]

    return concentrate_for_eggs_poultry_max

#Swine
def weight_swine_max():

    df_weight_swine = pd.read_csv("output/pigs_meat_emission_intake.csv",sep=",",index_col=0)

    df_weight_swine.dropna(inplace=True)

    df_weight_swine["Meat yield"]=df_weight_swine["Meat"]/df_weight_swine["Number"]

    total_production_nineth_quantile = df_weight_swine["Meat yield"].quantile([0.9], interpolation='nearest').values[0]

    return total_production_nineth_quantile

def intake_for_weight_swine_max(current_yield):

    weight_swine_max_value = weight_swine_max()

    coefficient_swine_weight_df=pd.read_csv("output/coefficients_weight_intake_pigs_relation.csv",sep=",",index_col=0)

    concentrate_for_swine_max = (weight_swine_max_value-current_yield)/(coefficient_swine_weight_df.iloc[0,1])

    return concentrate_for_swine_max

#General changes
def methane_intensity_change(current_yield,current_intake,GAEZ,production,emission_type,concentrate_change=1,item="Dairy"):

    if emission_type=="enteric":

        if production=='Milk, Total':
            #Effect of intensification on enteric methane intensity of milk
            methane_intensity_change_value=EI_change_for_milk_yield_max(current_intake,current_yield,GAEZ)
        elif (production=='Beef and Buffalo Meat'):
            if "non-dairy" in item:
                methane_intensity_change_value=EI_change_for_meat_yield_max(current_intake,current_yield,GAEZ)
            else:
                methane_intensity_change_value=EI_change_for_milk_yield_max(current_intake,current_yield,GAEZ)
        else:
            #No effect of intensification on enteric methane intensity of poultry and pigs products
            methane_intensity_change_value=1
    elif emission_type=="manure":
        #No effect of intensification on methane intensity of manure
        methane_intensity_change_value= concentrate_change
    else:
        methane_intensity_change_value= 1
    return methane_intensity_change_value

def compute_yield_change(country,item,production,yields_df):
    yield_dict={'Milk, Total':'Yield','Beef and Buffalo Meat':'Yield/Carcass Weight','Meat, pig':'Yield/Carcass Weight','Meat, Poultry':'Yield/Carcass Weight','Eggs Primary':'Yield','Sheep and Goat Meat':'Yield/Carcass Weight'}
    climatic_region={"India":"Tropical","Brazil":"Tropical","Ireland":"Temperate","France":"Temperate"}
    #animal_yields_df=read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")
    #animal_yield_current=animal_yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==yield_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
    if (production=='Milk, Total'):
        # concentrate_for_milk_yield_max=intake_for_methane_intensity_max(climatic_region[country])
        yield_max=milk_yield_max(climatic_region[country])
        yields_df=pd.read_csv("output/data_for_lm.csv",delimiter=",")
        milk_yield_current=yields_df.loc[(yields_df["Area"]==country),"Milk_yield"].values[0]
        #milk_yield_current = yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==yield_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
        yield_change = np.max([yield_max/milk_yield_current,1])
    elif (production=='Beef and Buffalo Meat') & ("non-dairy" not in item):
        yield_change=1
    elif (production=='Beef and Buffalo Meat') & ("non-dairy" in item):
        yield_max=growth_rate_max(climatic_region[country])
        yield_current_df=pd.read_csv("output/meat_intake_non_dairy.csv",delimiter=";")
        #intake_rate_current=yield_current_df.loc[(yield_current_df["Area"]==country),"Total_intake"].values[0]/yield_current_df.loc[(yield_current_df["Area"]==country),"Number"].values[0]
        #current_theoretical_growth_rate=growth_rate(intake_rate_current,climatic_region[country])
        yield_current = yield_current_df.loc[(yield_current_df["Area"]==country),"Production"].values[0]/yield_current_df.loc[(yield_current_df["Area"]==country),"Number"].values[0]
        yields_FAOSTAT_df=read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")
        yields_FAOSTAT=yields_FAOSTAT_df.loc[(yields_FAOSTAT_df['Area']==country) & (yields_FAOSTAT_df['Element']==yield_dict[production]) & (yields_FAOSTAT_df['Item']==production),'Value'].values[0]
        time_growing=yields_FAOSTAT*1E3/yield_current
        max_yield_max=np.max(yields_FAOSTAT_df.loc[(yields_FAOSTAT_df['Element']==yield_dict[production]) & (yields_FAOSTAT_df['Item']==production),'Value'])
        yield_change=np.max([np.min([max_yield_max*1E3,growth_rate_max(climatic_region[country])*time_growing])/(yields_FAOSTAT*1E3),1])
        # if yields_FAOSTAT*yield_change/yields_FAOSTAT_df.loc[(yields_FAOSTAT_df['Element']==yield_dict[production]) & (yields_FAOSTAT_df['Item']==production),'Value'].quantile([0.95], interpolation='nearest').values[0]>1:
            # yield_change=np.max([1,yields_FAOSTAT_df.loc[(yields_FAOSTAT_df['Element']==yield_dict[production]) & (yields_FAOSTAT_df['Item']==production),'Value'].quantile([0.95], interpolation='nearest').values[0]/yields_FAOSTAT])
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
        # concentrate_for_meat_yield_max=intake_for_weight_swine_max(animal_yield_current)
        yield_max=weight_swine_max()
        yield_current_df=pd.read_csv("output/pigs_meat_emission_intake.csv",delimiter=",")
        meat_yield_current = yield_current_df.loc[(yield_current_df['Area']==country),'Meat'].values[0]/yield_current_df.loc[(yield_current_df['Area']==country),'Number'].values[0]
        yield_change = np.max([yield_max/meat_yield_current,1])
    else:
        # print("No change in yield for "+production)
        yield_change=1
    return yield_change

def compute_intake_change(country,item,production,yields_df):
    animal_producing_dict={'Milk, Total':'Yield','Beef and Buffalo Meat':'Yield/Carcass Weight','Meat, pig':'Yield/Carcass Weight','Meat, Poultry':'Yield/Carcass Weight','Eggs Primary':'Yield','Sheep and Goat Meat':'Yield/Carcass Weight'}
    climatic_region={"India":"Tropical","Brazil":"Tropical","Ireland":"Temperate","France":"Temperate"}
    animal_yields_df=read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")
    animal_yield_current=animal_yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==animal_producing_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
    if (production=='Milk, Total') | ((production=='Beef and Buffalo Meat') & ("non-dairy" not in item)):
        concentrate_for_milk_yield_max=intake_for_milk_yield_max(animal_yield_current,climatic_region[country])
        intake_current_df=pd.read_csv("output/data_for_lm.csv",delimiter=",")
        intake_rate_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Concentrate_intake"].values[0]
        # milk_yield_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Milk_yield"].values[0]
        output_ratio=milk_yield_max(climatic_region[country])/animal_yield_current
        #Some countries have smaller intake and higher meat yield than the maximum computed here
        if output_ratio>1:
            intake_change = np.max([concentrate_for_milk_yield_max/intake_rate_current,1])
        else:
            intake_change=1
    elif (production=='Beef and Buffalo Meat') & ("non-dairy" in item):
        intake_current_df=pd.read_csv("output/meat_intake_non_dairy.csv",delimiter=";")
        intake_rate_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Total_intake"].values[0]/intake_current_df.loc[(intake_current_df["Area"]==country),"Number"].values[0]
        meat_yield_current = intake_current_df.loc[(intake_current_df["Area"]==country),"Production"].values[0]/intake_current_df.loc[(intake_current_df["Area"]==country),"Number"].values[0]
        intake_for_yield_max=intake_for_growth_rate_max(meat_yield_current,climatic_region[country])+intake_rate_current
        time_growing=animal_yield_current*1E3/meat_yield_current
        max_yield_max=np.max(animal_yields_df.loc[(yields_df['Element']==animal_producing_dict[production]) & (yields_df['Item']==production),'Value'])
        output_ratio=np.min([max_yield_max*1E3,growth_rate_max(climatic_region[country])*time_growing])/(animal_yield_current*1E3)
        #Some countries have smaller intake and higher meat yield than the maximum computed here
        if output_ratio>1:
            intake_change = np.max([intake_for_yield_max/intake_rate_current,1])
        else:
            intake_change=1
    elif (production=='Eggs Primary') | (production=='Meat, Poultry'):
        if production=='Eggs Primary':
            concentrate_for_production_max=intake_for_eggs_poultry_max(animal_yield_current)
            intake_current_df=pd.read_csv("output/poultry_meat_eggs_emission_intake.csv",delimiter=",")
            intake_rate_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Grain_intake_poultry"].values[0]/intake_current_df.loc[(intake_current_df["Area"]==country),"Number"].values[0]
            # eggs_yield_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Eggs"].values[0]/intake_current_df.loc[(intake_current_df["Area"]==country),"Number"].values[0]
            output_ratio=eggs_poultry_max()/animal_yield_current
            # yield_max=eggs_poultry(concentrate_for_production_max,country)
        elif production=='Meat, Poultry':
            concentrate_for_production_max=intake_for_weight_poultry_max(animal_yield_current)
            intake_current_df=pd.read_csv("output/poultry_meat_eggs_emission_intake.csv",delimiter=",")
            intake_rate_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Grain_intake_poultry"].values[0]/intake_current_df.loc[(intake_current_df["Area"]==country),"Number"].values[0]
            # meat_yield_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Meat"].values[0]/intake_current_df.loc[(intake_current_df["Area"]==country),"Number"].values[0]
            output_ratio=weight_poultry_max()/animal_yield_current
        #Some countries have smaller intake and higher meat yield than the maximum computed here
        if output_ratio>1:
            intake_change = np.max([concentrate_for_production_max/intake_rate_current,1])
        else:
            intake_change=1

    elif production=='Meat, pig':
        intake_current_df=pd.read_csv("output/pigs_meat_emission_intake.csv",delimiter=",")
        intake_rate_current=intake_current_df.loc[(intake_current_df["Area"]==country),"Grain_intake"].values[0]/intake_current_df.loc[(intake_current_df["Area"]==country),"Number"].values[0]
        meat_yield_current = intake_current_df.loc[(intake_current_df['Area']==country),'Meat'].values[0]/intake_current_df.loc[(intake_current_df['Area']==country),'Number'].values[0]
        concentrate_for_production_max=intake_for_weight_swine_max(animal_yield_current)+intake_rate_current
        #Some countries have smaller intake and higher meat yield than the maximum computed here
        if weight_swine_max()/meat_yield_current>1:
            intake_change = np.max([concentrate_for_production_max/intake_rate_current,1])
        else:
            intake_change = 1
    else:
        # print("No change in yield for "+production)
        intake_change=1
    return intake_change
