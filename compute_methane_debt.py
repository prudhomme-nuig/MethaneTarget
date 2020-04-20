#! /bin/python

import pandas as pd
import numpy as np
from common_data import read_FAOSTAT_df

#Country in this study
country_list=["Brazil","France","India","Ireland"]
reference_year=2010

def compute_methane_debt(past_trend,year_list,target_year=reference_year):
    year_mask=year_list<=target_year
    methane_debt=np.sum(past_trend[year_mask])*0.1 #10% of methane long term effect
    return methane_debt 

methane_past_df=read_FAOSTAT_df('data/FAOSTAT_methane_past.csv',delimiter=',')
methane_pivot_df=pd.pivot(methane_past_df,columns='Area')

methane_debt_df=pd.DataFrame(columns=[])
for country in methane_pivot_df['Value'].columns:
    methane_past=methane_pivot_df['Value'][country][~np.isnan(methane_pivot_df['Value'][country])].values
    year_list=methane_pivot_df['Year'][country][~np.isnan(methane_pivot_df['Year'][country])].values
    methane_debt_country=compute_methane_debt(methane_past,year_list)
    methane_debt_df=pd.concat([methane_debt_df,pd.DataFrame(data={country: [methane_debt_country]})],axis=1)

total_methane_debt=np.sum(methane_debt_df.values)
methane_debt_df=methane_debt_df[country_list]/total_methane_debt
    
methane_debt_df.to_csv('output/FAOSTAT_methane_debt.csv',index=False)
