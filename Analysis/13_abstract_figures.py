import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.cluster import KMeans
import matplotlib.dates as mdates
import datetime

# Load data
all_data = pd.read_csv('../Data/Intermediate/fullperiod_weekly_data_for_clustering.csv', index_col=0)
full_cluster_mapping = pd.read_csv('../Data/Intermediate/cluster_mapping_initial_recovery.csv', index_col=0)

# Plot part1 

colors = ['#d53e4f', '#fc8d59', '#fee08b', '#99d594', '#3288bd', '#5e4fa2']

subset = all_data[pd.to_datetime(all_data['Date']).dt.date <= datetime.date(2020, 5, 3)].reset_index(drop=True)
subset2 = all_data[pd.to_datetime(all_data['Date']).dt.date > datetime.date(2020, 4, 23)].reset_index(drop=True)
titles = ['Extreme', 'Severe', 'Mild']
fig, axes = plt.subplots(figsize=(8,5))#, sharey=True)
period = 'Initial'
for i in range(3):
    countries = full_cluster_mapping[full_cluster_mapping[period]==i]['Country'].values
    axes.plot(pd.to_datetime(subset['Date']), subset.loc[:, countries].mean(axis=1), color=colors[i], zorder=3, label=titles[i], linewidth=3)
        
titles = ['Slow', 'Quick', 'Recovered']
subset2 = all_data[pd.to_datetime(all_data['Date']).dt.date <= datetime.date(2020, 5, 3)].reset_index(drop=True)
subset = all_data[pd.to_datetime(all_data['Date']).dt.date > datetime.date(2020, 4, 23)].reset_index(drop=True)
period = 'Recovery'
for i in range(3):
    countries = full_cluster_mapping[full_cluster_mapping[period]==i]['Country'].values
    axes.plot(pd.to_datetime(subset['Date']), subset.loc[:, countries].mean(axis=1), color=colors[i+3], zorder=3, label=titles[i], linewidth=3)
    
    
axes.axhline(color='k', alpha=0.3, zorder=1)
axes.axvline(datetime.date(2020,4,28), linestyle='--', color='k', alpha=0.7, zorder=1)
axes.xaxis.set_major_locator(mdates.MonthLocator())
axes.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
axes.set_xlabel('Month', fontsize=16, fontname='Arial')
axes.set_ylabel('% Change Electricity Consumption', fontsize=16, fontname='Arial')
axes.set_yticks([-25, -20, -15, -10, -5, 0])
axes.set_yticklabels([-25, -20, -15, -10, -5, 0], fontsize=16, fontname='Arial')
axes.set_ylim([-28, 3])
axes.set_xlim([datetime.date(2020,1,1), datetime.date(2020, 10, 27)])
axes.legend(fontsize=16, ncol=2, loc='lower right', prop={'family':'Arial', 'size':16})
plt.xticks(fontsize=16, fontname='Arial')
plt.tight_layout()
plt.savefig('../Figures/fig_abstract_part1.pdf', bbox_inches='tight')
plt.show()
#     axes[i].set_title(titles[i], fontsize=16)

option_b_recovery = pd.read_csv('../Data/Intermediate/barchart_data_recovery_fixed.csv')
option_b_initial = pd.read_csv('../Data/Intermediate/barchart_data_initial_fixed.csv')

fig, axes = plt.subplots(1, 2, figsize=(8, 3), sharey=True)
for i in range(3):
    axes[0].bar([i], [option_b_initial.loc[i, 'Oxford']], width=0.8, color=colors[i], yerr=option_b_initial.loc[i, 'Oxford SEM'], error_kw={'elinewidth':3})
axes[0].set_xticks([0, 1, 2])
axes[0].set_xticklabels(['Extreme', 'Severe', 'Mild'], fontsize=16, fontname='Arial')
for i in range(3):
    axes[1].bar([i], [option_b_recovery.loc[i, 'Oxford']], width=0.8, color=colors[i+3], yerr=option_b_initial.loc[i, 'Oxford SEM'], error_kw={'elinewidth':3})
axes[1].set_xticks([0, 1, 2])
axes[1].set_xticklabels(['Slow', 'Quick', 'Recovered'], fontsize=16, fontname='Arial')
axes[0].set_yticks([0, 10, 20, 30, 40, 50, 60])
axes[0].set_yticklabels([0, 10, 20, 30, 40, 50, 60], fontsize=14, fontname='Arial')
axes[0].set_ylabel('Stringency Index', fontsize=16, fontname='Arial')
plt.tight_layout()
plt.savefig('../Figures/fig_abstract_part2a.pdf')
plt.show()

fig, axes = plt.subplots(1, 2, figsize=(8, 3), sharey=True)
for i in range(3):
    axes[0].bar([i], [option_b_initial.loc[i, 'Mobility: Retail and Recreation']], width=0.8, color=colors[i], yerr=option_b_initial.loc[i, 'Mobility: Retail and Recreation SEM'], error_kw={'elinewidth':3})
axes[0].set_xticks([0, 1, 2])
axes[0].set_xticklabels(['Extreme', 'Severe', 'Mild'], fontsize=16, fontname='Arial')
for i in range(3):
    axes[1].bar([i], [option_b_recovery.loc[i, 'Mobility: Retail and Recreation']], width=0.8, color=colors[i+3], yerr=option_b_initial.loc[i, 'Mobility: Retail and Recreation SEM'], error_kw={'elinewidth':3})
axes[1].set_xticks([0, 1, 2])
axes[1].set_xticklabels(['Slow', 'Quick', 'Recovered'], fontsize=16, fontname='Arial')
axes[0].set_yticks([-60, -50, -40, -30, -20, -10, 0])
axes[0].set_yticklabels([-60, -50, -40, -30, -20, -10, 0], fontsize=14, fontname='Arial')
axes[0].set_ylabel('Mobility: Retail/Rec', fontsize=16, fontname='Arial')
plt.tight_layout()
plt.savefig('../Figures/fig_abstract_part2b.pdf')
plt.show()