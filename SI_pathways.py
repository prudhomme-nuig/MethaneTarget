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

def weight_gain(X,GAEZ):

    if GAEZ=="Temperate":

        GAEZ_coef= 0

    else:

        GAEZ_coef= 1

    coefficient_milk_yield_df=pd.read_csv("output/coefficients_milk_yield_concentrate_relation.csv",sep=",",index_col=0)

    milk_yield= np.exp(coefficient_milk_yield_df.iloc[0,0] + coefficient_milk_yield_df.iloc[0,1]*X + coefficient_milk_yield_df.iloc[0,2]*(X**2) +coefficient_milk_yield_df.iloc[0,3]*GAEZ_coef)

    return milk_yield

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
            methane_intensity=methane_intensity_milk_yield(X,GAEZ)
        elif (production=='Eggs Primary') | (production=='Meat, Poultry'):
            #No effect of intensification on enteric methane intensity of poultry products
            methane_intensity=1
        elif production=='Meat, pig':
            #No effect of intensification on enteric methane intensity of pig products
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

def methane_intensity_max(GAEZ):

    concentrate_for_methane_intensity_max = minimize(lambda x: -methane_intensity(x,GAEZ), 0)

    return concentrate_for_methane_intensity_max.x[0]

def weight_swine(X):

    coefficient_weight_df=pd.read_csv("output/coefficients_weight_intake_pigs_relation.csv",sep=",",index_col=0)

    return coefficient_weight_df.iloc[0,0] + coefficient_weight_df.iloc[0,1]*X.values[0]

def weight_swine_max():

    df_weight_swine = pd.read_csv("output/weight_intake_swine.csv",sep=",",index_col=0)

    df_weight_swine.dropna(inplace=True)

    total_production_nineth_quantile = df_weight_swine["Meat.per.head"].quantile([0.9], interpolation='nearest').values[0]

    return df_weight_swine.loc[df_weight_swine["Meat.per.head"]==total_production_nineth_quantile,"swine_grain"]


def weight_poultry(X,country):

    coefficient_weight_df=pd.read_csv("output/coefficients_weight_intake_poultry_relation.csv",sep=",",index_col=0)

    df_weight_poultry = pd.read_csv("output/FAOSTAT_meat_eggs_intake_poultry.csv",sep=",",index_col=0)

    meat_share = df_weight_poultry.loc[country,"Meat share"]

    return (coefficient_weight_df.iloc[0,0] + coefficient_weight_df.iloc[0,1]*X ) * meat_share

def eggs_poultry(X,country):

    coefficient_weight_df=pd.read_csv("output/coefficients_eggs_intake_poultry_relation.csv",sep=",",index_col=0)

    df_weight_poultry = pd.read_csv("output/FAOSTAT_meat_eggs_intake_poultry.csv",sep=",",index_col=0)

    meat_share = df_weight_poultry.loc[country,"Meat share"]

    return (coefficient_weight_df.iloc[0,0] + coefficient_weight_df.iloc[0,1]*X ) * (1 - meat_share)

def weight_poultry_max():

    df_weight_poultry = pd.read_csv("output/FAOSTAT_meat_eggs_intake_poultry.csv",sep=",",index_col=0)

    df_weight_poultry.dropna(inplace=True)

    total_production_nineth_quantile = df_weight_poultry["Meat yield"].quantile([0.9], interpolation='nearest').values[0]

    return df_weight_poultry.loc[df_weight_poultry["Meat yield"]==total_production_nineth_quantile,"Grain intake rate"].values[0]

def eggs_poultry_max():

    df_eggs_poultry = pd.read_csv("output/FAOSTAT_meat_eggs_intake_poultry.csv",sep=",",index_col=0)

    df_eggs_poultry.dropna(inplace=True)

    total_production_nineth_quantile = df_eggs_poultry["Eggs"].quantile([0.9], interpolation='nearest').values[0]

    return df_eggs_poultry.loc[df_eggs_poultry["Eggs"]==total_production_nineth_quantile,"Grain intake rate"].values[0]

