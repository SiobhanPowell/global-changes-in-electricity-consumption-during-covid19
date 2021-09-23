import pandas as pd
import numpy as np
import datetime

# just countries:
country_list = ['Argentina' 'Australia' 'Austria' 'Belgium' 'Brazil' 'Bulgaria' 'Canada'
 'Chile' 'China' 'Croatia' 'Czech_Republic' 'Denmark' 'Estonia' 'Finland'
 'France' 'Germany' 'Greece' 'Hungary' 'India' 'Ireland' 'Italy' 'Japan'
 'Kenya' 'Latvia' 'Lithuania' 'Mexico' 'Netherlands' 'New_Zealand'
 'Norway' 'Poland' 'Portugal' 'Romania' 'Russia' 'Serbia' 'Singapore'
 'Slovakia' 'Slovenia' 'South Africa' 'Spain' 'Sweden' 'Switzerland'
 'Thailand' 'USA' 'Ukraine' 'United-Kingdom']
# countries and regions (three within canada, 10 within us):
country_region_list = ['Alberta' 'Australia' 'Austria' 'Belgium' 'Brazil' 'British_Columbia'
 'Bulgaria' 'Chile' 'Croatia' 'Czech_Republic' 'Denmark' 'Estonia'
 'Finland' 'France' 'Germany' 'Greece' 'Hungary' 'India' 'Ireland' 'Italy'
 'Japan' 'Latvia' 'Lithuania' 'Mexico' 'Netherlands' 'New_Zealand'
 'Norway' 'Ontario' 'Poland' 'Portugal' 'Region_CAL' 'Region_CAR'
 'Region_CENT' 'Region_FLA' 'Region_MIDA' 'Region_MIDW' 'Region_NE'
 'Region_NW' 'Region_NY' 'Region_SE' 'Region_TEN' 'Region_TEX' 'Romania'
 'Russia' 'Serbia' 'Singapore' 'Slovakia' 'Slovenia' 'Spain' 'Sweden'
 'Switzerland' 'Ukraine' 'United-Kingdom']

# ----------
# Process data for each country

# Sector breakdown
sector_notUS = pd.read_excel('../Data/Raw/Sectors.xlsx', header=4)
sector_notUS.loc[sector_notUS[sector_notUS['Country']=='Russian Federation'].index, 'Country'] = 'Russia'
sector_notUS.loc[sector_notUS[sector_notUS['Country']=='New Zealand'].index, 'Country'] = 'New_Zealand'
sector_notUS.loc[sector_notUS[sector_notUS['Country']=='Czech Republic'].index, 'Country'] = 'Czech_Republic'
sector_notUS = sector_notUS.loc[0:38]
sector_notUS = sector_notUS.fillna(0)
sector_notUS['Other'] = sector_notUS['Agriculture / forestry'] + sector_notUS['Non-specified'] + sector_notUS['Fishing']
sector = sector_notUS.loc[:, ['Country', 'Industry', 'Residential', 'Transport', 'Commercial and public services', 'Other']].copy(deep=True)
# Calculate fractions:
for i in sector.index:
    sector.loc[i, sector.columns[1:]] = sector.loc[i, sector.columns[1:]] / sector.loc[i, sector.columns[1:]].sum()
sectorUS = pd.read_csv('../Data/Intermediate/sector_by_region_US.csv')
sectorUS.rename(columns = {'region':'Country', 'Commercial':'Commercial and public services', 
                           'Industrial':'Industry', 'Transportation':'Transport'}, inplace = True)
for i in sectorUS.index:
    sectorUS.loc[i, sectorUS.columns[1:-1]] = sectorUS.loc[i, sectorUS.columns[1:-1]] / sectorUS.loc[i, sectorUS.columns[1:-1]].sum()

sector = pd.concat((sector, sectorUS.loc[:, sectorUS.columns[:-1]]), axis=0, ignore_index=True, sort=True).reset_index(drop=True)
sector.to_csv('../Data/Intermediate/all_sector_data.csv', index=None)

