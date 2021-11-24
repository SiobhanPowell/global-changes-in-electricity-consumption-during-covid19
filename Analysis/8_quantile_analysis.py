import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import matplotlib.dates as mdates
import datetime
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates

all_data = pd.read_csv('../Data/Intermediate/fullperiod_weekly_data_for_clustering.csv', index_col=0)
initial = all_data.loc[pd.to_datetime(all_data['Date']).dt.date <= datetime.date(2020,4,28)]
recovery = all_data.loc[pd.to_datetime(all_data['Date']).dt.date > datetime.date(2020,4,28)]
title_dict = {'Region_TEX':'US Texas', 'Region_CAL':'US California', 'Region_CAR':'US Carolinas', 'Region_CENT':'US Central', 
              'Region_FLA':'US Florida', 'Region_MIDA':'US Mid-Atlantic', 'Region_MIDW':'US Midwest', 'Region_NE':'US New England', 'Region_NW':'US Northwest', 'Region_NY':'US New York', 'Region_SE':'US Southeast', 'Region_SW':'US Southwest', 'Region_TEN':'US Tennessee', 'Region_TEX':'US Texas', 'Ontario':'CAN Ontario','British_Columbia':'CAN BC', 'Alberta':'CAN Alberta', 'Czech_Republic':'Czechia', 'New_Zealand':'New Zealand', 'United-Kingdom':'United Kingdom'}

# clustering
original_cluster_mapping = pd.read_csv('../Data/Intermediate/cluster_mapping_initial_recovery.csv', index_col=0)

def implement_clusters(df, num_clusters, return_cts=False, return_all=False):
    
    results_df = pd.DataFrame(np.zeros((len(df.columns[1:]), 100)))
    inertias = np.zeros((100,))
    
    for j in range(100):
        km = KMeans(n_clusters=num_clusters).fit(np.transpose(df.loc[:, df.columns[1:]].values))
        mins = km.cluster_centers_.min(axis=1)
        inds = np.argsort(mins)
        old_labels = np.copy(km.labels_)
        new_labels = np.zeros(np.shape(old_labels))
        for i in range(num_clusters):
            new_labels[np.where(old_labels==inds[i])[0]] = i

        results_df.loc[:, j] = new_labels
        inertias[j] = km.inertia_
        
    vals, inds, cts = np.unique(results_df.values, axis=1, return_counts=True, return_index=True)
    results_lowinertia = results_df.loc[:, np.where(inertias == np.min(inertias))[0][0]].values.ravel()
    new_labels = results_lowinertia
    
    new_centers = np.zeros(km.cluster_centers_.shape)
    cluster_mapping_result = {'Country':[], 'Cluster':[]}
    for i in range(num_clusters):
        setofcountries = list(df.columns[1:][np.where(results_lowinertia==i)[0]])
        for country in setofcountries:
            cluster_mapping_result['Country'].append(country)
            cluster_mapping_result['Cluster'].append(i)
        new_centers[i, :] = df.loc[:, setofcountries].mean(axis=1).values
            
    cluster_mapping_result = pd.DataFrame(cluster_mapping_result)
    if return_all:
        return new_labels, cluster_mapping_result, new_centers, cts, inds, vals, inertias, results_df
    if return_cts:
        return new_labels, cluster_mapping_result, new_centers, cts, results_df
    else:
        return new_labels, cluster_mapping_result, new_centers
    
# Run clustering for 4 and 5 clusters to compare with quartile and quintile results as needed
for num in [4, 5]:
    new_labels, cluster_mapping_result, new_centers = implement_clusters(initial, num_clusters=num)
    for i in original_cluster_mapping.index:
        original_cluster_mapping.loc[i, 'Initial '+str(num)] = int(cluster_mapping_result.loc[cluster_mapping_result[cluster_mapping_result['Country']==original_cluster_mapping.loc[i, 'Country']].index, 'Cluster'].values[0])
    new_labels, cluster_mapping_result, new_centers = implement_clusters(recovery, num_clusters=num)
    for i in original_cluster_mapping.index:
        original_cluster_mapping.loc[i, 'Recovery '+str(num)] = int(cluster_mapping_result.loc[cluster_mapping_result[cluster_mapping_result['Country']==original_cluster_mapping.loc[i, 'Country']].index, 'Cluster'].values[0])

