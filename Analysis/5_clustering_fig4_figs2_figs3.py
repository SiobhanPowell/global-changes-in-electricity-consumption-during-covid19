import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.cluster import KMeans
import matplotlib.dates as mdates
import datetime

all_data = pd.read_csv('../Data/Intermediate/fullperiod_weekly_data_for_clustering.csv', index_col=0)

# Functions for running clustering:
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
    
def elbow_plot(df, save_str=None, title=''):
    
    cluster_fit = pd.DataFrame({'Num Clusters':np.arange(2, 8), 'Inertia':np.zeros((6, ))})
    for i in cluster_fit.index:
        new_labels, cluster_mapping_result, new_centers, cts, inds, vals, inertias, results_df = implement_clusters(df, cluster_fit.loc[i, 'Num Clusters'], return_all=True)
        cluster_fit.loc[i, 'Inertia'] = np.min(inertias)

    plt.figure(figsize=(5,4))
    plt.plot(cluster_fit['Num Clusters'], cluster_fit['Inertia'],'-*')
    plt.ylabel('Inertia', fontsize=14, fontname='Arial'); 
    plt.xlabel('Number of Clusters', fontsize=14, fontname='Arial')
    plt.xticks(fontsize=14, fontname='Arial')
    plt.yticks(fontname='Arial')
    plt.tight_layout()
    plt.title(title, fontsize=14, fontname='Arial')
    if save_str is not None:
        plt.savefig(save_str, bbox_inches='tight')
    plt.show()
    
    
# Run Figures S2 and S3: 
subset = all_data[pd.to_datetime(all_data['Date']) <= datetime.date(2020, 4, 28)].reset_index(drop=True)
elbow_plot(subset, save_str='../Figures/figs2_elbow_plot_initial.pdf', title='Initial Period')
subset = all_data[pd.to_datetime(all_data['Date']) > datetime.date(2020, 4, 28)].reset_index(drop=True)
elbow_plot(subset, save_str='../Figures/figs3_elbow_plot_recovery.pdf', title='Recovery Period')

# Select K=3 for both
# Save clustering result:

full_centers = {}

# initial
subset = all_data[pd.to_datetime(all_data['Date']) <= datetime.date(2020, 4, 30)].reset_index(drop=True)
new_labels, cluster_mapping_result, new_centers, cts, inds, vals, inertias, results_df = implement_clusters(subset, num_clusters=3, return_all=True)
full_cluster_mapping = pd.DataFrame({'Country':cluster_mapping_result['Country'], 'Initial':cluster_mapping_result['Cluster']})
full_centers['Initial'] = new_centers

# recovery
subset = all_data[pd.to_datetime(all_data['Date']) > datetime.date(2020, 4, 30)].reset_index(drop=True)
new_labels, cluster_mapping_result, new_centers, cts, inds, vals, inertias, results_df = implement_clusters(subset, num_clusters=3, return_all=True)
for i in full_cluster_mapping.index:
    full_cluster_mapping.loc[i, 'Recovery'] = int(cluster_mapping_result.loc[cluster_mapping_result['Country']==full_cluster_mapping.loc[i, 'Country']]['Cluster'].values[0])
full_centers['Recovery'] = new_centers


for col in ['Initial', 'Recovery']:
    full_cluster_mapping[col] = full_cluster_mapping[col].astype(int)
full_cluster_mapping.to_csv('../Data/Intermediate/cluster_mapping_initial_recovery.csv')

# Plot Figure 4 for paper showing the results
all_data = pd.read_csv('../Data/Intermediate/fullperiod_weekly_data_for_clustering.csv', index_col=0)
full_cluster_mapping = pd.read_csv('../Data/Intermediate/cluster_mapping_initial_recovery.csv', index_col=0)

period = 'Initial'

# Show continuous series across initial and recovery, marking date of cutoff with vertical line
subset = all_data[pd.to_datetime(all_data['Date']).dt.date <= datetime.date(2020, 5, 3)].reset_index(drop=True)
subset2 = all_data[pd.to_datetime(all_data['Date']).dt.date > datetime.date(2020, 4, 23)].reset_index(drop=True)

