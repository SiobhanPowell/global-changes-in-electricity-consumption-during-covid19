################################## Preliminaries
library(tidyverse)
library(reshape2)
library(data.table)
library(stringr)
library(lubridate)
library(mvtnorm)
library(latex2exp)
library(scales)
library(readxl)

################################## Read in COVID case data

# (Originally read in 2020)
covid.cases.global = read.csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', header = T)
write.csv(covid.cases.global, '../Data/Raw/covid.cases.global.csv', row.names = F)
covid.deaths.global = read.csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv', header = T)
write.csv(covid.deaths.global, '../Data/Raw/covid.deaths.global.csv', row.names = F)
covid.cases.us = read.csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv', header = T)
covid.deaths.us = read.csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv', header = T)

################################## Read in cluster mapping and EIA mapping files
# setwd('~/Google Drive File Stream/My Drive/Research Stuff/Covid and the Grid/Covid_power_website')
setwd('..')
cluster.mapping = read.csv('Data/Intermediate/cluster_mapping_initial_recovery.csv')
eia_county_xwalk = 
  read.csv('Data/Raw/EIA_region_by_county_covid_orders.csv', header = T) %>%
  select(Geo_FIPS, State, County_name, ID, Population)
eia_id_name_xwalk = read.csv('Data/Raw/eia_matching_table.csv', header = T)
eia_county_name_xwalk = 
  merge(eia_county_xwalk, eia_id_name_xwalk, by = 'ID')

################################## Reshape and merge with cluster file

covid.cases.global.long = 
  select(covid.cases.global, -Lat, -Long) %>%
  melt(id.vars = c('Country.Region','Province.State')) %>%
  mutate(
    date.char = gsub('X','', variable),
    date = as.Date(date.char, '%m.%d.%y')
  )

covid.deaths.global.long = 
  select(covid.deaths.global, -Lat, -Long) %>%
  melt(id.vars = c('Country.Region','Province.State')) %>%
  mutate(
    date.char = gsub('X','', variable),
    date = as.Date(date.char, '%m.%d.%y')
  )

covid.cases.us.wide = 
  select(
    covid.cases.us, 
    -UID, -iso2, -iso3, -code3,        
    -Admin2, -Province_State, -Country_Region, -Lat,  -Long_,  
    -Combined_Key
  ) %>%
  melt(id.vars = 'FIPS') %>%
  mutate(
    date.char = gsub('X','', variable),
    date = as.Date(date.char, '%m.%d.%y')
  ) %>%
  select(FIPS, date, value) %>%
  merge(eia_county_name_xwalk,  by.x = 'FIPS', by.y = 'Geo_FIPS', all = F) %>%
  dplyr::group_by(Region.Name, date) %>%
  dplyr::summarise(
    tot.pop = sum(Population),
    tot.cases = sum(value)
  ) %>%
  mutate(rate.per.100k = tot.cases/tot.pop*1E5) %>%
  dcast(date ~ Region.Name, value.var = 'rate.per.100k')
write.csv(covid.cases.us.wide, 'Data/Intermediate/cases_per100k_US.csv', row.names = F)

covid.deaths.us.wide = 
  select(
    covid.deaths.us, 
    -UID, -iso2, -iso3, -code3,        
    -Admin2, -Province_State, -Country_Region, -Lat,  -Long_,  
    -Combined_Key
  ) %>%
  melt(id.vars = c('FIPS','Population')) %>%
  mutate(
    date.char = gsub('X','', variable),
    date = as.Date(date.char, '%m.%d.%y')
  ) %>%
  select(FIPS, date, value) %>%
  merge(eia_county_name_xwalk,  by.x = 'FIPS', by.y = 'Geo_FIPS', all = F) %>%
  dplyr::group_by(Region.Name, date) %>%
  dplyr::summarise(
    tot.pop = sum(Population),
    tot.deaths = sum(value)
  ) %>%
  mutate(rate.per.100k = tot.deaths/tot.pop*1E5) %>%
  dcast(date ~ Region.Name, value.var = 'rate.per.100k')
write.csv(covid.deaths.us.wide, 'Data/Intermediate/deaths_per100k_US.csv', row.names = F)

