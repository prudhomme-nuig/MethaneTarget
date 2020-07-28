#!/usr/bin/env python

'''
Perform a Kruskal et Wallis test to know
if the AFOLU GWP and production in variant are signicantly different
'''
from scipy.stats import mstats
import pandas as pd
import numpy as np

df_all_variants=pd.DataFrame(columns=["Country","AFOLU balance (with eGWP*)","Allocation rule","Variant"])
for suffix_variant in ["_carbon+50","_carbon-50","_yield+50","_yield-50","_mitigation-50","_no_mitigation",""]:
    if suffix_variant=="":
        suffix_variant_name="main"
    else:
        suffix_variant_name=suffix_variant
    df_tmp=pd.read_csv("output/AFOLU_balance_2050"+suffix_variant+".csv")
    df_to_concat=pd.concat([df_tmp["Country"],df_tmp["AFOLU balance (with eGWP*)"],df_tmp["Allocation rule"],pd.DataFrame([suffix_variant_name.replace("_","")]*len(df_tmp["Total production"]),columns=['Variant'])],axis=1,sort=True)
    df_all_variants=pd.concat([df_all_variants,df_to_concat],axis=0,sort=False)

rule_list=["Debt","Population","Protein","GDP"]
country_list=["Brazil","France","India","Ireland"]
test_dict={False:"No Significant differences",True:"Significant differences"}
group_dict={"carbon":["carbon+50","carbon-50"],"yield":["yield+50","yield-50"],"mitigation":["mitigation-50","nomitigation"]}
df_to_table=df_all_variants.pivot_table(values='AFOLU balance (with eGWP*)',columns=["Variant"],index=["Country","Allocation rule"],aggfunc=np.median)
df_to_table.to_excel("output/sensitivity_analysis_median.xlsx",index_label=None,float_format = "%0.3f")
df_for_test=df_all_variants.pivot(values=['AFOLU balance (with eGWP*)',"Allocation rule","Country"],columns="Variant")
df_result={}
for country in country_list:
    df_result_test={}
    for rule in rule_list:
        df_result_test[rule]=pd.DataFrame(columns=["H","Pvalue","Significant"],index=["carbon","yield","mitigation"])
        for group in ["carbon","yield","mitigation"]:
            group_list=group_dict[group]
            group_list.extend(["main"])
            country_mask=df_for_test["Country"][group_list[0]]==country
            rule_mask=df_for_test["Allocation rule"][group_list[0]]==rule
            country_rule_mask=country_mask & rule_mask
            df=df_for_test["AFOLU balance (with eGWP*)"][group_list][country_rule_mask]
            df=df.astype("float")
            H,pvalue = mstats.kruskalwallis(df[group_list])
            df_result_test[rule].loc[group,"H"]=H
            df_result_test[rule].loc[group,"Pvalue"]=pvalue
            df_result_test[rule].loc[group,"Significant"]=test_dict[pvalue < 0.05]
    df_result[country]=pd.concat(df_result_test,axis=0)
df_result=pd.concat(df_result,axis=0)
df_result.to_excel("output/sensitivity_analysis.xlsx",float_format = "%0.4f")
