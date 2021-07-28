import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from scipy.stats import sem


cluster_mapping = pd.read_csv('../Data/Intermediate/cluster_mapping_initial_recovery.csv', index_col=0)
cluster_mapping.loc[cluster_mapping[cluster_mapping['Country']=='United-Kingdom'].index, 'Country'] = 'United Kingdom'
mob_cols = ['Mobility: '+i for i in ['Workplaces', 'Residences', 'Grocery and Pharmacy', 'Retail and Recreation', 'Parks', 'Transit Stations']]

# Calculate means
option_b_initial = pd.DataFrame({'Cluster':np.arange(0, 3)})
option_b_recovery = pd.DataFrame({'Cluster':np.arange(0, 3)})

df_ref = pd.read_csv('../Data/Intermediate/summary_data/'+'Italy'+'_timevarying_recovery_fixed.csv')
df_ref_init = df_ref.loc[pd.to_datetime(df_ref['Date']).dt.date <= datetime.date(2020,4,28)].copy(deep=True)
df_ref_recov = df_ref.loc[pd.to_datetime(df_ref['Date']).dt.date > datetime.date(2020,4,28)].copy(deep=True)
for col in ['Oxford', 'Pct Change in Electricity Demand', 'Daily Cases per 100k', 'Daily Deaths per 100k']:
    for clust in range(3):
        countries = cluster_mapping[cluster_mapping['Initial']==clust]['Country'].values
        data_here_init = np.zeros((len(df_ref_init), len(countries)))
        for i, country in enumerate(countries):
            df = pd.read_csv('../Data/Intermediate/summary_data/'+country+'_timevarying_recovery_fixed.csv')
            data_here_init[:, i] = df.loc[pd.to_datetime(df['Date']).dt.date <= datetime.date(2020,4,28)][col].values
        
        option_b_initial.loc[clust, col] = np.mean(np.nanmean(data_here_init, axis=0))
        option_b_initial.loc[clust, col+' SEM'] = sem(np.nanmean(data_here_init, axis=0))
        
        countries = cluster_mapping[cluster_mapping['Recovery']==clust]['Country'].values
        data_here_recov = np.zeros((len(df_ref_recov), len(countries)))
        for i, country in enumerate(countries):
            df = pd.read_csv('../Data/Intermediate/summary_data/'+country+'_timevarying_recovery_fixed.csv')
            data_here_recov[:, i] = df.loc[pd.to_datetime(df['Date']).dt.date > datetime.date(2020,4,28)][col].values
        option_b_recovery.loc[clust, col] = np.mean(np.nanmean(data_here_recov, axis=0))
        option_b_recovery.loc[clust, col+' SEM'] = sem(np.nanmean(data_here_recov, axis=0))

for col in mob_cols:
    for clust in range(3):
        countries = cluster_mapping[cluster_mapping['Initial']==clust]['Country'].values
        data_here_init = np.zeros((len(df_ref_init), len(countries)))
        for i, country in enumerate(countries):
            df = pd.read_csv('../Data/Intermediate/summary_data/'+country+'_timevarying_recovery_fixed.csv')
            data_here_init[:, i] = df.loc[pd.to_datetime(df['Date']).dt.date <= datetime.date(2020,4,28)][col].values
        option_b_initial.loc[clust, col] = np.mean(np.nanmean(data_here_init, axis=0))
        option_b_initial.loc[clust, col+' SEM'] = sem(np.nanmean(data_here_init, axis=0))#, nan_policy='omit')
        
        countries = cluster_mapping[cluster_mapping['Recovery']==clust]['Country'].values
        data_here_recov = np.zeros((len(df_ref_recov), len(countries)))
        for i, country in enumerate(countries):
            df = pd.read_csv('../Data/Intermediate/summary_data/'+country+'_timevarying_recovery_fixed.csv')
            data_here_recov[:, i] = df.loc[pd.to_datetime(df['Date']).dt.date > datetime.date(2020,4,28)][col].values
        option_b_recovery.loc[clust, col] = np.mean(np.nanmean(data_here_recov, axis=0))
        option_b_recovery.loc[clust, col+' SEM'] = sem(np.nanmean(data_here_recov, axis=0))#, nan_policy='omit')
    