def compute_yield_change(country,item,production,yields_df):
    yield_dict={'Milk, Total':'Yield','Beef and Buffalo Meat':'Yield/Carcass Weight','Meat, pig':'Yield/Carcass Weight','Meat, Poultry':'Yield/Carcass Weight','Eggs Primary':'Yield','Sheep and Goat Meat':'Yield/Carcass Weight'}
    climatic_region={"India":"Tropical","Brazil":"Tropical","Ireland":"Temperate","France":"Temperate"}
    yields_df=read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")
    if production=='Milk, Total':
        concentrate_for_milk_yield_max=milk_yield_max(climatic_region[country])
        yield_max=milk_yield(concentrate_for_milk_yield_max,climatic_region[country])
        milk_yield_current = yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==yield_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
        yield_change = np.max([yield_max/milk_yield_current,1])
    elif (production=='Eggs Primary') | (production=='Meat, Poultry'):
        if production=='Eggs Primary':
            concentrate_for_production_max=eggs_poultry_max()
            yield_max=eggs_poultry(concentrate_for_production_max,country)
        elif production=='Meat, Poultry':
            concentrate_for_production_max=weight_poultry_max()
            yield_max=eggs_poultry(concentrate_for_production_max,country)
        yield_current = yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==yield_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
        yield_change = np.max([yield_max/yield_current,1])
    elif production=='Meat, pig':
        concentrate_for_production_max=weight_swine_max()
        yield_max=weight_swine(concentrate_for_production_max)
        yield_current = yields_df.loc[(yields_df['Area']==country) & (yields_df['Element']==yield_dict[production]) & (yields_df['Item']==production),'Value'].values[0]
        yield_change = np.max([yield_max/yield_current,1])
    else:
        # print("No change in yield for "+production)
        yield_change=1
    return yield_change
# import numpy as np
# import os
# os.environ['R_HOME'] = 'C:\\Users\\prudhomme\\anaconda3\\Lib\\R\\'
# os.environ['R_USER'] = 'C:\\Users\\prudhomme\\anaconda3\\lib\\site-packages\\rpy2'
# os.environ['PYTHONPATH'] = 'C:\\Users\\prudhomme\\anaconda3\\lib\\site-packages'
# os.environ['PYTHONHOME'] = 'C:\\Users\\prudhomme\\anaconda3\\Python'
# import rpy2.robjects as robjects
# from rpy2.robjects import numpy2ri
# from rpy2.robjects.packages import importr
#
#
# # Constants
# MODEL_PATH = "output/milk_yield_concentrate.rds"
#
# r = robjects.r
# numpy2ri.activate()
#
# class Model(object):
#     """
#     R Model Loader
#
#     Attributes
#     ----------
#     model : R object
#     """
#
#     def __init__(self):
#         self.model = None
#
#     def load(self, path):
#         model_rds_path = "{}.rds".format(path)
#         model_dep_path = "{}.dep".format(path)
#
#         self.model = r.readRDS(model_rds_path)
#
#         with open(model_dep_path, "rt") as f:
#             model_dep_list = [importr(dep.strip())
#                               for dep in f.readlines()
#                               if dep.strip()!='']
#
#         return self
#
#     def predict(self, X):
#         """
#         Perform classification on samples in X.
#
#         Parameters
#         ----------
#         X : array, shape (n_samples, n_features)
#         Returns
#         -------
#         pred_probs : array, shape (n_samples, probs)
#         """
#
#         if self.model is None:
#             raise Exception("There is no Model")
#
#         if type(X) is not np.ndarray:
#             X = np.array(X)
#
#         pred = r.predict(self.model, X)
#         predlm = r.attr(pred, "predlm")
#
#         return np.array(predlm)
#
# model = Model()
# model.load(path="output/milk_yield_concentrate")
#
# d = {"Concentrate_intake": np.linspace(0,0.9),
#      "GAEZ": "Temperate"}
# dataf = robjects.DataFrame(d)
#
# prediction_temperate = model.predict(dataf)
#
# d = {"Concentrate_intake": np.linespace(),
#      "GAEZ": "Tropical"}
# dataf = robjects.DataFrame(d)
#
# prediction_tropical = model.predict(dataf)

