import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.cluster import KMeans
import matplotlib.dates as mdates
import datetime

# Collect all country/region data together
countries_and_regions = ['Bulgaria', 'United-Kingdom', 'Germany', 'Belgium', 'Greece', 'Slovakia', 'Italy', 'Lithuania', 'Portugal', 'Switzerland', 'Finland', 'Hungary', 'Croatia', 'Poland', 'Estonia', 'Netherlands', 'Slovenia', 'Norway', 'Denmark', 'Serbia', 'Romania', 'France', 'Ireland', 'Latvia', 'Austria', 'Sweden', 'Spain', 'Ukraine', 'Czech_Republic', 'India', 'Japan', 'Chile', 'Brazil', 'Russia', 'New_Zealand', 'British_Columbia', 'Ontario', 'Australia', 'Singapore', 'Mexico', 'Alberta', 'Region_MIDW', 'Region_CAR', 'Region_NE', 'Region_NW', 'Region_CENT', 'Region_TEN', 'Region_FLA', 'Region_CAL', 'Region_SE', 'Region_TEX', 'Region_NY', 'Region_MIDA']#, 'Region_SW'
# Names for plotting:
title_dict = {'Region_TEX':'US Texas', 'Region_CAL':'US California', 'Region_CAR':'US Carolinas', 'Region_CENT':'US Central', 
              'Region_FLA':'US Florida', 'Region_MIDA':'US Mid-Atlantic', 'Region_MIDW':'US Midwest', 'Region_NE':'US New England', 'Region_NW':'US Northwest', 'Region_NY':'US New York', 'Region_SE':'US Southeast', 'Region_SW':'US Southwest', 'Region_TEN':'US Tennessee', 'Region_TEX':'US Texas', 'Ontario':'CAN Ontario','British_Columbia':'CAN BC','United-Kingdom':'United Kingdom', 'Czech_Republic':'Czechia', 'New_Zealand':'New Zealand'} 

saturdays = pd.date_range(start='1/1/2020', end='10/31/2020')[3:304:7].values
all_data = pd.DataFrame({'Date':saturdays}, index=np.arange(0, len(saturdays)))
for country in countries_and_regions:
    df_subset = pd.read_csv('../Data/Intermediate/consumption_change_estimates/'+country+'_final_week.csv', index_col=0)
    all_data[country] = df_subset['percent_red']
all_data = all_data.fillna(method='pad').fillna(method='bfill') # 8 missing values for later period (3 in Finland, 1 in Ukraine, 4 in Alberta)
all_data.to_csv('../Data/Intermediate/fullperiod_weekly_data_for_clustering.csv')


fig, ax = plt.subplots(figsize=(8,5))
for i in countries_and_regions:
    ax.plot(pd.to_datetime(all_data['Date']), all_data[i], color='C0', alpha=0.3, zorder=1)
ax.plot(pd.to_datetime(all_data['Date']), all_data.loc[:, all_data.columns[1:]].mean(axis=1), 'k', zorder=2)
ax.axhline(color='k', zorder=1)
ax.axvline(datetime.datetime(2020,4,25), color='r', zorder=1)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.set_xlim([datetime.datetime(2020,1,1), datetime.datetime(2020,10,31)])
ax.tick_params(axis = 'both', which = 'major', labelsize = 14)
ax.set_ylabel('Percent change in electricity consumption', fontsize=16)
plt.tight_layout()
plt.savefig('../Figures/fig3_full_timeseries_showing_cutoff.pdf', bbox_inches='tight')
plt.show()