original_cluster_mapping['Recovery 4'] = original_cluster_mapping['Recovery 4'].astype(int)
original_cluster_mapping['Recovery 5'] = original_cluster_mapping['Recovery 5'].astype(int)
original_cluster_mapping['Initial 4'] = original_cluster_mapping['Initial 4'].astype(int)
original_cluster_mapping['Initial 5'] = original_cluster_mapping['Initial 5'].astype(int)

# Summary values for quantile analysis
ind1 = recovery.index.values[0]
ind2 = recovery.index.values[-1]
summary_data = pd.DataFrame({'Country':all_data.columns[1:]})
summary_data = summary_data.sort_values(by='Country').reset_index(drop=True)
for i in summary_data.index:
    summary_data.loc[i, 'Initial Size of Drop'] = initial[summary_data.loc[i, 'Country']].min()
    summary_data.loc[i, 'Recovery Speed'] = (recovery.loc[ind2, summary_data.loc[i, 'Country']] - recovery.loc[ind1, summary_data.loc[i, 'Country']]) / (ind2-ind1)
    summary_data.loc[i, 'Recovery Mean'] = recovery[summary_data.loc[i, 'Country']].mean()
    try:
        summary_data.loc[i, 'Recovery Cross Zero'] = recovery[recovery[summary_data.loc[i, 'Country']]>=0].index.values[0]
    except:
        summary_data.loc[i, 'Recovery Cross Zero'] = recovery.index.values[-1]+1
    # transfer clustering data
    summary_data.loc[i, 'Initial Cluster 3'] = original_cluster_mapping.loc[original_cluster_mapping[original_cluster_mapping['Country']==summary_data.loc[i, 'Country']].index, 'Initial'].values[0]
    summary_data.loc[i, 'Recovery Cluster 3'] = original_cluster_mapping.loc[original_cluster_mapping[original_cluster_mapping['Country']==summary_data.loc[i, 'Country']].index, 'Recovery'].values[0]
    summary_data.loc[i, 'Initial Cluster 4'] = original_cluster_mapping.loc[original_cluster_mapping[original_cluster_mapping['Country']==summary_data.loc[i, 'Country']].index, 'Initial 4'].values[0]
    summary_data.loc[i, 'Recovery Cluster 4'] = original_cluster_mapping.loc[original_cluster_mapping[original_cluster_mapping['Country']==summary_data.loc[i, 'Country']].index, 'Recovery 4'].values[0]
    summary_data.loc[i, 'Initial Cluster 5'] = original_cluster_mapping.loc[original_cluster_mapping[original_cluster_mapping['Country']==summary_data.loc[i, 'Country']].index, 'Initial 5'].values[0]
    summary_data.loc[i, 'Recovery Cluster 5'] = original_cluster_mapping.loc[original_cluster_mapping[original_cluster_mapping['Country']==summary_data.loc[i, 'Country']].index, 'Recovery 5'].values[0]
for i in summary_data.index:
    if summary_data.loc[i, 'Country'] in title_dict.keys():
        summary_data.loc[i, 'Country Name'] = title_dict[summary_data.loc[i, 'Country']]
    else:
        summary_data.loc[i, 'Country Name'] = summary_data.loc[i, 'Country']
        
# Quantiles
def terciles_calculation(metric_name, summary_data, number=3):
    
    val0 = 0
    for i, val in enumerate(np.linspace(0, 100, number+1)):
        perc1 = np.percentile(summary_data[metric_name].values, val0)
        perc2 = np.percentile(summary_data[metric_name].values, val)
        inds = summary_data.loc[(summary_data[metric_name] >= perc1)&(summary_data[metric_name] <= perc2)].index
        if number == 4:
            summary_data.loc[inds, metric_name+' Quartile '+str(number)] = i-1
        else:
            summary_data.loc[inds, metric_name+' Tercile '+str(number)] = i-1
        val0 = val
        
    return summary_data