# Health data
covid_deaths = pd.read_csv('../Data/Raw/covid.deaths.global.csv')
covid_cases = pd.read_csv('../Data/Raw/covid.cases.global.csv')
pop_data = pd.read_excel('../Data/Raw/population_analysis.xlsx')
pop_data = pop_data.loc[:, pop_data.columns[0:2]].dropna(axis=0)
pop_data.loc[54, 'Country/Region'] = 'Australia'
pop_data.loc[54, 'Population (thousands)'] = pop_data.loc[40:44, 'Population (thousands)'].sum()
pop_data.loc[55, 'Country/Region'] = 'Japan'
pop_data.loc[55, 'Population (thousands)'] = 126264.931 # https://data.worldbank.org/indicator/SP.POP.TOTL?locations=JP
pop_data.loc[56, 'Country/Region'] = 'British_Columbia' # statcan https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000501&pickMembers%5B0%5D=1.11&pickMembers%5B1%5D=2.1&cubeTimeFrame.startYear=2016&cubeTimeFrame.endYear=2020&referencePeriods=20160101%2C20200101
pop_data.loc[56, 'Population (thousands)'] = 5147.712
pop_data.loc[57, 'Country/Region'] = 'Ontario'
pop_data.loc[57, 'Population (thousands)'] = 14734.014
pop_data.loc[58, 'Country/Region'] = 'Alberta'
pop_data.loc[58, 'Population (thousands)'] = 4421.876

xvals = pd.date_range(start="2020-01-22",end="2020-11-14")
per_100k_df_deaths = {'date':xvals}
per_100k_df_cases = {'date':xvals}

cluster_mapping = pd.read_csv('../Data/Intermediate/cluster_mapping_initial_recovery.csv', index_col=0)
for i in range(3):
    countries = cluster_mapping[cluster_mapping['Initial']==i]['Country'].values
    for country in countries:
        country2 = country
        if country == 'New_Zealand':
            country = 'New Zealand'
            country2 = 'New Zealand'
        if country == 'United-Kingdom':
            country = 'United Kingdom'
            country2 = 'United Kingdom'
        if country == 'Czech_Republic':
            country = 'Czechia'
            country2 = 'Czech Republic'
        if (country in covid_deaths['Country.Region'].values)&(country2 in pop_data['Country/Region'].values):
            pop = pop_data[pop_data['Country/Region']==country2]['Population (thousands)'].values[0] * 1000
            subset = covid_deaths.loc[(covid_deaths['Country.Region']==country)&(covid_deaths['Province.State']!=covid_deaths['Province.State'])]
            if len(subset) == 0:
                subset = covid_deaths.loc[(covid_deaths['Country.Region']==country)].sum(axis=0)
                per_100k_df_deaths[country2] = (100000)*(1/pop)*subset.loc[covid_deaths.columns[4:]].values.ravel()[np.arange(0, len(xvals))]
            else:
                per_100k_df_deaths[country2] = (100000)*(1/pop)*subset.loc[:, covid_deaths.columns[4:]].values.ravel()[np.arange(0, len(xvals))]
            subset = covid_cases.loc[(covid_cases['Country.Region']==country)&(covid_cases['Province.State']!=covid_cases['Province.State'])]
            if len(subset) == 0:
                subset = covid_cases.loc[(covid_cases['Country.Region']==country)].sum(axis=0)
                per_100k_df_cases[country2] = (100000)*(1/pop)*subset.loc[covid_cases.columns[4:]].values.ravel()[np.arange(0, len(xvals))]
            else:
                per_100k_df_cases[country2] = (100000)*(1/pop)*subset.loc[:, covid_cases.columns[4:]].values.ravel()[np.arange(0, len(xvals))]
             
        elif country == 'British_Columbia':
            pop = pop_data[pop_data['Country/Region']==country2]['Population (thousands)'].values[0] * 1000
            subset = covid_deaths.loc[(covid_cases['Country.Region']=='Canada')&(covid_deaths['Province.State']=='British Columbia')]
            per_100k_df_deaths[country2] = (100000)*(1/pop)*subset.loc[:, covid_deaths.columns[4:]].values.ravel()[np.arange(0, len(xvals))]
            
            subset = covid_cases.loc[(covid_cases['Country.Region']=='Canada')&(covid_cases['Province.State']=='British Columbia')]
            per_100k_df_cases[country2] = (100000)*(1/pop)*subset.loc[:, covid_cases.columns[4:]].values.ravel()[np.arange(0, len(xvals))]
            
        elif country in ['Ontario', 'Alberta']:
            pop = pop_data[pop_data['Country/Region']==country2]['Population (thousands)'].values[0] * 1000
            subset = covid_deaths.loc[(covid_cases['Country.Region']=='Canada')&(covid_deaths['Province.State']=='Ontario')]
            per_100k_df_deaths[country2] = (100000)*(1/pop)*subset.loc[:, covid_deaths.columns[4:]].values.ravel()[np.arange(0, len(xvals))]
            
            subset = covid_cases.loc[(covid_cases['Country.Region']=='Canada')&(covid_cases['Province.State']=='Ontario')]
            per_100k_df_cases[country2] = (100000)*(1/pop)*subset.loc[:, covid_cases.columns[4:]].values.ravel()[np.arange(0, len(xvals))]
        else:
            print(country)