new_mappings = pd.read_csv('../Data/Intermediate/new_gdp_holidays_weekends.csv')
sector = pd.read_csv('../Data/Intermediate/all_sector_data.csv')
for clust in range(3):
    for col in new_mappings.columns[2:]:
        countries = cluster_mapping[cluster_mapping['Initial']==clust]['Country'].values
        option_b_initial.loc[clust, col] = np.mean(new_mappings[new_mappings['Country'].isin(countries)][col].values)
        option_b_initial.loc[clust, col+' SEM'] = sem(new_mappings[new_mappings['Country'].isin(countries)][col].values)
        countries = cluster_mapping[cluster_mapping['Recovery']==clust]['Country'].values
        option_b_recovery.loc[clust, col] = np.mean(new_mappings[new_mappings['Country'].isin(countries)][col].values)
        option_b_recovery.loc[clust, col+' SEM'] = sem(new_mappings[new_mappings['Country'].isin(countries)][col].values)
        
    for col in ['Commercial and public services', 'Industry', 'Other', 'Residential', 'Transport']:
        countries = cluster_mapping[cluster_mapping['Initial']==clust]['Country'].values
        countries2 = []
        for country in countries:
            country2 = country
            if country == 'Czech_Republic':
                country2 = 'Czech Republic'
            if country == 'New_Zealand':
                country2 = 'New Zealand'
            if country == 'Russia':
                country2 = 'Russian Federation'
            if country in ['Ontario','British_Columbia', 'Alberta']:
                country2 = 'Canada'
            countries2.append(country2)
        option_b_initial.loc[clust, 'Sector '+col] = np.mean(sector[sector['Country'].isin(countries2)][col].values)
        option_b_initial.loc[clust, 'Sector '+col+' SEM'] = sem(sector[sector['Country'].isin(countries2)][col].values)
        
        countries = cluster_mapping[cluster_mapping['Recovery']==clust]['Country'].values
        countries2 = []
        for country in countries:
            country2 = country
            if country == 'Czech_Republic':
                country2 = 'Czech Republic'
            if country == 'New_Zealand':
                country2 = 'New Zealand'
            if country == 'Russia':
                country2 = 'Russian Federation'
            if country in ['Ontario','British_Columbia', 'Alberta']:
                country2 = 'Canada'
            countries2.append(country2)
        option_b_recovery.loc[clust, 'Sector '+col] = np.mean(sector[sector['Country'].isin(countries2)][col].values)
        option_b_recovery.loc[clust, 'Sector '+col+' SEM'] = sem(sector[sector['Country'].isin(countries2)][col].values)

        
option_b_recovery.to_csv('../Data/Intermediate/barchart_data_recovery_fixed.csv', index=None)
option_b_initial.to_csv('../Data/Intermediate/barchart_data_initial_fixed.csv', index=None)

# Plotting functions

def plot_means_optionb(df, col, ylabel, figsize=(3.5, 3), savestr=None, yrange=None, bar=False, color='C0', init=None):
    
    means = [df.loc[i, col] for i in range(3)]
    sems = [df.loc[i, col+' SEM'] for i in range(3)]
    
    plt.figure(figsize=figsize)
    if bar:
        plt.bar([1,2,3], means, width=0.6, yerr=sems, zorder=2, color=color, error_kw={'elinewidth':3})
        plt.axhline(color='k', zorder=1, alpha=0.2)
    else:
        plt.errorbar([1,2,3], means, yerr=sems, fmt="_", markersize=24)
    if ('Initial' in ylabel) or init:
        cluster_labels = ['Extreme', 'Severe', 'Mild']
    else:
        cluster_labels = ['Slow', 'Quick', 'Recovered']
    plt.xticks([1,2,3],labels=cluster_labels, fontsize=12, rotation=25, ha='center')
    plt.xlim([0.5, 3.5])
    plt.ylabel(ylabel, fontsize=12)
    if yrange is not None:
        plt.ylim(yrange)
    plt.yticks(fontsize=14)
    plt.tight_layout()
    if savestr is not None:
        plt.savefig(savestr, bbox_inches='tight')
    plt.show()
    
    return