# Tercile plotting function
def plot_terciles_oneplot(metric_name, number, period, summary_data, reverse=False, save_string=None):
    
    if period in ['Initial', 'Initial 3']:
        col = 'Initial Cluster 3'
        data_plot = initial.copy(deep=True)
    elif period in ['Recovery', 'Recovery 3']:
        col = 'Recovery Cluster 3'
        data_plot = recovery.copy(deep=True)
    elif period == 'Initial 4':
        col = 'Initial Cluster 4'
        data_plot = initial.copy(deep=True)
    elif period == 'Initial 5':
        col = 'Initial Cluster 5'
        data_plot = initial.copy(deep=True)
    elif period == 'Recovery 4':
        col = 'Recovery Cluster 4'
        data_plot = recovery.copy(deep=True)
    elif period == 'Recovery 5':
        col = 'Recovery Cluster 5'
        data_plot = recovery.copy(deep=True)
    else:
        print('Please specify period.')
        return
    
    all_colours = ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#a50026']
    all_colours2 = ['#1a9850', '#91cf60', '#d9ef8b', '#ffffbf', '#006837']

    if number == 3:
        legend_elements_terciles = [Patch(facecolor=all_colours2[0], label='Tercile 1'), Patch(facecolor=all_colours2[1], label='Tercile 2'), Patch(facecolor=all_colours2[2], label='Tercile 3')]
    elif number == 4:
        legend_elements_terciles = [Patch(facecolor=all_colours2[0], label='Tercile 1'), Patch(facecolor=all_colours2[1], label='Tercile 2'), Patch(facecolor=all_colours2[2], label='Tercile 3'), Patch(facecolor=all_colours2[3], label='Tercile 4')]
    elif number == 5:
        legend_elements_terciles = [Patch(facecolor=all_colours2[0], label='Tercile 1'), Patch(facecolor=all_colours2[1], label='Tercile 2'), Patch(facecolor=all_colours2[2], label='Tercile 3'), Patch(facecolor=all_colours2[3], label='Tercile 4'), Patch(facecolor=all_colours2[4], label='Tercile 5')]

    
    test = summary_data.sort_values(by=metric_name).reset_index(drop=True)
    for i in range(number):
        test.loc[test[test[metric_name+' Tercile '+str(number)]==i].index, 'Colour'] = all_colours2[i]
        if reverse:
            test.loc[test[test[col]==i].index, 'Colour2'] = all_colours[number-1-i]
        else:
            test.loc[test[test[col]==i].index, 'Colour2'] = all_colours[i]

    fig = plt.figure(constrained_layout=True, figsize=(16, 8))
    gs = fig.add_gridspec(2, 6, width_ratios=[3,3,0.5, 5,5,5])
    f_ax1 = fig.add_subplot(gs[:, 0])
    f_ax2 = fig.add_subplot(gs[:, 1])
    f_ax0 = fig.add_subplot(gs[:, 2])
    f_ax3 = fig.add_subplot(gs[0, 3])
    f_ax4 = fig.add_subplot(gs[0, 4], sharey=f_ax3)
    f_ax5 = fig.add_subplot(gs[0, 5], sharey=f_ax3)
    f_ax6 = fig.add_subplot(gs[1, 3])
    f_ax7 = fig.add_subplot(gs[1, 4], sharey=f_ax6)
    f_ax8 = fig.add_subplot(gs[1, 5], sharey=f_ax6)

    f_ax1.set_title('Colour By KMeans', fontname='Arial')
    f_ax1.barh(test.index.values, test[metric_name].values, color=test['Colour2'].values)
    f_ax1.set_yticks(test.index.values)
    f_ax1.set_yticklabels(test['Country Name'].values, fontname='Arial')
    f_ax1.set_xlabel(metric_name, fontname='Arial')
    legend_elements = [Patch(facecolor=all_colours[0], label='Cluster 1'), Patch(facecolor=all_colours[1], label='Cluster 2'), Patch(facecolor=all_colours[2], label='Cluster 3')]
    f_ax1.legend(handles=legend_elements, loc='upper left', prop={'family':'Arial'})
    f_ax2.set_title('Colour By Tercile', fontname='Arial')
    f_ax2.barh(test.index.values, test[metric_name].values, color=test['Colour'].values)
    f_ax2.set_yticks(test.index.values)
    f_ax2.set_yticklabels(test['Country Name'].values, fontname='Arial')
    f_ax2.set_xlabel(metric_name, fontname='Arial')
    f_ax2.legend(handles=legend_elements_terciles, loc='upper left', prop={'family':'Arial'})
        
    label1 = col
    label2 = metric_name+' Tercile '+str(number)
    title2 = metric_name
    
    legend_elements = [Patch(facecolor=all_colours[0], label='Cluster 1'), Patch(facecolor=all_colours[1], label='Cluster 2'), Patch(facecolor=all_colours[2], label='Cluster 3')]
    ax_dict = {0:f_ax3, 1:f_ax4, 2:f_ax5}
    for i in data_plot.columns[1:]:
        val1 = summary_data.loc[summary_data[summary_data['Country']==i].index, label1].values
        val2 = summary_data.loc[summary_data[summary_data['Country']==i].index, label2].values
        ax_dict[int(val1)].plot(pd.to_datetime(data_plot['Date']), data_plot[i].values, color=all_colours[int(val1)])
    for j in range(3):
        ax_dict[j].axhline(0, color='k')
        ax_dict[j].set_title('Cluster '+str(j+1), fontname='Arial')
        ax_dict[j].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax_dict[j].xaxis.set_major_formatter(DateFormatter("%m-%d"))
        plt.xticks(fontname='Arial')
        ax_dict[j].set_xlabel('Date', fontname='Arial')
    f_ax3.legend(handles=legend_elements, loc='lower left', prop={'family':'Arial'})
    f_ax3.set_ylabel('Percent Change Electricity Consumption', fontname='Arial')

    ax_dict = {0:f_ax6, 1:f_ax7, 2:f_ax8}
    for i in data_plot.columns[1:]:
        val1 = summary_data.loc[summary_data[summary_data['Country']==i].index, label1].values
        val2 = summary_data.loc[summary_data[summary_data['Country']==i].index, label2].values
        if reverse:
            ax_dict[2-int(val2)].plot(pd.to_datetime(data_plot['Date']), data_plot[i].values, color=all_colours[int(val1)])
        else:
            ax_dict[int(val2)].plot(pd.to_datetime(data_plot['Date']), data_plot[i].values, color=all_colours[int(val1)])
    for j in range(number):
        ax_dict[j].axhline(0, color='k')
        ax_dict[j].set_title('Tercile '+str(j+1), fontname='Arial')
        ax_dict[j].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax_dict[j].xaxis.set_major_formatter(DateFormatter("%m-%d"))
        ax_dict[j].set_xlabel('Date', fontname='Arial')
        plt.xticks(fontname='Arial')
    ax_dict[0].set_ylabel('Percent Change Electricity Consumption', fontname='Arial')
    ax_dict[0].legend(handles=legend_elements, loc='lower left', prop={'family':'Arial'})


    f_ax0.axis('off')
    
    if save_string is not None:
        plt.savefig('../Figures/'+save_string+'_all.pdf', bbox_inches='tight')
        plt.savefig('../Figures/'+save_string+'_all.png', bbox_inches='tight')
    plt.show()

    return