per_100k_df_deaths = pd.DataFrame(per_100k_df_deaths)
per_100k_df_cases = pd.DataFrame(per_100k_df_cases)
per_100k_df_deaths.to_csv('../Data/Intermediate/deaths_per100k_notUS.csv', index=False)
per_100k_df_cases.to_csv('../Data/Intermediate/cases_per100k_notUS.csv', index=False)

health_uscases = pd.read_csv('../Data/Intermediate/cases_per100k_US.csv')
health_nonuscases = pd.read_csv('../Data/Intermediate/cases_per100k_notUS.csv')
health_usdeaths = pd.read_csv('../Data/Intermediate/deaths_per100k_US.csv')
health_nonusdeaths = pd.read_csv('../Data/Intermediate/deaths_per100k_notUS.csv')

health_cases = pd.concat((health_nonuscases, health_uscases.loc[:, health_uscases.columns[1:]]), axis=1)
health_deaths = pd.concat((health_nonusdeaths, health_usdeaths.loc[:, health_usdeaths.columns[1:]]), axis=1)

health_dailycases = health_cases.loc[1:290, :].copy(deep=True)
health_dailycases.loc[:, health_dailycases.columns[1:]] = health_dailycases.loc[:, health_dailycases.columns[1:]] - health_cases.loc[0:289, health_cases.columns[1:]].values

health_dailydeaths = health_deaths.loc[1:290, :].copy(deep=True)
health_dailydeaths.loc[:, health_dailydeaths.columns[1:]] = health_dailydeaths.loc[:, health_dailydeaths.columns[1:]] - health_deaths.loc[0:289, health_dailydeaths.columns[1:]].values

# Mobility
mobility = pd.read_csv('../Data/Raw/Global_Mobility_Report_dec2020_edited.csv', index_col=0)

# Confinement
oxford = pd.read_csv('../Data/Raw/OxCGRT_latest.csv')
oxford['CAll'] = oxford['C1_School closing'] + oxford['C2_Workplace closing'] + oxford['C6_Stay at home requirements'] + oxford['C7_Restrictions on internal movement']

# GDP
econ_df = pd.read_csv('../Data/Raw/QNA_20122020160508960.csv')
econ_mapping2 = cluster_mapping.copy(deep=True)
econ_mapping2['Q2-2020 change in GDP since Q1'] = np.nan
for i in econ_mapping2.index:
    country = econ_mapping2.loc[i, 'Country']
    country2 = country
    if country == 'Slovakia':
        country2 = 'Slovak Republic'
    elif country == 'New_Zealand':
        country2 = 'New Zealand'
    elif country == 'United-Kingdom':
        country2 = 'United Kingdom'
    if country2 in set(econ_df['Country']):
        econ_mapping2.loc[i, 'Q2-2020 change in GDP since Q2-2019'] = econ_df.loc[(econ_df['Country']==country2)&(econ_df['SUBJECT']=='B1_GE')&(econ_df['MEASURE']=='GYSA')&(econ_df['Frequency']=='Quarterly')&(econ_df['TIME']=='2020-Q2')]['Value'].values[0]
        econ_mapping2.loc[i, 'Q3-2020 change in GDP since Q3-2019'] = econ_df.loc[(econ_df['Country']==country2)&(econ_df['SUBJECT']=='B1_GE')&(econ_df['MEASURE']=='GYSA')&(econ_df['Frequency']=='Quarterly')&(econ_df['TIME']=='2020-Q3')]['Value'].values[0]
        econ_mapping2.loc[i, 'Q3-2020 change in GDP since Q2-2020'] = econ_df.loc[(econ_df['Country']==country2)&(econ_df['SUBJECT']=='B1_GE')&(econ_df['MEASURE']=='GPSA')&(econ_df['Frequency']=='Quarterly')&(econ_df['TIME']=='2020-Q3')]['Value'].values[0]
        
        
states = pd.read_excel('../Data/Raw/qgdpstate1220_0.xlsx', sheet_name='Table 3', header=4)
states['State'] = states['Unnamed: 0'].str.strip()
population_mapping = pd.read_csv('../Data/Raw/county_eiaregion_population_mapping.csv', index_col=0)  
region_list = ['Region_MIDW', 'Region_CAR', 'Region_NE', 'Region_NW', 'Region_SW', 'Region_CENT', 'Region_TEN', 'Region_FLA',
               'Region_CAL', 'Region_SE', 'Region_TEX', 'Region_NY', 'Region_MIDA']