# Example Input
#X = np.array([[5.1, 3.5,  1.4, 0.2], # setosa
#              [6.1, 2.6,  5.6, 1.4]]  # virginica

# Example Run
# model = Model().load(MODEL_PATH)
#pred = model.predict(X)


























# from common_data import read_FAOSTAT_df
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import statsmodels.api as sm
# import statsmodels.formula.api as smf
# import seaborn as sns
#
# gleam_intake_df = read_FAOSTAT_df("data/GLEAM_Intake.csv",delimiter=";")
# #gleam_intake_df = read_FAOSTAT_df("data/GLEAM_Intake_tropical_warm.csv",delimiter=",")
# faostat_yield_df = read_FAOSTAT_df("data/FAOSTAT_animal_yields.csv",delimiter="|")
# fostat_methane_df = read_FAOSTAT_df("data/FAOSTAT_enteric_fermentation.csv",delimiter="|")
#
# fostat_methane_df.loc[fostat_methane_df["Area"]=="United Kingdom of Great Britain and Northern Ireland","Area"] = "United Kingdom"
#
# fostat_methane_df.index=fostat_methane_df["Area"]
# gleam_intake_df.index=gleam_intake_df["Country"]
# gleam_intake_df.index.name="Area"
# faostat_yield_df.index=faostat_yield_df["Area"]
#
# country_list = list(set(gleam_intake_df["Country"]).intersection(set(faostat_yield_df["Area"])))
# country_list = list(set(country_list).intersection(set(fostat_methane_df["Area"])))
#
# #country_list.remove("Mongolia")
#
# fostat_yield_country_mask = faostat_yield_df["Area"].isin(country_list)
# fostat_yield_element_mask = faostat_yield_df["Element"]=="Yield"
# fostat_yield_item_mask = faostat_yield_df["Item"]=="Milk, Total"
# fostat_meat_item_mask = faostat_yield_df["Item"]=="Beef and Buffalo Meat"
# fostat_meat_element_mask = faostat_yield_df["Element"]=="Yield/Carcass Weight"
# fostat_methane_country_mask = fostat_methane_df["Area"].isin(country_list)
# fostat_methane_emissions_mask = fostat_methane_df["Element"]=="Emissions (CH4) (Enteric)"
# fostat_methane_stock_mask = fostat_methane_df["Element"]=="Stocks"
# fostat_methane_item_mask = fostat_methane_df["Item"]=="Cattle, dairy"
# fostat_methane_meat_item_mask = fostat_methane_df["Item"]=="Cattle"
# gleam_variable_mask = gleam_intake_df["Variable"].str.contains("INTAKE: Total intake - Grains")
# gleam_grass_mask = gleam_intake_df["Variable"].str.contains("INTAKE: Total intake - Roughages")
# gleam_total_mask = gleam_intake_df["Variable"]=="INTAKE: Total intake"
# gleam_number_mask = gleam_intake_df["Variable"]=="HERD: total number of animals"
# gleam_herd_type_mask= gleam_intake_df["Herd type"]=="Dairy"
# gleam_species_mask= gleam_intake_df["Species"]=="Cattle"
# gleam_country_mask= gleam_intake_df["Country"].isin(country_list)
#
# df_to_plot=pd.DataFrame(columns=["Methane_intensity","Milk_yield","Concentrate_intake"])
#
# df_to_plot["Milk_yield"]=faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Value"] #kg/year
# df_to_plot.index=faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Area"]
# df_to_plot["Methane_intensity"]=fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_emissions_mask & fostat_methane_item_mask,"Value"]*1000/fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_stock_mask & fostat_methane_item_mask,"Value"]#/(faostat_yield_df.loc[fostat_yield_country_mask & fostat_yield_element_mask & fostat_yield_item_mask,"Value"]*1000)
# no_zero_mask = gleam_intake_df.loc[gleam_total_mask,"Value"]!=0
# df_to_plot["Total_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_total_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
# df_to_plot=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_variable_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
# # df_to_plot.loc[df_to_plot["Concentrate_intake"]==0,"Concentrate_intake"]=1E-3
# df_to_plot["Grass_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
# df_to_plot = df_to_plot.dropna()
#
# df_to_plot["GAEZ"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"GAEZ"]
#
# # df_to_plot["Grass_intake_average"]=np.int64(df_to_plot["Grass_intake"])
# # df_to_plot["Concentrate_intake_2"]=df_to_plot["Concentrate_intake"]*df_to_plot["Concentrate_intake"]
# # df_to_plot["Conversion_rate"]=df_to_plot["Methane_intensity"]/df_to_plot["Total_intake"]*1E6
#
# # from linearmodels import PanelOLS
# # from linearmodels import RandomEffects
# #
# # exog_vars = ["Concentrate_intake"]
# # exog = sm.add_constant(df_to_plot[exog_vars])
# # mod = RandomEffects(data.clscrap, exog)
# # re_res = mod.fit()
# # print(re_res)
#
# df_to_plot["Grass_intake_cat"] = np.round(df_to_plot["Grass_intake"])
# # df_to_plot.to_csv("output/data_for_lm.csv")
# # #df_to_plot["Grass_intake"] = df_to_plot["Grass_intake"].astype("category")
# # md = smf.mixedlm("Methane_intensity ~ (1 | Grass_intake) + Concentrate_intake", df_to_plot, re_formula="1", groups=df_to_plot["Grass_intake"])
# # # md = sm.MixedLM(df_to_plot["Methane_intensity"],df_to_plot["Concentrate_intake"],exog_re=df_to_plot["Total_intake"])
# # mdf = md.fit()
# # print(mdf.summary())
#
#
# # re = mdf.cov_re.iloc[0,0]
# # likev = mdf.profile_re(0, 're',dist_low=0.5*re, dist_high=0.8*re)
# # plt.figure(figsize=(10,8))
# # plt.plot(likev[:,0], 2*likev[:,1])
# # plt.xlabel("Variance of random slope", size=17)
# # plt.ylabel("-2 times profile log likelihood", size=17)
#
# # df_to_plot = df_to_plot.drop(index=["Antigua and Barbuda","Guyana","Ecuador"])
# # df_to_plot["Grass_intake"] = df_to_plot["Grass_intake"].astype("category")
# # df_to_plot["Total_intake_cat"] = np.around(df_to_plot["Total_intake"])
# # index_list = df_to_plot.index[df_to_plot['Total_intake_cat'] == 2.].tolist()
# # df_to_plot.loc[index_list,"Total_intake_cat"]=3.
# # index_list = df_to_plot.index[df_to_plot['Total_intake_cat'] == 24.].tolist()
# # df_to_plot.loc[index_list,"Total_intake_cat"]=11.
# # index_list = df_to_plot.index[df_to_plot['Total_intake_cat'] == 17.].tolist()
# # df_to_plot.loc[index_list,"Total_intake_cat"]=11.
# df_to_plot["Grass_intake_cat"] = np.around(df_to_plot["Grass_intake"])
# index_list = df_to_plot.index[df_to_plot['Grass_intake_cat'] == 14.].tolist()
# df_to_plot.loc[index_list,"Grass_intake_cat"]=9.
# index_list = df_to_plot.index[df_to_plot['Grass_intake_cat'] == 20.].tolist()
# df_to_plot.loc[index_list,"Grass_intake_cat"]=9.
#
# df_to_plot.drop(index=["Antigua and Barbuda"])
# df_to_plot = df_to_plot.dropna()
#
# df_to_plot.to_csv("output/data_dairy_for_lm.csv")
#
# # fig = plt.figure()
# # ax1 = fig.add_subplot(121)
# # #df_to_plot.plot(ax=ax1,x="Total_intake", y=["Methane_intensity",], kind="scatter")
# # #df_to_plot.plot(ax=ax2, x="Concentrate_intake", y='Milk_yield',color='g',kind="scatter")
# # sns.lmplot(x="Concentrate_intake",y="Methane_intensity",data=df_to_plot, fit_reg=True,order=2) #,hue="GAEZ"
# # ax2 = fig.add_subplot(122)
# # sns.lmplot(x="Concentrate_intake",y="Milk_yield",data=df_to_plot,fit_reg=True,order=2)#,hue="GAEZ"
# # #ax1.set_ylabel('Methane intensity')
# # #ax1.set_ylabel('Milk_yield')
# # plt.show()
#
# # model = sm.formula.ols(formula='Methane_intensity ~ Concentrate_intake_2', data=df_to_plot)
# # res = model.fit()
# # print(res.summary())
# # model2 = sm.formula.ols(formula='Milk_yield ~ Concentrate_intake_2', data=df_to_plot)
# # res2 = model2.fit()
# # print(res2.summary())
# # plt.savefig("output/Methane_intensity_milk_yield_concentrate_share.png")
# # #plt.show()
#
# df_to_plot=pd.DataFrame(columns=["Methane_intensity","Meat_yield","Concentrate_intake","Grass_intake"])
#
# gleam_herd_type_mask= gleam_intake_df["Herd type"]=="Non-dairy"
#
# df_to_plot["Meat_yield"]=faostat_yield_df.loc[fostat_yield_country_mask & fostat_meat_element_mask & fostat_meat_item_mask,"Value"] #kg/year
# df_to_plot.index=faostat_yield_df.loc[fostat_yield_country_mask & fostat_meat_element_mask & fostat_meat_item_mask,"Area"]
# df_to_plot["Methane_intensity"]=fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_emissions_mask & fostat_methane_item_mask,"Value"]*1000/fostat_methane_df.loc[fostat_methane_country_mask & fostat_methane_stock_mask & fostat_methane_meat_item_mask,"Value"]#/(faostat_yield_df.loc[fostat_yield_country_mask & fostat_meat_element_mask & fostat_meat_item_mask,"Value"]*1000)
# df_to_plot["Concentrate_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_variable_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
# df_to_plot["Grass_intake"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"Value"]/gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_number_mask,"Value"]
# df_to_plot["Grass_intake_cat"] = np.round(df_to_plot["Grass_intake"])
# df_to_plot["GAEZ"]=gleam_intake_df.loc[gleam_country_mask & gleam_species_mask & gleam_herd_type_mask & gleam_grass_mask,"GAEZ"]
#
# # fig = plt.figure()
# # ax1 = fig.add_subplot(121)
# # # df_to_plot.plot(ax=ax1,x="Concentrate_intake", y=["Methane_intensity",], kind="scatter",trendline="lowess")
# # # df_to_plot.scatter(ax=ax2, x="Concentrate_intake", y='Milk_yield',color='g',kind="scatter",trendline="lowess")
# # sns.regplot(x="Concentrate_intake",y="Methane_intensity",data=df_to_plot, fit_reg=True,ax=ax1,order=1)
# # ax2 = fig.add_subplot(122)
# # sns.regplot(x="Concentrate_intake",y="Meat_yield",data=df_to_plot, fit_reg=True,ax=ax2,color="g",order=2)
# # ax1.set_ylabel('Methane_intensity')
# # ax2.set_ylabel('Meat_yield')
# # plt.show()
#
# df_to_plot.to_csv("output/data_non-dairy_for_lm.csv")
