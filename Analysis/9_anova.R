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

################################## Read in cluster mapping and EIA mapping files
setwd('..')
cluster.mapping = read.csv('Data/Intermediate/cluster_mapping_initial_recovery.csv')
sector_data = 
  read.csv('Data/Intermediate/all_sector_data.csv', header = T) %>% 
  merge(cluster.mapping, by = 'Country') %>% 
  select(Country, Commercial.and.public.services, Residential, Industry, Transport, Other)

holiday_weekend_gdp = read.csv('Data/Intermediate/new_gdp_holidays_weekends.csv') 

geographies = as.character(cluster.mapping$Country)
panel.data =
  lapply(geographies, function(geography_){
    print(geography_)
    fname = paste0('Data/Intermediate/summary_data/', geography_,'_timevarying_recovery_fixed.csv')
    read.csv(fname, header = T) %>% mutate(Country = geography_)
  }) %>%
  bind_rows() %>%
  mutate(Date = as.Date(Date))

all.cluster.data = 
  merge(panel.data, holiday_weekend_gdp, by = 'Country') %>% 
  merge(cluster.mapping, by = 'Country') %>%
  mutate(Date = as.Date(Date)) %>%
  bind_rows(merge(sector_data, cluster.mapping, by = 'Country'))

###################### Helper functions
get.anova = function(variable, cluster_period){
  print(variable)
  if (variable %in% c("Commercial.and.public.services","Residential","Industry","Transport","Other")){
    all.cluster.data$variable = all.cluster.data[,variable]*100 
  } else{
    all.cluster.data$variable = all.cluster.data[,variable]
  }
  all.cluster.data$cluster = all.cluster.data[,cluster_period]
  means = dplyr::group_by(all.cluster.data, cluster, Country) %>% summarize(mean.variable = mean(variable, na.rm = T))
  if (cluster_period == 'Initial'){
    all.cluster.data.period = filter(all.cluster.data, Date <= as.Date('4-28-20','%m-%d-%y'))
    
  } else{
    all.cluster.data.period = filter(all.cluster.data, Date > as.Date('4-28-20','%m-%d-%y'))
  }
  if (variable %in%c("Commercial.and.public.services","Residential","Industry","Transport","Other")){
    all.cluster.data.period = all.cluster.data
  }
  cluster.means = 
    dplyr::group_by(all.cluster.data.period, cluster) %>% 
    summarize(mean.variable = mean(variable, na.rm = T)) %>%
    dcast(.~cluster)
  # Check significance of difference  
  mod = lm(mean.variable ~ as.factor(cluster), data = means) %>% summary()
  p_value = pf(mod$fstat['value'], mod$fstat['numdf'], mod$fstat['dendf'], lower.tail = F) 
  cluster.means$significance = case_when(
    p_value >= 0.05 ~ sprintf('%.3f', p_value),
    p_value < 0.05 & p_value >= 0.01 ~ paste0(sprintf('%.3f', p_value),'*'),
    p_value < 0.01 & p_value >= 0.001 ~ paste0(sprintf('%.3f', p_value),'**'),
    p_value < 0.001 ~ paste0(sprintf('%.3f', p_value),'***')
  )
  cluster.means$variable = variable
  cluster.means
}