for i in population_mapping.index:
    if population_mapping.loc[i, 'State_name'] not in states['State'].values:
        print(population_mapping.loc[i, 'State_name'])
        
for region in region_list:

    subset = population_mapping[population_mapping['Region_name']==region]
    states_here = list(set(subset['State_name']))
    pops_here = []
    for state in states_here:
        pops_here.append(subset.loc[subset.loc[subset['State_name']==state].index, 'Population'].sum())
    popdf = pd.DataFrame({'State':states_here, 'Population':pops_here})
    popdf['Population Fraction'] = popdf['Population'] / popdf['Population'].sum()

    val = 0
    val2 = 0
    val3 = 0
    for j in popdf.index:
        subset = states.loc[(states['State']==popdf.loc[j, 'State'])].reset_index(drop=True)
        i=0
        valhere = 100*(subset.loc[i, 'Q2.1'] - subset.loc[i, 'Q2'])/subset.loc[i, 'Q2']
        valhere2 = 100*(subset.loc[i, 'Q3.1'] - subset.loc[i, 'Q3'])/subset.loc[i, 'Q3']
        valhere3 = 100*(subset.loc[i, 'Q3.1'] - subset.loc[i, 'Q2.1'])/subset.loc[i, 'Q2.1']
        val += popdf.loc[j, 'Population Fraction'] * valhere
        val2 += popdf.loc[j, 'Population Fraction'] * valhere2
        val3 += popdf.loc[j, 'Population Fraction'] * valhere3
        
    econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']==region].index, 'Q2-2020 change in GDP since Q2-2019'] = val
    econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']==region].index, 'Q3-2020 change in GDP since Q3-2019'] = val2
    econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']==region].index, 'Q3-2020 change in GDP since Q2-2020'] = val3
    
for country in ['Alberta', 'Ontario', 'British_Columbia']:
    country2 = 'Canada'
    i = econ_mapping2[econ_mapping2['Country']==country].index
    econ_mapping2.loc[i, 'Q2-2020 change in GDP since Q2-2019'] = econ_df.loc[(econ_df['Country']==country2)&(econ_df['SUBJECT']=='B1_GE')&(econ_df['MEASURE']=='GYSA')&(econ_df['Frequency']=='Quarterly')&(econ_df['TIME']=='2020-Q2')]['Value'].values[0]
    econ_mapping2.loc[i, 'Q3-2020 change in GDP since Q2-2020'] = econ_df.loc[(econ_df['Country']==country2)&(econ_df['SUBJECT']=='B1_GE')&(econ_df['MEASURE']=='GPSA')&(econ_df['Frequency']=='Quarterly')&(econ_df['TIME']=='2020-Q3')]['Value'].values[0]
    econ_mapping2.loc[i, 'Q3-2020 change in GDP since Q3-2019'] = econ_df.loc[(econ_df['Country']==country2)&(econ_df['SUBJECT']=='B1_GE')&(econ_df['MEASURE']=='GYSA')&(econ_df['Frequency']=='Quarterly')&(econ_df['TIME']=='2020-Q3')]['Value'].values[0]
    
# https://www.businesstimes.com.sg/government-economy/singapore-q2-gdp-plunges-by-132-in-worst-quarter-on-record
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Singapore'].index, 'Q2-2020 change in GDP since Q2-2019'] = -13.2

# https://www.total-croatia-news.com/business/46150-croatia-s-q2-gdp-contracts-by-record-high-15
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Croatia'].index, 'Q2-2020 change in GDP since Q2-2019'] = -15.1

# https://bbj.hu/economy/statistics/figures/serbia%CA%BCs-gdp-declines-in-q2
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Serbia'].index, 'Q2-2020 change in GDP since Q2-2019'] = -6.4

# https://www.focus-economics.com/countries/czech-republic/news/gdp/gdp-records-largest-drop-on-record-in-q2-amid-covid-19-health
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Czech_Republic'].index, 'Q2-2020 change in GDP since Q2-2019'] = -11

# https://www.focus-economics.com/countries/ukraine/news/gdp/gdp-contracts-at-fastest-pace-in-over-four-years-in-q2
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Ukraine'].index, 'Q2-2020 change in GDP since Q2-2019'] = -11.4


# https://www.focus-economics.com/countries/singapore/news/gdp/revised-estimate-reveals-softer-gdp-contraction-in-q3
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Singapore'].index, 'Q3-2020 change in GDP since Q3-2019'] = -5.8
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Singapore'].index, 'Q3-2020 change in GDP since Q2-2020'] = 9.2