def plot_means_set_optionb(df, col_set, ylabel, figsize=(6,3), savestr=None, yrange=None, move_legend=False, bar=False, special_legend=None, init=None, colors=['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7'], legend_ncol=2, legend_loc='upper left'):
    
    if len(col_set) == 2:
        shifts = [-0.15, 0.15]
        width = 0.3
    elif len(col_set) == 3:
        shifts = [-0.25, 0, 0.25]
        width = 0.25
    elif len(col_set) == 4:
        shifts = [-0.25, -0.083, 0.083, 0.25]
        width = 0.1
    elif len(col_set) == 5:
        shifts = [-0.25, -0.125, 0, 0.125, 0.25]
        width = 0.08
    elif len(col_set) == 6:
        shifts = [-0.25, -0.15, -0.05, 0.05, 0.15, 0.25]
        width = 0.08

    plt.figure(figsize=figsize)
    for j, col in enumerate(col_set):
        means = [df.loc[i, col] for i in range(3)]
        sems = [df.loc[i, col+' SEM'] for i in range(3)]
        if bar:
            if special_legend is not None:
                plt.bar(np.array([1,2,3])+shifts[j], means, width=width, yerr=sems, label=special_legend[j], zorder=2, color=colors[j], error_kw={'elinewidth':3})
            else:
                plt.bar(np.array([1,2,3])+shifts[j], means, width=width, yerr=sems, label=col, zorder=2, color=colors[j], error_kw={'elinewidth':3})
            plt.axhline(color='k', zorder=1, alpha=0.2)
        else:
            plt.errorbar(np.array([1,2,3])+shifts[j], means, yerr=sems, fmt="_", markersize=24, label=col)
    if ('Initial' in ylabel) or init:
        cluster_labels = ['Extreme', 'Severe', 'Mild']
    else:
        cluster_labels = ['Slow', 'Quick', 'Recovered']
    plt.xticks([1,2,3],labels=cluster_labels, fontsize=12, rotation=25, ha='center')
    plt.xlim([0.5, 3.5])
    plt.ylabel(ylabel, fontsize=12)
    plt.yticks( fontsize=14)
    if yrange is not None:
        plt.ylim(yrange)
    if move_legend:
        plt.legend(loc=(-1,1))
    else:
#         plt.legend(ncol=1, loc='lower right')
        plt.legend(ncol=legend_ncol, loc=legend_loc)
        plt.tight_layout()
#     plt.tight_layout()
    if savestr is not None:
        plt.savefig(savestr, bbox_inches='tight')
    plt.show()
    
    return

# Plot components of Fig S10
color = '#8dd3c7'
plot_means_optionb(option_b_initial, 'Daily Cases per 100k',  'Daily Cases per 100k', init=True, yrange=[0,  10], savestr='../Figures/figs10_component_cases_initial.pdf', bar=True, color=color)
plot_means_optionb(option_b_recovery, 'Daily Cases per 100k',  'Daily Cases per 100k', init=False, yrange=[0, 10], savestr='../Figures/figs10_component_cases_recovery.pdf', bar=True, color=color)

color = '#80b1d3'
plot_means_optionb(option_b_initial, 'Daily Deaths per 100k',  'Daily Deaths per 100k', init=True,yrange=[0, 0.5], savestr='../Figures/figs10_component_deaths_initial.pdf', bar=True, color=color)
plot_means_optionb(option_b_recovery, 'Daily Deaths per 100k',  'Daily Deaths per 100k', init=False, yrange=[0, 0.5], savestr='../Figures/figs10_component_deaths_recovery.pdf', bar=True, color=color)

