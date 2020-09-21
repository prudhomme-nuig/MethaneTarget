#! /bin/python

'''
Compute impacts of national methane quotas
on the AFOLU balance
'''

import pandas as pd
import numpy as np
from common_data import read_FAOSTAT_df
from common_methane import compute_CO2_equivalent
from copy import deepcopy
import argparse

parser = argparse.ArgumentParser('Compute impacts of different national methane quotas on AFOLU balance...')
parser.add_argument('--sensitivity-analysis', help='Yields can be +50 or -50')
parser.add_argument('--print-table', action='store_true', help='Print tables used in the methane paper and ')
parser.add_argument('--mitigation',  help='Change mitigation option')
parser.add_argument('--carbon',  help='Change mitigation option')

args = parser.parse_args()

#Option for sensitivity analysis: change yield of +50% or -50%
if args.sensitivity_analysis is not None:
    yield_change=float(args.sensitivity_analysis)/100.
    file_name_suffix='_yield'+args.sensitivity_analysis
else:
    yield_change=0
    file_name_suffix=''

#Option with an increased mitigation aplied in 2050 for N2O and methane
if args.mitigation is not None:
    activity_df=pd.read_csv("output/activity_2050_mitigation"+args.mitigation+".csv")
    file_name_suffix+="_mitigation"+args.mitigation
else:
    activity_df=pd.read_csv("output/activity_2050.csv")
    file_name_suffix+=''

if args.carbon is not None:
    file_name_suffix+="_carbon"+args.carbon
else:
    file_name_suffix+=""

country_list=["Brazil","France","India","Ireland"]

ponderation_dict={}
ponderation_dict['Population']=pd.read_csv('data/WB_population_reference.csv',delimiter=',')
ponderation_dict['GDP']=pd.read_csv('data/WB_GDP_reference.csv',delimiter=',')
ponderation_grand_parenting_df=pd.read_csv('data/FAOSTAT_methane_past.csv',delimiter=',')
ponderation_dict['Grand-parenting']=None
ponderation_dict['Debt']=pd.read_csv('output/FAOSTAT_methane_debt.csv',delimiter=',')
ponderation_dict['Protein']=pd.read_csv('output/FAOSTAT_protein_production.csv',delimiter=',',index_col=0)


activity_df=pd.read_csv("output/impact_2050"+file_name_suffix+".csv",index_col=0)
GWP_N2O=298
GWP100_CH4=34
t_to_kt=1E-3

#Read methane Debt
methane_debt_df=pd.read_csv("output/FAOSTAT_methane_debt_value.csv")

activity_df['GWP N2O manure']=activity_df['N2O manure']*GWP_N2O
activity_df['GWP N2O fert']=activity_df['N2O fert']*GWP_N2O
activity_df['GWP N2O manure 2010']=activity_df['N2O manure 2010']*GWP_N2O
activity_df['GWP N2O fert 2010']=activity_df['N2O fert 2010']*GWP_N2O
activity_df['Total CO2 emissions']=-activity_df['Total offset']
activity_df['Total CO2 emissions 2010']=0
activity_df['International Feed offset 2010']=0
activity_df['National quota eGWP*']=np.nan
activity_df['National quota GWP*']=np.nan
activity_df['National quota GWP100']=np.nan
for country in country_list:
    for rule in np.unique(activity_df['Allocation rule']):
        country_rule_mak=(activity_df['Allocation rule']==rule) & (activity_df['Country']==country)
        activity_df.loc[country_rule_mak,'National quota eGWP*']=compute_CO2_equivalent(activity_df.loc[country_rule_mak,'National quota'],rule,activity_df.loc[country_rule_mak,'2010']*activity_df.loc[country_rule_mak,'Share'],country,ponderation_in_GWP_star=ponderation_dict[rule],methane_debt=methane_debt_df)
        activity_df.loc[country_rule_mak,'National quota GWP*']=compute_CO2_equivalent(activity_df.loc[country_rule_mak,'National quota'],'Grand-parenting',activity_df.loc[country_rule_mak,'National 2010'],country,ponderation_in_GWP_star=ponderation_dict[rule],methane_debt=methane_debt_df)
        activity_df.loc[country_rule_mak,'National quota GWP100']=compute_CO2_equivalent(activity_df.loc[country_rule_mak,'National quota'],'GWP100',activity_df.loc[country_rule_mak,'National 2010'],country,ponderation_in_GWP_star=ponderation_dict[rule],methane_debt=methane_debt_df)
        activity_df.loc[country_rule_mak,'National quota GWP* 2010']=0
        activity_df.loc[country_rule_mak,'National quota eGWP* 2010']=compute_CO2_equivalent(activity_df.loc[country_rule_mak,'National 2010'],rule,activity_df.loc[country_rule_mak,'2010'],country,ponderation_in_GWP_star=ponderation_dict[rule],methane_debt=methane_debt_df)
        activity_df.loc[country_rule_mak,'National quota GWP100 2010']=activity_df.loc[country_rule_mak,'National 2010']*GWP100_CH4
        if rule=='Grand-parenting':
            activity_df.loc[country_rule_mak,'Biogenic reference CH4 emissions in 2010 (ktCH4)']=activity_df.loc[country_rule_mak,'National 2010']
        elif rule=='GDP':
            activity_df.loc[country_rule_mak,'Biogenic reference CH4 emissions in 2010 (ktCH4)']=((-activity_df.loc[country_rule_mak,'National quota']+np.maximum(activity_df.loc[country_rule_mak,'National 2010'],-activity_df.loc[country_rule_mak,'Share']*(activity_df.loc[country_rule_mak,'2050']-activity_df.loc[country_rule_mak,'2010'])))/activity_df.loc[country_rule_mak,'Share']+activity_df.loc[country_rule_mak,'2050'])/activity_df.loc[country_rule_mak,'2050']*activity_df.loc[country_rule_mak,'National quota']
        elif rule=='Population':
            activity_df.loc[country_rule_mak,'Biogenic reference CH4 emissions in 2010 (ktCH4)']=activity_df.loc[country_rule_mak,'2010']*ponderation_dict[rule][ponderation_dict[rule]['Country Name']==country]['2010'].values[0]/ponderation_dict[rule][ponderation_dict[rule]['Country Name']=='World']['2010'].values[0]
        elif rule=='Protein':
            activity_df.loc[country_rule_mak,'Biogenic reference CH4 emissions in 2010 (ktCH4)']=activity_df.loc[country_rule_mak,'2010']*ponderation_dict[rule][country].values[0]

