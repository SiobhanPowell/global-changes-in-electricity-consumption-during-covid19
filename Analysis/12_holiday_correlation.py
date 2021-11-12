import pandas as pd
import os
import numpy as np
from scipy import stats

os.chdir('..')
df_init = pd.read_csv('Data/Intermediate/panel_data.csv', index_col=0)
df_recov = pd.read_csv('Data/Intermediate/panel_data_recovery.csv', index_col=0)

res = pd.DataFrame({'Country':list(set(df_init['Country']))})
for i in res.index:
    subset1 = df_init.loc[df_init['Country']==res.loc[i, 'Country']]
    subset2 = df_recov.loc[df_recov['Country']==res.loc[i, 'Country']]
    res.loc[i, 'Min'] = min(subset1['Pct Change in Electricity Demand'].min(), subset2['Pct Change in Electricity Demand'].min())
    res.loc[i, 'Holiday Effect'] = subset1['Holiday Effect'].min()
    
print('Results with Pandas:')
print(res.corr().loc['Holiday Effect'])
print('------'*10)

print('Scipy:')
print(stats.pearsonr(res['Min'].values, res['Holiday Effect'].values))
print('------'*10)