rm(list = ls())

library(ggplot2)
library(dplyr)

################################################################
# 1) Load data
################################################################
data_path <- "Clean_data/"

dataset <- read.csv(paste0(data_path,"Argentina.csv"),stringsAsFactors = F)

# Correct variable for years
dataset$year <- as.character(dataset$year)

################################################################
# 2) Various plots to visualise the data
################################################################
# # Load timeseries
# dataset$month <- as.numeric(dataset$month)
# p <- ggplot(dataset, aes(x = month, y = load, col = year))
# p <- p + geom_line()
# p
# # Sensitivity to HDD/CDD
# p <- ggplot(dataset, aes(x = cdd, y = load, col = year))
# p <- p + geom_point()
# p
# p <- ggplot(dataset, aes(x = hdd, y = load, col = year))
# p <- p + geom_point()
# p

################################################################
# 3) Regression
################################################################
# Make sure months are considered as indicator variables
dataset$month <- as.character(dataset$month)

# Train regression on years prior to 2020
a <- lm(load ~ month + cdd + hdd, data = dataset %>% filter(year != 2020))

# Forecast for 2020
dataset$forecast <- predict(a, dataset, interval = "prediction")[,"fit"]
dataset$CI_low <- predict(a, dataset, interval = "prediction")[,"lwr"]
dataset$CI_high <- predict(a, dataset, interval = "prediction")[,"upr"]

# Plot of the result
plot(dataset$load, type = "l", xlab = "Months since Jan 2017", ylab = "Load (GWh)", lwd = 2)
lines(dataset$forecast, col = "red", lwd = 2)
lines(dataset$CI_low, lty=2, col = "red")
lines(dataset$CI_high, lty=2, col = "red")
abline(v = 36.5, col = 'blue') # beginning of 2020

################################################################
# 4) Estimated % change in load 
################################################################
dataset$change <- 100*(dataset$load-dataset$forecast)/dataset$forecast

# Plot of the result
plot(dataset$change,type = "l", xlab = "Months since Jan 2017", ylab = "Estimated % change", lwd = 2)
abline(h = 0, col = 'blue')
abline(v = 36.5, col = 'red')

################################################################
# 5) Export result
################################################################
dataset <- dataset %>% filter(
  year == 2020
) %>% select(
  year,month,change
)

# Path to result folder
path_result <- "Results/"

# Export result
write.csv(dataset, paste0(path_result,"Argentina.csv"), row.names = F)