color='#bebada'
plot_means_optionb(option_b_initial, 'Holiday Effect',  'Holiday Effect', init=True, yrange=[-0.28,0],savestr='../Figures/figs10_component_holiday_initial.pdf', bar=True, color=color)
plot_means_optionb(option_b_recovery, 'Holiday Effect', 'Holiday Effect', init=False, yrange=[-0.28,0],savestr='../Figures/figs10_component_holiday_recovery.pdf', bar=True, color=color)

colors=['#f7fcb9', '#addd8e', '#78c679', '#41ab5d', '#006837']
colors=['#d9f0a3', '#78c679', '#006837']
plot_means_set_optionb(option_b_initial, ['Sector Commercial and public services',
       'Sector Industry', 'Sector Residential'],  'Sector Fraction', figsize=(4,3), init=True, yrange=[0, 0.6], savestr='../Figures/figs10_component_sectors_initial.pdf', bar=True, special_legend=['Commercial', 'Industry', 'Residential'], colors=colors)
plot_means_set_optionb(option_b_recovery, ['Sector Commercial and public services',
       'Sector Industry', 'Sector Residential'],  'Sector Fraction', figsize=(4,3), init=False, yrange=[0, 0.6], savestr='../Figures/figs10_component_sectors_recovery.pdf', bar=True, special_legend=['Commercial', 'Industry','Residential'], colors=colors)

color = '#fb8072'
colors = ['#fb8072', '#fdb462']
plot_means_optionb(option_b_initial, 'Q2-2020 change in GDP since Q2-2019', 'GDP Pct Change', init=True, yrange=[-25,0], savestr='../Figures/figs10_component_gdp_initial.pdf', bar=True, color=color)
plot_means_set_optionb(option_b_recovery, ['Q2-2020 change in GDP since Q2-2019', 'Q3-2020 change in GDP since Q3-2019'], 'GDP Pct Change', init=False, yrange=[-25,0], figsize=(3.5,3), savestr='../Figures/figs10_component_gdp_recovery.pdf', bar=True, special_legend=['Q2 2020 vs. Q2 2019', 'Q3 2020 vs. Q3 2019'], colors=colors, legend_ncol=1, legend_loc='lower right')

color='#fee08b'
plot_means_optionb(option_b_initial, 'Oxford', 'Oxford Stringency Index', init=True, yrange=[0,65],savestr='../Figures/figs10_component_restrictions_initial.pdf', bar=True, color=color)
plot_means_optionb(option_b_recovery, 'Oxford', 'Oxford Stringency Index', init=False, yrange=[0,65],savestr='../Figures/figs10_component_restrictions_recovery.pdf', bar=True, color=color)

colors=['#fde0dd', '#fcc5c0', '#fa9fb5', '#f768a1', '#dd3497', '#ae017e', '#7a0177']
colors=['#d73027', '#fc8d59', '#fee090', '#e0f3f8', '#91bfdb', '#4575b4']
mob_cols = ['Mobility: '+i for i in ['Workplaces', 'Residences', 'Grocery and Pharmacy', 'Retail and Recreation']]#, 'Parks', 'Transit Stations']]
plot_means_set_optionb(option_b_initial, mob_cols,  '% chg Mobility Demand', init=True, yrange=[-60, 50], special_legend=['Workplaces', 'Residences', 'Grocery Pharmacy', 'Retail Recreation', 'Parks', 'Transit'], savestr='../Figures/figs10_component_mobility_initial.pdf', bar=True, colors=colors)
plot_means_set_optionb(option_b_recovery, mob_cols,  '% chg Mobility Demand', init=False, yrange=[-60,50], special_legend=['Workplaces', 'Residences', 'Grocery Pharmacy', 'Retail Recreation', 'Parks', 'Transit'], savestr='../Figures/figs10_component_mobility_recovery.pdf', bar=True, colors=colors)