# https://www.focus-economics.com/countries/croatia/news/gdp/gdp-contracts-at-softer-albeit-still-pronounced-pace-in-q3
# https://in.reuters.com/article/croatia-gdp-idINL1N2ID0IF
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Croatia'].index, 'Q3-2020 change in GDP since Q3-2019'] = -10.0
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Croatia'].index, 'Q3-2020 change in GDP since Q2-2020'] = 6.9

# https://seenews.com/news/serbias-gdp-shrinks-14-yy-in-q3-stats-office-722727
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Serbia'].index, 'Q3-2020 change in GDP since Q3-2019'] = -1.3
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Serbia'].index, 'Q3-2020 change in GDP since Q2-2020'] = 7.4

# https://www.focus-economics.com/countries/czech-republic/news/gdp/gdp-rebounds-in-q3-on-easing-restrictions
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Czech_Republic'].index, 'Q3-2020 change in GDP since Q3-2019'] = -5.8
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Czech_Republic'].index, 'Q3-2020 change in GDP since Q2-2020'] = 6.2

# https://www.focus-economics.com/countries/ukraine/news/gdp/gdp-contracts-at-fastest-pace-in-over-four-years-in-q2
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Ukraine'].index, 'Q3-2020 change in GDP since Q3-2019'] = -3.5
econ_mapping2.loc[econ_mapping2[econ_mapping2['Country']=='Ukraine'].index, 'Q3-2020 change in GDP since Q2-2020'] = 8.5


# Holidays
holidays_df = pd.read_csv('../Data/Intermediate/holiday_effect.csv')
holidays_df.loc[holidays_df[holidays_df['country']=='United-Kingdom'].index, 'country'] = 'United Kingdom'

# Save intermediate calculations
new_mappings = econ_mapping2.loc[:, ['Country', 'Cluster', 'Q2-2020 change in GDP since Q2-2019', 'Q3-2020 change in GDP since Q2-2020', 'Q3-2020 change in GDP since Q3-2019']].copy(deep=True)

new_mappings['Holiday Effect'] = np.nan
new_mappings.loc[new_mappings[new_mappings['Country']=='United-Kingdom'].index, 'Country'] = 'United Kingdom'
for i in new_mappings.index:
    country = new_mappings.loc[i, 'Country']
    country2 = country
#     if country == 'United Kingdom':
#         country2 = 'United-Kingdom'
    try:
        new_mappings.loc[i, 'Holiday Effect'] = holidays_df.loc[holidays_df[holidays_df['country']==country2].index, 'holiday_effect'].values[0]
    except:
        print(country2)
#     new_mappings.loc[i, 'Weekend Effect'] = weekends_df.loc[weekends_df[weekends_df['country']==country2].index, 'weekday_effect'].values[0]
        
new_mappings.to_csv('../Data/Intermediate/new_gdp_holidays_weekends.csv', index=None)

import os
try: 
    os.mkdir('../Data/Intermediate/summary_data')
except:
    print('summary_data folder already exists')
# Create full timeseries for each country
cluster_mapping = pd.read_csv('../Data/Intermediate/cluster_mapping_initial_recovery.csv', index_col=0)
cluster_mapping.loc[cluster_mapping[cluster_mapping['Country']=='United-Kingdom'].index, 'Country'] = 'United Kingdom'
full_date_set_recovery = pd.to_datetime(pd.DataFrame({'year':np.repeat(2020, 31+29+31+30+31+30+31+31+30+31), 'month':np.concatenate((np.repeat(1, 31), np.repeat(2,29), np.repeat(3,31), np.repeat(4,30), np.repeat(5,31), np.repeat(6, 30), np.repeat(7, 31), np.repeat(8, 31), np.repeat(9, 30), np.repeat(10, 31))),
                                         'day':np.concatenate((np.arange(1, 32), np.arange(1,30), np.arange(1,32), np.arange(1,31), np.arange(1,32), np.arange(1,31), np.arange(1,32), np.arange(1,32), np.arange(1,31), np.arange(1,32)))}))
