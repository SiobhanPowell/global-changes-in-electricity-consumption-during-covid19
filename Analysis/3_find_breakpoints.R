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

############# Read in datasets
# root_dir = '/Volumes/GoogleDrive/My Drive/Research Stuff/Covid and the Grid'
setwd('..')#root_dir)
geographies = read_excel('Data/Raw/geography names dictionaries.xlsx')$geography
# setwd(paste0(root_dir,'/Daily_weekly_011120'))
# Weekly
weekly_data = 
  lapply(geographies, function(geography_){
    fname = paste0('Data/Intermediate/consumption_change_estimates/', geography_,'_final_week.csv')
    read.csv(fname, header = T) %>% mutate(geography = geography_)
  }) %>%
  bind_rows() %>%
  mutate(change = actual_weekly_mwh - pred_weekly_mwh) %>%
  group_by(week_2020) %>%
  summarize(sum.change = mean(percent_red, na.rm = T))

# Daily
daily_data = 
  lapply(geographies, function(geography_){
    fname = paste0('Data/Intermediate/consumption_change_estimates/', geography_,'_final.csv')
    read.csv(fname, header = T) %>% mutate(geography = geography_)
  }) %>%
  bind_rows() %>%
  mutate(change = actual_daily_mwh - pred_daily_mwh) %>%
  group_by(day_2020) %>%
  summarize(sum.change = mean(percent_red, na.rm = T))


################# Helper functions
library(genlasso)

# Extract best fit with given degrees of freedom
get_best_fit = function(df){
  df_error = data.frame(df = trends$df, err = trends.cv$err)
  best_err = min(df_error[df_error$df == df,'err'])
  best_fit = trends$fit[,which(df_error$err == best_err)]
}

get_tf_knots = function(fit, tol = 0.001){
  # Check whether slope before point is the same as slope after
  fit_next = c(fit[2:length(fit)], NA)
  fit_prev = c(NA, fit[1:(length(fit) - 1)])
  indices = which(abs((fit_next - fit) - (fit - fit_prev)) > tol)
  values = fit[indices]
  data.frame('week' = indices, 'value' = values)
}

######################### Weekly analysis
# Run fused lasso
trends = trendfilter(weekly_data$sum.change)
# Run cross validation
trends.cv = cv.trendfilter(trends)

desired_df = 3
weekly_data$best_fit = get_best_fit(desired_df)
ggplot(weekly_data, aes(week_2020, sum.change)) + 
  geom_point()+
  geom_line(aes(week_2020, best_fit), color = 'red')+
  labs(x = 'Week of 2020', y = 'Total consumption change (MWh)') + 
  theme_bw()
ggsave('Figures/breakpoints_weekly.png', height = 3, width = 5)

get_tf_knots(weekly_data$best_fit)
as.Date('1-1-20','%m-%d-%y') + 17*7

######################### Daily analysis
# Run fused lasso
trends = trendfilter(daily_data$sum.change)
# Run cross validation
trends.cv = cv.trendfilter(trends)
desired_df = 3
daily_data$best_fit = get_best_fit(desired_df)
ggplot(daily_data, aes(day_2020, sum.change)) + 
  geom_point(alpha = 0.4)+
  geom_line(aes(day_2020, best_fit), color = 'red')+
  labs(x = 'Day of 2020', y = 'Total consumption change (MWh)') + 
  theme_bw()
ggsave('Figures/breakpoints_daily.png', height = 3, width = 5)

get_tf_knots(daily_data$best_fit)
as.Date('12-31-19','%m-%d-%y') + 112
  