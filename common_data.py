#! /bin/python

import pandas as pd

convert_unit_dict={'1000 Head':1E3, #in Head
                    'hg/An':1E-4, #in tonne/an
                    '100mg/An':1E-7, #in t/an
                    'gigagrams':1E3, #in t
                    'g CH4/m2':1E-2, #in t/ha
                    'ha':1, #in ha
                    'Head':1, #in head
                    'tonnes':1,
                    '0.1g/An':1E-7, #in t/an
                    'kg DM':1E-3, #in t DM
                    '1000 tonnes':1E3, #in t
                    'kg DM/head':1E-3, # in t DM/head
                    'hg/ha':1E-4, #in t/ha
                    't/ha':1,
                    't/Head':1,
                    't':1,
                    'Head':1,
                    'tCH4/ha':1,
                    'kgCH4/head':1E-3,
                    '1000 ha':1E3,
                    'kg N2O-N/kg N':(14.*2+16.)/14.,
                    'kg':1E-3,
                    'kg/ha':1E-3,
                    'kg of nutrients':1E-3,
                    "g/capita/day":1E-6,
                    "tonnes CO2/ha":1,
                    "tN/ha":1,
                    "kg CH4/head":1E-3
                    }

new_unit_dict={'1000 Head':'Head', #in Head
                    'hg/An':'t', #in tonne/an
                    '100mg/An':'t', #in t/an
                    'gigagrams':'t', #in t
                    'g CH4/m2':'tCH4/ha', #in t/ha
                    'ha':'ha', #in ha
                    'Head':'Head', #in head
                    'tonnes':'t',
                    '0.1g/An':'t', #in t/an
                    'kg DM':'t', #in t DM
                    '1000 tonnes':'t', #in t
                    'kg DM/head':'t/Head', # in t DM/head
                    'hg/ha':'t/ha', #in t/ha
                    'kgCH4/head':'tCH4/Head',
                    '1000 ha':'ha',
                    'kg N2O-N/kg N':'t N2O/t N',
                    'kg':'t',
                    'kg/ha':'t/ha',
                    'kg of nutrients':'t',
                    "g/capita/day":'t',
                    't':'t',
                    "tonnes CO2/ha":"t CO2/ha",
                    "tN/ha":"tN/ha",
                    "kg CH4/head":'tCH4/Head'
                    }

def read_FAOSTAT_df(file_name,convert_unit_dict=convert_unit_dict,delimiter=",",index_col=None):
    df=pd.read_csv(file_name,delimiter=delimiter,index_col=index_col)
    unit_list=df['Unit'].dropna().unique()
    for unit in unit_list:
        if unit not in convert_unit_dict.keys():
            print(unit+' missing')
        else:
            df.loc[df['Unit']==unit,'Value']=df.loc[df['Unit']==unit,'Value'].values*convert_unit_dict[unit]
            df.loc[df['Unit']==unit,'Unit']=new_unit_dict[unit]
    return df