for i in cluster_mapping.index:
    country = cluster_mapping.loc[i, 'Country']

    timevarying = pd.DataFrame({'Date': pd.date_range(start='2020-01-01', end='2020-11-01')})
    country2 = country
    if country == 'Czech_Republic':
        country2 = 'Czech Republic'
    elif country == 'New_Zealand':
        country2 = 'New Zealand'
    elif country == 'United-Kingdom':
        country2 = 'United Kingdom'
    if country == 'Slovakia':
        subset = oxford.loc[(oxford['CountryName']=='Slovak Republic')&(oxford['RegionName']!=oxford['RegionName'])].loc[:, ['CountryName', 'Date', 'StringencyIndex', 'CAll', 'E1_Income support', 'EconomicSupportIndex']]
    elif country in ['Ontario', 'British_Columbia', 'Alberta']:
        subset = oxford.loc[(oxford['CountryName']=='Canada')&(oxford['RegionName']!=oxford['RegionName'])].loc[:, ['CountryName', 'Date', 'StringencyIndex', 'CAll', 'E1_Income support', 'EconomicSupportIndex']]
    elif 'Region' in country:
        subset = pd.read_csv('../Data/Intermediate/oxford_'+country+'.csv')
    else:
        subset = oxford.loc[(oxford['CountryName']==country2)&(oxford['RegionName']!=oxford['RegionName'])].loc[:, ['CountryName', 'Date', 'StringencyIndex', 'CAll', 'E1_Income support', 'EconomicSupportIndex']]
    subset['Date'] = pd.to_datetime(subset['Date'], format='%Y%m%d')
    subset = subset.reset_index(drop=True)
    timevarying.loc[timevarying[timevarying['Date'].isin(subset['Date'])].index, 'Oxford'] = subset.loc[subset[subset['Date'].isin(timevarying['Date'])].index, 'StringencyIndex'].values
    timevarying.loc[timevarying[timevarying['Date'].isin(subset['Date'])].index, 'Oxford Energy'] = subset.loc[subset[subset['Date'].isin(timevarying['Date'])].index, 'CAll'].values
    
    timevarying.loc[timevarying[timevarying['Date'].isin(subset['Date'])].index, 'Oxford E1 Income support'] = subset.loc[subset[subset['Date'].isin(timevarying['Date'])].index, 'E1_Income support'].values
    timevarying.loc[timevarying[timevarying['Date'].isin(subset['Date'])].index, 'Oxford EconomicSupportIndex'] = subset.loc[subset[subset['Date'].isin(timevarying['Date'])].index, 'EconomicSupportIndex'].values
    # health metrics
    timevarying.loc[timevarying[timevarying['Date'].isin(pd.to_datetime(health_cases['date']))].index, 'Cumulative Cases per 100k'] = health_cases.loc[health_cases[pd.to_datetime(health_cases['date']).isin(timevarying['Date'])].index, country2].values
    timevarying.loc[timevarying[timevarying['Date'].isin(pd.to_datetime(health_deaths['date']))].index, 'Cumulative Deaths per 100k'] = health_deaths.loc[health_deaths[pd.to_datetime(health_deaths['date']).isin(timevarying['Date'])].index, country2].values
    timevarying.loc[timevarying[timevarying['Date'].isin(pd.to_datetime(health_dailycases['date']))].index, 'Daily Cases per 100k'] = health_dailycases.loc[health_dailycases[pd.to_datetime(health_dailycases['date']).isin(timevarying['Date'])].index, country2].values
    timevarying.loc[timevarying[timevarying['Date'].isin(pd.to_datetime(health_dailydeaths['date']))].index, 'Daily Deaths per 100k'] = health_dailydeaths.loc[health_dailydeaths[pd.to_datetime(health_dailydeaths['date']).isin(timevarying['Date'])].index, country2].values
    # mobility
    if country == 'Czech_Republic':
        subset = mobility.loc[(mobility['country_region']=='Czechia')&(mobility['sub_region_1']!=mobility['sub_region_1'])&(mobility['sub_region_2']!=mobility['sub_region_2'])&(mobility['metro_area']!=mobility['metro_area'])].reset_index(drop=True)
    elif country == 'New_Zealand':
        subset = mobility.loc[(mobility['country_region']=='New Zealand')&(mobility['sub_region_1']!=mobility['sub_region_1'])&(mobility['sub_region_2']!=mobility['sub_region_2'])&(mobility['metro_area']!=mobility['metro_area'])].reset_index(drop=True)
    elif country in ['Ontario', 'Alberta']:
        subset = mobility.loc[(mobility['country_region']=='Canada')&(mobility['sub_region_1']==country)&(mobility['sub_region_2']!=mobility['sub_region_2'])&(mobility['metro_area']!=mobility['metro_area'])].reset_index(drop=True)
    elif country == 'British_Columbia':
        subset = mobility.loc[(mobility['country_region']=='Canada')&(mobility['sub_region_1']=='British Columbia')&(mobility['sub_region_2']!=mobility['sub_region_2'])&(mobility['metro_area']!=mobility['metro_area'])].reset_index(drop=True)
    elif 'Region' in country:
        subset = mobility.loc[(mobility['country_region']=='United States')&(mobility['sub_region_1']==country)&(mobility['sub_region_2']!=mobility['sub_region_2'])&(mobility['metro_area']!=mobility['metro_area'])].reset_index(drop=True)
    else:
        subset = mobility.loc[(mobility['country_region']==country)&(mobility['sub_region_1']!=mobility['sub_region_1'])&(mobility['sub_region_2']!=mobility['sub_region_2'])&(mobility['metro_area']!=mobility['metro_area'])].reset_index(drop=True)
    for key, val in {'Retail and Recreation':'retail_and_recreation', 'Grocery and Pharmacy':'grocery_and_pharmacy', 'Parks':'parks','Transit Stations':'transit_stations', 'Workplaces':'workplaces', 'Residences':'residential'}.items():
        timevarying.loc[timevarying[timevarying['Date'].isin(pd.to_datetime(subset['date']))].index, 'Mobility: '+key] = subset.loc[subset[pd.to_datetime(subset['date']).isin(timevarying['Date'])].index, val+'_percent_change_from_baseline'].values

    if country == 'United Kingdom':
        df_subset = pd.read_csv('../Data/Intermediate/consumption_change_estimates/'+'United-Kingdom'+'_final.csv', index_col=0)
    else:
        df_subset = pd.read_csv('../Data/Intermediate/consumption_change_estimates/'+country+'_final.csv', index_col=0)
    df_subset = df_subset.rename(columns={'percent_red':'pct_change', 'percent_red_upper':'pct_upper', 'percent_red_lower':'pct_lower'})
    df_subset['Date'] = full_date_set_recovery[df_subset['day_2020']-1].values
    df_subset['Date'] = pd.to_datetime(df_subset['Date'])
    timevarying.loc[timevarying[timevarying['Date'].isin(pd.to_datetime(df_subset['Date']))].index, 'Pct Change in Electricity Demand'] = df_subset.loc[df_subset[pd.to_datetime(df_subset['Date']).isin(timevarying['Date'])].index, 'pct_change']


    final_timevarying = timevarying.loc[(timevarying['Date']>=pd.to_datetime('2020-01-01', format='%Y-%m-%d'))&(timevarying['Date']<=pd.to_datetime('2020-10-31', format='%Y-%m-%d'))].copy(deep=True).reset_index(drop=True)
    
    final_timevarying.to_csv('../Data/Intermediate/summary_data/'+country+'_timevarying_recovery_fixed.csv', index=None)
    if country == 'United Kingdom':
        final_timevarying.to_csv('../Data/Intermediate/summary_data/'+'United-Kingdom'+'_timevarying_recovery_fixed.csv', index=None)
        
    

