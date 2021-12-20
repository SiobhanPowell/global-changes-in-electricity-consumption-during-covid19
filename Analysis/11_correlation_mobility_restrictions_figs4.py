import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from statsmodels.stats.outliers_influence import variance_inflation_factor

df1 = pd.read_csv('../Data/Intermediate/panel_data.csv', index_col=0)
df2 = pd.read_csv('../Data/Intermediate/panel_data_recovery.csv', index_col=0)

countries = list(set(df1['Country']))
df1['datetime'] = pd.to_datetime(df1['Date'])
df2['datetime'] = pd.to_datetime(df2['Date'])
df = pd.concat((df1, df2), axis=0)
df = df.sort_values(by=['Country', 'datetime']).reset_index(drop=True)

all_countries = pd.DataFrame(np.zeros((6, len(countries))), index=['Mobility: Retail and Recreation', 'Mobility: Residences',
       'Mobility: Workplaces', 'Mobility: Transit Stations',
       'Mobility: Grocery and Pharmacy', 'Mobility: Parks'], columns=countries)
all_countries_initial = all_countries.copy(deep=True)
all_countries_recovery = all_countries.copy(deep=True)
for country in countries:
    inds = df[df['Country']==country].index
    corr = df.loc[inds, ['Oxford', 'Mobility: Retail and Recreation', 'Mobility: Residences', 'Mobility: Workplaces', 'Mobility: Transit Stations', 'Mobility: Grocery and Pharmacy', 'Mobility: Parks']].corr()
    for key in all_countries.index:
        all_countries.loc[key, country] = corr.loc['Oxford', key]
    inds = df.loc[(df['Country']==country)&(df['datetime'].dt.month < 5)].index
    corr = df.loc[inds, ['Oxford', 'Mobility: Retail and Recreation', 'Mobility: Residences', 'Mobility: Workplaces', 'Mobility: Transit Stations', 'Mobility: Grocery and Pharmacy', 'Mobility: Parks']].corr()
    for key in all_countries.index:
        all_countries_initial.loc[key, country] = corr.loc['Oxford', key]
    inds = df.loc[(df['Country']==country)&(df['datetime'].dt.month >= 5)].index
    corr = df.loc[inds, ['Oxford', 'Mobility: Retail and Recreation', 'Mobility: Residences', 'Mobility: Workplaces', 'Mobility: Transit Stations', 'Mobility: Grocery and Pharmacy', 'Mobility: Parks']].corr()
    for key in all_countries.index:
        all_countries_recovery.loc[key, country] = corr.loc['Oxford', key]
        
# Plot results: Figure S4
plt.figure(figsize=(5, 5))
plt.subplot(211)
plt.title('Initial Period', fontname='Arial')
plt.boxplot(all_countries_initial, vert=False)
plt.xlim([-1,1])
plt.axvline(0, color='k', alpha=0.3, zorder=10)
plt.xticks([], fontname='Arial')
plt.yticks(np.arange(1,7), fontname='Arial', labels=['Retail and Recreation', 'Residences','Workplaces', 'Transit Stations', 'Grocery and Pharmacy', 'Parks'])
plt.subplot(212)
plt.boxplot(all_countries_recovery, vert=False)
plt.xlim([-1,1])
plt.axvline(0, color='k', alpha=0.3, zorder=10)
plt.title('Recovery Period', fontname='Arial')
plt.xlabel('Correlation with Stringency Index', fontname='Arial')
plt.yticks(np.arange(1,7), fontname='Arial', labels=['Retail and Recreation', 'Residences','Workplaces', 'Transit Stations', 'Grocery and Pharmacy', 'Parks'])
plt.tight_layout()
plt.savefig('../Figures/figs4_SI_correlation_restrictions_mobility.pdf', bbox_inches='tight')
plt.show()