# Quartile plotting function

def plot_quartiles_oneplot(metric_name, number, period, summary_data, reverse=False, save_string=None):
    
    if period in ['Initial', 'Initial 3']:
        col = 'Initial Cluster 3'
        data_plot = initial.copy(deep=True)
    elif period in ['Recovery', 'Recovery 3']:
        col = 'Recovery Cluster 3'
        data_plot = recovery.copy(deep=True)
    elif period == 'Initial 4':
        col = 'Initial Cluster 4'
        data_plot = initial.copy(deep=True)
    elif period == 'Initial 5':
        col = 'Initial Cluster 5'
        data_plot = initial.copy(deep=True)
    elif period == 'Recovery 4':
        col = 'Recovery Cluster 4'
        data_plot = recovery.copy(deep=True)
    elif period == 'Recovery 5':
        col = 'Recovery Cluster 5'
        data_plot = recovery.copy(deep=True)
    else:
        print('Please specify period.')
        return
    
    all_colours = ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#a50026']
    all_colours2 = ['#1a9850', '#91cf60', '#d9ef8b', '#ffffbf', '#006837']

    if number == 3:
        legend_elements_terciles = [Patch(facecolor=all_colours2[0], label='Tercile 1'), Patch(facecolor=all_colours2[1], label='Tercile 2'), Patch(facecolor=all_colours2[2], label='Tercile 3')]
    elif number == 4:
        legend_elements_terciles = [Patch(facecolor=all_colours2[0], label='Quartile 1'), Patch(facecolor=all_colours2[1], label='Quartile 2'), Patch(facecolor=all_colours2[2], label='Quartile 3'), Patch(facecolor=all_colours2[3], label='Quartile 4')]

    
    test = summary_data.sort_values(by=metric_name).reset_index(drop=True)
    for i in range(number):
        test.loc[test[test[metric_name+' Quartile '+str(number)]==i].index, 'Colour'] = all_colours2[i]
        if reverse:
            test.loc[test[test[col]==i].index, 'Colour2'] = all_colours[number-1-i]
        else:
            test.loc[test[test[col]==i].index, 'Colour2'] = all_colours[i]

    fig = plt.figure(constrained_layout=True, figsize=(16, 8))
    gs = fig.add_gridspec(2, 7, width_ratios=[3,3,0.5, 5,5,5, 5])
    f_ax1 = fig.add_subplot(gs[:, 0])
    f_ax2 = fig.add_subplot(gs[:, 1])
    f_ax0 = fig.add_subplot(gs[:, 2])
    f_ax3 = fig.add_subplot(gs[0, 3])
    f_ax4 = fig.add_subplot(gs[0, 4], sharey=f_ax3)
    f_ax5 = fig.add_subplot(gs[0, 5], sharey=f_ax3)
    f_ax6 = fig.add_subplot(gs[0, 6], sharey=f_ax3)
    f_ax7 = fig.add_subplot(gs[1, 3])
    f_ax8 = fig.add_subplot(gs[1, 4], sharey=f_ax6)
    f_ax9 = fig.add_subplot(gs[1, 5], sharey=f_ax6)
    f_ax10 = fig.add_subplot(gs[1, 6], sharey=f_ax6)

    f_ax1.set_title('Colour By KMeans', fontname='Arial')
    f_ax1.barh(test.index.values, test[metric_name].values, color=test['Colour2'].values)
    f_ax1.set_yticks(test.index.values)
    f_ax1.set_yticklabels(test['Country Name'].values, fontname='Arial')
    f_ax1.set_xlabel(metric_name, fontname='Arial')
    legend_elements = [Patch(facecolor=all_colours[0], label='Cluster 1'), Patch(facecolor=all_colours[1], label='Cluster 2'), Patch(facecolor=all_colours[2], label='Cluster 3'), Patch(facecolor=all_colours[3], label='Cluster 4')]
    f_ax1.legend(handles=legend_elements, loc='upper left', prop={'family':'Arial'})
    f_ax2.set_title('Colour By Quartile', fontname='Arial')
    f_ax2.barh(test.index.values, test[metric_name].values, color=test['Colour'].values)
    f_ax2.set_yticks(test.index.values)
    f_ax2.set_yticklabels(test['Country Name'].values, fontname='Arial')
    f_ax2.set_xlabel(metric_name, fontname='Arial')
    plt.xticks(fontname='Arial')
    f_ax2.legend(handles=legend_elements_terciles, loc='upper left', prop={'family':'Arial'})
        
    label1 = col
    label2 = metric_name+' Quartile '+str(number)
    title2 = metric_name
    
    legend_elements = [Patch(facecolor=all_colours[0], label='Cluster 1'), Patch(facecolor=all_colours[1], label='Cluster 2'), Patch(facecolor=all_colours[2], label='Cluster 3'), Patch(facecolor=all_colours[3], label='Cluster 4')]
    ax_dict = {0:f_ax3, 1:f_ax4, 2:f_ax5, 3:f_ax6}
    for i in data_plot.columns[1:]:
        val1 = summary_data.loc[summary_data[summary_data['Country']==i].index, label1].values
        val2 = summary_data.loc[summary_data[summary_data['Country']==i].index, label2].values
        ax_dict[int(val1)].plot(pd.to_datetime(data_plot['Date']), data_plot[i].values, color=all_colours[int(val1)])
    for j in range(4):
        ax_dict[j].axhline(0, color='k')
        ax_dict[j].set_title('Cluster '+str(j+1), fontname='Arial')
        ax_dict[j].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax_dict[j].xaxis.set_major_formatter(DateFormatter("%m-%d"))
        ax_dict[j].set_xlabel('Date', fontname='Arial')
        plt.xticks(fontname='Arial')
    f_ax3.legend(handles=legend_elements, loc='lower left', prop={'family':'Arial'})
    f_ax3.set_ylabel('Percent Change Electricity Consumption', fontname='Arial')

    ax_dict = {0:f_ax7, 1:f_ax8, 2:f_ax9, 3:f_ax10}
    for i in data_plot.columns[1:]:
        val1 = summary_data.loc[summary_data[summary_data['Country']==i].index, label1].values
        val2 = summary_data.loc[summary_data[summary_data['Country']==i].index, label2].values
        if reverse:
            ax_dict[2-int(val2)].plot(pd.to_datetime(data_plot['Date']), data_plot[i].values, color=all_colours[int(val1)])
        else:
            ax_dict[int(val2)].plot(pd.to_datetime(data_plot['Date']), data_plot[i].values, color=all_colours[int(val1)])
    for j in range(number):
        ax_dict[j].axhline(0, color='k')
        ax_dict[j].set_title('Quartile '+str(j+1), fontname='Arial')
        ax_dict[j].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax_dict[j].xaxis.set_major_formatter(DateFormatter("%m-%d"))
        ax_dict[j].set_xlabel('Date', fontname='Arial')
        plt.xticks(fontname='Arial')
    ax_dict[0].set_ylabel('Percent Change Electricity Consumption', fontname='Arial')
    ax_dict[0].legend(handles=legend_elements, loc='lower left', prop={'family':'Arial'})


    f_ax0.axis('off')
    
    if save_string is not None:
        plt.savefig('../Figures/'+save_string+'_all.pdf', bbox_inches='tight')
        plt.savefig('../Figures/'+save_string+'_all.png', bbox_inches='tight')
    plt.show()

    return