get.TukeyHSD = function(variable, cluster_period) {
  print(variable)
  if (variable %in% c("Commercial.and.public.services","Residential","Industry","Transport","Other")){
    all.cluster.data$variable = all.cluster.data[,variable]*100 
  } else{
    all.cluster.data$variable = all.cluster.data[,variable]
  }
  all.cluster.data$cluster = all.cluster.data[,cluster_period]
  means = dplyr::group_by(all.cluster.data, cluster, Country) %>% summarize(mean.variable = mean(variable, na.rm = T))
  if (cluster_period == 'Initial'){
    all.cluster.data.period = filter(all.cluster.data, Date <= as.Date('4-28-20','%m-%d-%y'))
  } else{
    all.cluster.data.period = filter(all.cluster.data, Date > as.Date('4-28-20','%m-%d-%y'))
  }
  if (variable %in%c("Commercial.and.public.services","Residential","Industry","Transport","Other")){
    all.cluster.data.period = all.cluster.data
  }
  cluster.means = 
    dplyr::group_by(all.cluster.data.period, cluster) %>% 
    summarize(mean.variable = mean(variable, na.rm = T)) %>%
    dcast(.~cluster)
  mod.aov = lm(mean.variable ~ as.factor(cluster), data = means) %>% aov()
  tukeyhsd.results = TukeyHSD(mod.aov)$`as.factor(cluster)`
  results.df =  data.frame(tukeyhsd.results)
  results.df$cluster.pair = paste0('Clusters: ', row.names(tukeyhsd.results) %>% as.character())
  results.df$variable = variable
  results.df$significance = case_when(
    results.df$p.adj >= 0.05 ~ sprintf('%.3f', results.df$p.adj),
    results.df$p.adj < 0.05 & results.df$p.adj >= 0.01 ~ paste0(sprintf('%.3f', results.df$p.adj),'*'),
    results.df$p.adj < 0.01 & results.df$p.adj >= 0.001 ~ paste0(sprintf('%.3f', results.df$p.adj),'**'),
    results.df$p.adj < 0.001 ~ paste0(sprintf('%.3f', results.df$p.adj),'***')
  )
  select(results.df, variable, cluster.pair, diff, significance)
}

####################### Run analyses
variables = c(
  "Oxford","Oxford.Energy",
  "Pct.Change.in.Electricity.Demand",
  "Mobility..Workplaces","Mobility..Residences","Mobility..Transit.Stations",
  "Mobility..Grocery.and.Pharmacy","Mobility..Retail.and.Recreation","Mobility..Parks",
  "Q2.2020.change.in.GDP.since.Q2.2019","Q3.2020.change.in.GDP.since.Q2.2020","Q3.2020.change.in.GDP.since.Q3.2019",
  "Holiday.Effect",
  "Commercial.and.public.services","Residential","Industry","Transport","Other",
  "Daily.Cases.per.100k","Daily.Deaths.per.100k"
)
sumstats.anova.initial = 
  lapply(variables, function(variable){get.anova(variable, 'Initial')}) %>% 
  bind_rows() %>%
  select(variable,`0`,`1`,`2`, significance) %>% 
  mutate(variable = factor(variable, levels = variables)) %>%
  arrange(variable)

sumstats.anova.recovery = 
  lapply(variables, function(variable){get.anova(variable, 'Recovery')}) %>% 
  bind_rows() %>%
  select(variable,`0`,`1`,`2`, significance) %>% arrange(variable) %>%
  mutate(variable = factor(variable, levels = variables)) %>%
  arrange(variable)

sumstats.tukeyHSD.initial = 
  lapply(variables, function(variable){get.TukeyHSD(variable, 'Initial')}) %>% 
  bind_rows() %>%
  rename(variable_ = variable) %>%
  melt(id.vars = c('variable_','cluster.pair')) %>%
  dcast(variable_ ~ cluster.pair + variable) %>% arrange(variable_) %>%
  mutate(variable_ = factor(variable_, levels = variables)) %>%
  arrange(variable_)

sumstats.tukeyHSD.recovery = 
  lapply(variables, function(variable){get.TukeyHSD(variable, 'Recovery')}) %>% 
  bind_rows() %>%
  rename(variable_ = variable) %>%
  melt(id.vars = c('variable_','cluster.pair')) %>%
  dcast(variable_ ~ cluster.pair + variable) %>% arrange(variable_) %>%
  mutate(variable_ = factor(variable_, levels = variables)) %>%
  arrange(variable_)  

################### Output results
write.csv(sumstats.anova.initial,'Data/Intermediate/sumstats.anova.initial_3digits.csv', row.names = F )  
write.csv(sumstats.anova.recovery,'Data/Intermediate/sumstats.anova.recovery_3digits.csv', row.names = F )  
write.csv(sumstats.tukeyHSD.initial,'Data/Intermediate/sumstats.tukeyHSD.initial_3digits.csv', row.names = F )  
write.csv(sumstats.tukeyHSD.recovery,'Data/Intermediate/sumstats.tukeyHSD.recovery_3digits.csv', row.names = F )  