titles = ['Extreme', 'Severe', 'Mild']
xlims = [datetime.date(2020,1,1), datetime.date(2020,5,2)]
fig, axes = plt.subplots(1,3, figsize=(12,4), sharey=True)
for i in range(3):
    countries = full_cluster_mapping[full_cluster_mapping[period]==i]['Country'].values
    for country in countries:
        axes[i].plot(pd.to_datetime(subset['Date']), subset[country], color='C0', alpha=0.5, zorder=2)
    axes[i].plot(pd.to_datetime(subset['Date']), subset.loc[:, countries].mean(axis=1), color='k', zorder=3, label='Cluster Center')
    print(titles[i]+' Low Point: ', np.round(subset.loc[:, countries].mean(axis=1).min(), 2))
    print(titles[i]+' Mean: ', np.round(subset.loc[:, countries].mean(axis=1).mean(),2))
    print(titles[i]+' End Point: ', np.round(subset.loc[:, countries].mean(axis=1).values[-1],2))
    axes[i].axhline(color='k', alpha=0.3, zorder=1)
    axes[i].axvline(datetime.date(2020,4,28), color='k', alpha=0.7, zorder=1)
    axes[i].xaxis.set_major_locator(mdates.MonthLocator())
    axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    axes[i].set_ylim([-28, 10])
    axes[i].set_xlim(xlims)
    axes[i].set_title(titles[i], fontsize=16, fontname='Arial')
    if i == 0:
        axes[i].set_ylabel('Weekly % chg electricity consumption', fontsize=12, fontname='Arial')
    axes[i].set_xlabel('Date', fontsize=12, fontname='Arial')
    plt.xticks(fontname='Arial', fontsize=12)
    
plt.tight_layout()
plt.savefig('../Figures/fig4a_timeseries_Initial_transition.pdf', bbox_inches='tight')
plt.show()

period = 'Recovery'

subset2 = all_data[pd.to_datetime(all_data['Date']).dt.date <= datetime.date(2020, 5, 3)].reset_index(drop=True)
subset = all_data[pd.to_datetime(all_data['Date']).dt.date > datetime.date(2020, 4, 23)].reset_index(drop=True)

titles = ['Slow', 'Quick', 'Recovered']
xlims = [datetime.date(2020,4,25), datetime.date(2020,10,27)]

fig, axes = plt.subplots(1,3, figsize=(12,4), sharey=True)

for i in range(3):
    countries = full_cluster_mapping[full_cluster_mapping[period]==i]['Country'].values
    for country in countries:
        axes[i].plot(pd.to_datetime(subset['Date']), subset[country], color='C0', alpha=0.5, zorder=2)
    axes[i].plot(pd.to_datetime(subset['Date']), subset.loc[:, countries].mean(axis=1), color='k', zorder=3, label='Cluster Center')
    print(titles[i]+' Low Point: ', np.round(subset.loc[:, countries].mean(axis=1).min(), 2))
    print(titles[i]+' Mean: ', np.round(subset.loc[:, countries].mean(axis=1).mean(),2))
    print(titles[i]+' End Point: ', np.round(subset.loc[:, countries].mean(axis=1).values[-1],2))
    axes[i].axhline(color='k', alpha=0.3, zorder=1)
    axes[i].axvline(datetime.date(2020,4,28), color='k', alpha=0.7, zorder=1)
    axes[i].xaxis.set_major_locator(mdates.MonthLocator())
    axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    axes[i].set_ylim([-28, 10])
    axes[i].set_xlim(xlims)
    axes[i].set_title(titles[i], fontsize=16, fontname='Arial')
    if i == 0:
        axes[i].set_ylabel('Weekly % chg electricity consumption', fontsize=12, fontname='Arial')
    axes[i].set_xlabel('Date', fontsize=12, fontname='Arial')
    plt.xticks(fontname='Arial', fontsize=12)
plt.tight_layout()
plt.savefig('../Figures/fig4b_timeseries_Recovery_transition.pdf', bbox_inches='tight')
plt.show()
    