activity_df['Biogenic CH4 target 2050 (ktCH4)']=activity_df['National quota']
activity_df['Biogenic CH4 change in 2050 (%)']=100-activity_df['National quota']/activity_df['Biogenic reference CH4 emissions in 2010 (ktCH4)']*100

table_ref = pd.pivot_table(activity_df, values=['Biogenic reference CH4 emissions in 2010 (ktCH4)','Biogenic CH4 target 2050 (ktCH4)','Biogenic CH4 change in 2050 (%)'], index=['Country'],columns=["Allocation rule"],aggfunc='mean')
table_ref.loc[:,['Biogenic reference CH4 emissions in 2010 (ktCH4)','Biogenic CH4 target 2050 (ktCH4)']] = table_ref[['Biogenic reference CH4 emissions in 2010 (ktCH4)','Biogenic CH4 target 2050 (ktCH4)']]*t_to_kt
table_ref.to_excel("output/table_methane_reference.xlsx")

activity_df['AFOLU balance (with eGWP*)']=activity_df['National quota eGWP*']+activity_df['GWP N2O fert']+activity_df['GWP N2O manure']+activity_df['Total CO2 emissions']
activity_df['AFOLU balance (with GWP*)']=activity_df['National quota GWP*']+activity_df['GWP N2O fert']+activity_df['GWP N2O manure']+activity_df['Total CO2 emissions']
activity_df['AFOLU balance (with GWP100)']=activity_df['National quota GWP100']+activity_df['GWP N2O fert']+activity_df['GWP N2O manure']+activity_df['Total CO2 emissions']
activity_df['AFOLU balance 2010']=activity_df['National quota GWP* 2010']+activity_df['GWP N2O fert 2010']+activity_df['GWP N2O manure 2010']+activity_df['Total CO2 emissions 2010']
activity_df['AFOLU balance (with eGWP*) 2010']=activity_df['National quota eGWP* 2010']+activity_df['GWP N2O fert 2010']+activity_df['GWP N2O manure 2010']+activity_df['Total CO2 emissions 2010']
activity_df['AFOLU balance (with GWP*) 2010']=activity_df['National quota GWP* 2010']+activity_df['GWP N2O fert 2010']+activity_df['GWP N2O manure 2010']+activity_df['Total CO2 emissions 2010']
activity_df['AFOLU balance (with GWP100) 2010']=activity_df['National quota GWP100 2010']+activity_df['GWP N2O fert 2010']+activity_df['GWP N2O manure 2010']+activity_df['Total CO2 emissions 2010']


activity_df.to_csv("output/AFOLU_balance_2050"+file_name_suffix+".csv")

if args.print_table:
    column_name_to_variable_name_dict={"AFOLU balance (with eGWP*)":{'AFOLU balance (with eGWP*)':['AFOLU balance (with eGWP*)'],
                                                        'GWP N2O':['GWP N2O fert','GWP N2O manure'],
                                                        'GWP CH4':['National quota GWP*'],
                                                        'CO2 emissions':['Total CO2 emissions'],
                                                        'Net imported CO2 emissions from feed':['International Feed offset']},
                                        "AFOLU balance":{'AFOLU balance (with eGWP*)':['AFOLU balance (with eGWP*)'],
                                                        'AFOLU balance (with GWP*)':['AFOLU balance (with GWP*)'],
                                                        'AFOLU balance (with GWP100)':['AFOLU balance (with GWP100)']
                                                        }
                                        }

    from common_methane import print_table_results
    print_table_df=print_table_results(activity_df,country_list,column_name_to_variable_name_dict)
    print_table_df.to_csv("output/paper_table2"+file_name_suffix+".csv",sep=";",encoding="utf-8",decimal =",",float_format='%.3f')
