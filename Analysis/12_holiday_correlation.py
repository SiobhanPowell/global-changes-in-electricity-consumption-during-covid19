import pandas as pd
import os
os.chdir('..')
df_init = pd.read_csv('Data/Intermediate/panel_data.csv', index_col=0)
df_recov = pd.read_csv('Data/Intermediate/panel_data_recovery.csv', index_col=0)

res_init = pd.DataFrame({'Country':list(set(df_init['Country']))})
for i in res_init.index:
    subset = df_init.loc[df_init['Country']==res_init.loc[i, 'Country']]
    res_init.loc[i, 'Min'] = subset['Pct Change in Electricity Demand'].min()
    res_init.loc[i, 'Mean'] = subset['Pct Change in Electricity Demand'].mean()
    res_init.loc[i, 'Holiday Effect'] = subset['Holiday Effect'].min()
    
print('Initial period:')
print(res_init.corr()['Holiday Effect'])
print('------'*10)
    
res_recov = pd.DataFrame({'Country':list(set(df_recov['Country']))})
for i in res_recov.index:
    subset = df_recov.loc[df_recov['Country']==res_recov.loc[i, 'Country']]
    res_recov.loc[i, 'Min'] = subset['Pct Change in Electricity Demand'].min()
    res_recov.loc[i, 'Mean'] = subset['Pct Change in Electricity Demand'].mean()
    res_recov.loc[i, 'Holiday Effect'] = subset['Holiday Effect'].min()
    
print('Recovery period:')
print(res_recov.corr()['Holiday Effect'])
print('------'*10)