# Calculation for Figure S5
summary_data = terciles_calculation('Initial Size of Drop', summary_data, 3)
plot_terciles_oneplot('Initial Size of Drop', 3, 'Initial', summary_data, save_string='figs5_initial_drop_3clusters_3terciles')

# Calculation for Figure S6
summary_data = terciles_calculation('Initial Size of Drop', summary_data, 4)
plot_quartiles_oneplot('Initial Size of Drop', 4, 'Initial 4', summary_data, save_string='figs6_initial_drop_4clusters_4terciles')

# Calculation for Figure S7
summary_data = terciles_calculation('Recovery Cross Zero', summary_data, 3)
plot_terciles_oneplot('Recovery Cross Zero', 3, 'Recovery', summary_data, reverse=False, save_string='figs7_recovery_cross_zero_3clusters_3terciles')

# Calculation for Figure S8
summary_data = terciles_calculation('Recovery Mean', summary_data, 3)
plot_terciles_oneplot('Recovery Mean', 3, 'Recovery', summary_data, reverse=False, save_string='figs8_recovery_mean_value_3clusters_3terciles')

# Calculation for Figure S9
summary_data = terciles_calculation('Recovery Speed', summary_data, 3)
plot_terciles_oneplot('Recovery Speed', 3, 'Recovery', summary_data, reverse=False, save_string='figs9_recovery_total_slope_3clusters_3terciles')



    