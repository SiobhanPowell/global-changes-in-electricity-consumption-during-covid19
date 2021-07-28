import pandas as pd
import numpy as np

population_mapping = pd.read_csv('../Data/Raw/county_eiaregion_population_mapping.csv', index_col=0)  
region_list = ['Region_MIDW', 'Region_CAR', 'Region_NE', 'Region_NW', 'Region_SW', 'Region_CENT', 'Region_TEN', 'Region_FLA',
               'Region_CAL', 'Region_SE', 'Region_TEX', 'Region_NY', 'Region_MIDA']

"""Mobility Calculation

For each region: 
- Prepare an empty df for the mobility dataset
- Find the matching region ID in the eia_map table
- Calculate what fraction of that regions population falls under each state
- For each state, load its mobility dataset and add it (with a weight for population) to the region dataset
- Append the region dataset to the overall set
"""
mobility = pd.read_csv('../Data/Raw/Global_Mobility_Report_dec2020.csv')

for region in region_list:

    new_mobility = mobility.loc[(mobility['country_region']=='United States')&(mobility['sub_region_1']!=mobility['sub_region_1'])].copy(deep=True).reset_index(drop=True)
    new_mobility['sub_region_1'] = region
    new_mobility.loc[:, new_mobility.columns[8:]] = 0

    subset = population_mapping[population_mapping['Region_name']==region]
    states_here = list(set(subset['State_name']))
    pops_here = []
    for state in states_here:
        pops_here.append(subset.loc[subset.loc[subset['State_name']==state].index, 'Population'].sum())
    popdf = pd.DataFrame({'State':states_here, 'Population':pops_here})
    popdf['Population Fraction'] = popdf['Population'] / popdf['Population'].sum()

    for j in popdf.index:
        subset = mobility.loc[(mobility['country_region']=='United States')&(mobility['sub_region_1']==popdf.loc[j, 'State'])&(mobility['sub_region_2']!=mobility['sub_region_2'])&(mobility['metro_area']!=mobility['metro_area'])]
        new_mobility.loc[:, new_mobility.columns[8:]] += popdf.loc[j, 'Population Fraction'] * subset.loc[:, subset.columns[8:]].values

    mobility = pd.concat((mobility, new_mobility), ignore_index=True).reset_index(drop=True)    
    
mobility.to_csv('../Data/Raw/Global_Mobility_Report_dec2020_edited.csv')

"""Oxford Index for Confinement and government restrictions.

For each region, follow same process as above. Save four data columns."""

oxford_other = pd.read_csv('../Data/Raw/OxCGRT_latest.csv')
oxford_other['CAll'] = oxford_other['C1_School closing'] + oxford_other['C2_Workplace closing'] + oxford_other['C6_Stay at home requirements'] + oxford_other['C7_Restrictions on internal movement']

for region in region_list:

    subset = population_mapping[population_mapping['Region_name']==region]
    states_here = list(set(subset['State_name']))
    pops_here = []
    for state in states_here:
        pops_here.append(subset.loc[subset.loc[subset['State_name']==state].index, 'Population'].sum())
    popdf = pd.DataFrame({'State':states_here, 'Population':pops_here})
    popdf['Population Fraction'] = popdf['Population'] / popdf['Population'].sum()

    total_sip = np.zeros((321, ))
    energy_sip = np.zeros((321, ))
    e1_series = np.zeros((321, ))
    e2_series = np.zeros((321, ))
    eindex_series = np.zeros((321, ))
    for j in popdf.index:
        if popdf.loc[j, 'State'] == 'District of Columbia':
            subset = oxford_other.loc[(oxford_other['CountryName']=='United States')&(oxford_other['RegionName']=='Washington DC')].reset_index(drop=True).loc[0:320, :]
        else:
            subset = oxford_other.loc[(oxford_other['CountryName']=='United States')&(oxford_other['RegionName']==popdf.loc[j, 'State'])].reset_index(drop=True).loc[0:320, :]
        total_sip += popdf.loc[j, 'Population Fraction'] * subset['StringencyIndex'].values
        energy_sip += popdf.loc[j, 'Population Fraction'] * subset['CAll'].values
        e1_series += popdf.loc[j, 'Population Fraction'] * subset['E1_Income support']
        e2_series += popdf.loc[j, 'Population Fraction'] * subset['E2_Debt/contract relief']
        eindex_series += popdf.loc[j, 'Population Fraction'] * subset['EconomicSupportIndex']
        
    
    oxford_df = {'Date':subset['Date'].values, 'StringencyIndex':total_sip, 'CAll':energy_sip, 'EconomicSupportIndex':eindex_series, 'E1_Income support':e1_series, 'E2_Debt/contract relief':e2_series}
    pd.DataFrame(oxford_df).to_csv('../Data/Intermediate/oxford_'+region+'.csv')
    
"""Sectoral breakdown: weight values by population in each state and from each state."""

df = pd.read_excel('../Data/Raw/us_state_sector_data.xlsx', header=1)
df['State name'] = ['Alaska', 'Alabama', 'Arkansas', 'Arizona', 'California', 'Colorado', 'Connecticut', 'District of Columbia', 
                    'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Iowa', 'Idaho', 'Illinois', 'Indiana', 'Kansas', 'Kentucky', 
                    'Louisiana', 'Massachusetts', 'Maryland', 'Maine', 'Michigan', 'Minnesota', 'Missouri', 'Mississippi', 
                    'Montana', 'North Carolina', 'North Dakota', 'Nebraska', 'New Hampshire', 'New Jersey', 'New Mexico', 
                    'Nevada', 'New York', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 
                    'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Virginia', 'Vermont', 'Washington', 'Wisconsin', 'West Virginia', 'Wyoming', 'US']

# Per capita values
cols = ['Residential', 'Commercial', 'Industrial', 'Transportation', 'Other', 'Total']
df_percapita = df.loc[0:51, :].copy(deep=True)
for i in df_percapita.index:
    state = df_percapita.loc[i, 'State name']
    pop = population_mapping[population_mapping['State_name']==state]['Population'].sum()
    df_percapita.loc[i, cols] = df.loc[i, cols] / pop

# Calculate sectoral breakdown for each region
sector_by_region = pd.DataFrame({'region':region_list})
for col in cols:
    sector_by_region[col] = 0
for i in sector_by_region.index:
    region = sector_by_region.loc[i, 'region']
    # Find population fractions
    subset = population_mapping[population_mapping['Region_name']==region]
    states_here = list(set(subset['State_name']))
    pops_here = []
    pop_fractions_here = []
    for state in states_here:
        pops_here.append(subset.loc[subset.loc[subset['State_name']==state].index, 'Population'].sum())
    popdf = pd.DataFrame({'State':states_here, 'Population':pops_here})
    
    # Calculate total using per capita
    for j in popdf.index:
        for col in cols:
            sector_by_region.loc[i, col] += popdf.loc[j, 'Population'] * df_percapita.loc[df_percapita[df_percapita['State name']==popdf.loc[j, 'State']].index, col].values[0]        
sector_by_region = sector_by_region.fillna(0)
sector_by_region.to_csv('../Data/Intermediate/sector_by_region_US.csv', index=False)


"""Health calculation."""
# See next file in R