# -------
# Data for panel regression
country_count = 0
df_ts_ref = pd.read_csv('../Data/Intermediate/summary_data/'+'Italy'+'_timevarying_recovery_fixed.csv')
df_ts_ref = df_ts_ref.loc[(pd.to_datetime(df_ts_ref['Date']).dt.date >= datetime.date(2020,2,15))&(pd.to_datetime(df_ts_ref['Date']).dt.date <= datetime.date(2020,4,28))].reset_index(drop=True)
panel_dataframe = pd.DataFrame({key:np.zeros((len(df_ts_ref)*53,)) for key in ['Country', 'Date', 'Initial Cluster', 'Recovery Cluster']})
for key in ['Country', 'Date', 'Initial Cluster', 'Recovery Cluster']:
    panel_dataframe[key] = np.nan

for clustnum in [0, 1, 2]:
    countries = cluster_mapping[cluster_mapping['Initial']==clustnum]['Country'].values
    for country in countries:
        df_ts = pd.read_csv('../Data/Intermediate/summary_data/'+country+'_timevarying_recovery_fixed.csv')
        df_ts = df_ts.loc[(pd.to_datetime(df_ts['Date']).dt.date >= datetime.date(2020,2,15))&(pd.to_datetime(df_ts['Date']).dt.date <= datetime.date(2020,4,28))].reset_index(drop=True)
        idx = np.arange(country_count*len(df_ts_ref), (country_count+1)*len(df_ts_ref))
        panel_dataframe.loc[idx, 'Country'] = country
        panel_dataframe.loc[idx, 'Date'] = df_ts['Date'].values
        panel_dataframe.loc[idx, 'Initial Cluster'] = clustnum+1
        panel_dataframe.loc[idx, 'Recovery Cluster'] = cluster_mapping[cluster_mapping['Country']==country]['Recovery'].values[0]+1
        for col in ['Oxford', 'Daily Cases per 100k', 'Daily Deaths per 100k', 'Mobility: Retail and Recreation','Mobility: Workplaces', 'Mobility: Residences', 'Mobility: Transit Stations',  'Mobility: Grocery and Pharmacy', 'Mobility: Parks', 'Pct Change in Electricity Demand']:
            panel_dataframe.loc[idx, col] = df_ts[col].values
        if country in ['Ontario', 'British_Columbia', 'Alberta']:
            idx2 = sector[sector['Country']=='Canada'].index.values[0]
        else:
            idx2 = sector[sector['Country']==country].index.values[0]
        for col in ['Commercial and public services', 'Industry', 'Residential']:
            try:
                panel_dataframe.loc[idx, 'Sector: '+col] = sector.loc[idx2, col]
            except:
                print(country)
                print(sector)
                panel_dataframe.loc[idx, 'Sector: '+col] = sector.loc[idx2, col]

        idx3 = new_mappings[new_mappings['Country']==country].index.values[0]
        for col in ['Q2-2020 change in GDP since Q2-2019', 'Q3-2020 change in GDP since Q3-2019', 'Holiday Effect']:
            panel_dataframe.loc[idx, col] = new_mappings.loc[idx3, col]

        country_count += 1
