#Panel regression analysis results
#script reproducing Table 1 in the main text and Table S4 in the supplmental materials

#required libraries
library(plm)
library(lfe)
library(lmtest)
library(car)
library(dplyr)

#Import data
setwd('..')
csvfile_initial<-read.csv("Data/Intermediate/panel_data.csv")
csvfile_recovery<-read.csv("Data/Intermediate/panel_data_recovery.csv")

str(csvfile_initial)
str(csvfile_recovery)

#Data cleaning
dfi<-csvfile_initial[c(-1)]
dfr<-csvfile_recovery[c(-1)]

#Rolling deaths for dfi dataframe
dfi$Date <- as.Date(dfi$Date)
dfi$window <- 0
dfi$Deaths_rolling <- 0

for (i in 1:nrow(csvfile_initial)){
  country <- dfi$Country[i]
  
  dfi$window[i] <- sum(dfi$Country == country & difftime(dfi$Date,dfi$Date[i], units = "days") <= 0 & difftime(dfi$Date,dfi$Date[i], units = "days") > -14)
  
  dfi$Deaths_rolling[i] <- mean(dfi$Daily.Deaths.per.100k[dfi$Country == country & difftime(dfi$Date,dfi$Date[i], units = "days") <= 0 & difftime(dfi$Date,dfi$Date[i], units = "days") > -14])
}
dfi <- dfi %>% filter(window == 14)



#Rolling deaths for dfr dataframe
dfr$Date <- as.Date(dfr$Date)
dfr$window <- 0
dfr$Deaths_rolling <- 0

for (i in 1:nrow(csvfile_recovery)){
  country <- dfr$Country[i]
  
  dfr$window[i] <- sum(dfr$Country == country & difftime(dfr$Date,dfr$Date[i], units = "days") <= 0 & difftime(dfr$Date,dfr$Date[i], units = "days") > -14)
  
  dfr$Deaths_rolling[i] <- mean(dfr$Daily.Deaths.per.100k[dfr$Country == country & difftime(dfr$Date,dfr$Date[i], units = "days") <= 0 & difftime(dfr$Date,dfr$Date[i], units = "days") > -14])
}
dfr <- dfr %>% filter(window == 14)

#Create panel data frame for plm function
pdi <- pdata.frame(dfi, index=c("Country","Date"), drop.index=TRUE, row.names=TRUE)
str(pdi)
pdr <- pdata.frame(dfr, index=c("Country","Date"), drop.index=TRUE, row.names=TRUE)
str(pdr)


#Table 1, main text, random effects
model1.re.initial<- plm(Pct.Change.in.Electricity.Demand~Oxford+Deaths_rolling+Mobility..Retail.and.Recreation+Holiday.Effect
                        +Q2.2020.change.in.GDP.since.Q2.2019+Sector..Commercial.and.public.services, data = pdi, model = "random")
summary(model1.re.initial)

model2.re.recovery<- plm(Pct.Change.in.Electricity.Demand~Oxford+Deaths_rolling+Mobility..Retail.and.Recreation+Holiday.Effect
                         +Q2.2020.change.in.GDP.since.Q2.2019+Sector..Commercial.and.public.services, data = pdr, model = "random")
summary(model2.re.recovery)


#Table S4, supplement, fixed effects
model1.fe.initial<- plm(Pct.Change.in.Electricity.Demand~Oxford+Deaths_rolling+Mobility..Retail.and.Recreation+Holiday.Effect
                        +Q2.2020.change.in.GDP.since.Q2.2019+Sector..Commercial.and.public.services, data = pdi, model = "within")
summary(model1.fe.initial)

model2.fe.recovery<- plm(Pct.Change.in.Electricity.Demand~Oxford+Deaths_rolling+Mobility..Retail.and.Recreation+Holiday.Effect
                         +Q2.2020.change.in.GDP.since.Q2.2019+Sector..Commercial.and.public.services, data = pdr, model = "within")
summary(model2.re.recovery)


#Table S4, supplment, fixed effects with projected and full R-squared
model1.fe.initial.full<- felm(Pct.Change.in.Electricity.Demand~Oxford+Deaths_rolling+Mobility..Retail.and.Recreation|Country, data = dfi, contrasts=c('Country','Date'))
summary(model1.fe.initial.full)

model2.fe.recovery.full<- felm(Pct.Change.in.Electricity.Demand~Oxford+Deaths_rolling+Mobility..Retail.and.Recreation|Country, data = dfr, contrasts=c('Country','Date'))
summary(model2.fe.recovery.full)


#Table S5, supplement, random effects without pre-pandemic holiday effect
model1.re.initial<- plm(Pct.Change.in.Electricity.Demand~Oxford+Deaths_rolling+Mobility..Retail.and.Recreation
                        +Q2.2020.change.in.GDP.since.Q2.2019+Sector..Commercial.and.public.services, data = pdi, model = "random")
summary(model1.re.initial)

model2.re.recovery<- plm(Pct.Change.in.Electricity.Demand~Oxford+Deaths_rolling+Mobility..Retail.and.Recreation
                         +Q2.2020.change.in.GDP.since.Q2.2019+Sector..Commercial.and.public.services, data = pdr, model = "random")
summary(model2.re.recovery)