panel_dataframe.to_csv('../Data/Intermediate/panel_data.csv')

country_count = 0
df_ts_ref = pd.read_csv('../Data/Intermediate/summary_data/'+'Italy'+'_timevarying_recovery_fixed.csv')
df_ts_ref = df_ts_ref.loc[(pd.to_datetime(df_ts_ref['Date']).dt.date > datetime.date(2020,4,28))&(pd.to_datetime(df_ts_ref['Date']).dt.date <= datetime.date(2020,10,27))].reset_index(drop=True)
panel_dataframe = pd.DataFrame({key:np.zeros((len(df_ts_ref)*53,)) for key in ['Country', 'Date', 'Initial Cluster', 'Recovery Cluster']})
for key in ['Country', 'Date', 'Initial Cluster', 'Recovery Cluster']:
    panel_dataframe[key] = np.nan

for clustnum in [0, 1, 2]:
    countries = cluster_mapping[cluster_mapping['Initial']==clustnum]['Country'].values
    for country in countries:
        df_ts = pd.read_csv('../Data/Intermediate/summary_data/'+country+'_timevarying_recovery_fixed.csv')
        df_ts = df_ts.loc[(pd.to_datetime(df_ts['Date']).dt.date > datetime.date(2020,4,28))&(pd.to_datetime(df_ts['Date']).dt.date <= datetime.date(2020,10,27))].reset_index(drop=True)
        idx = np.arange(country_count*len(df_ts_ref), (country_count+1)*len(df_ts_ref))
        panel_dataframe.loc[idx, 'Country'] = country
        panel_dataframe.loc[idx, 'Date'] = df_ts['Date'].values
        panel_dataframe.loc[idx, 'Initial Cluster'] = clustnum+1
        panel_dataframe.loc[idx, 'Recovery Cluster'] = cluster_mapping[cluster_mapping['Country']==country]['Recovery'].values[0]+1
        for col in ['Oxford', 'Daily Cases per 100k', 'Daily Deaths per 100k', 'Mobility: Retail and Recreation','Mobility: Workplaces', 'Mobility: Residences', 'Mobility: Transit Stations',  'Mobility: Grocery and Pharmacy', 'Mobility: Parks', 'Pct Change in Electricity Demand']:
            panel_dataframe.loc[idx, col] = df_ts[col].values
        if country in ['Ontario', 'British_Columbia', 'Alberta']:
            idx2 = sector[sector['Country']=='Canada'].index.values[0]
        else:
            idx2 = sector[sector['Country']==country].index.values[0]
        for col in ['Commercial and public services', 'Industry', 'Residential']:
            panel_dataframe.loc[idx, 'Sector: '+col] = sector.loc[idx2, col]
        idx3 = new_mappings[new_mappings['Country']==country].index.values[0]
        for col in ['Q2-2020 change in GDP since Q2-2019', 'Q3-2020 change in GDP since Q3-2019', 'Holiday Effect']:
            panel_dataframe.loc[idx, col] = new_mappings.loc[idx3, col]

        country_count += 1
panel_dataframe.to_csv('../Data/Intermediate/panel_data_recovery.csv')
