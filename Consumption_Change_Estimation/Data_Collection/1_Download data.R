#####################################################
# This script downloads measurements between 31 Dec 2014 and 15 November 2020
# from the weather stations listed in the "metafile.csv" file
#####################################################
rm(list = ls())
library(stringr)
library(lubridate)

# 1) Load the list of stations to scrap
stations <- read.csv("weatherdata_metafile.csv", stringsAsFactors = F)

# 2) Define beginning and end date for timeseries
date1 <- ISOdate(2014,12,31) #start date in year, month, day format
date2 <- ISOdate(2020,11,15) #end date in year, month, day format

# 3) Header of the request
service <- "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
service <- str_c(service, "data=all&tz=Etc/UTC&format=comma&latlon=no&", sep="")
service <- str_c(service, "year1=", year(date1), "&month1=", month(date1), "&day1=", mday(date1), "&", sep="")
service <- str_c(service, "year2=", year(date2), "&month2=", month(date2), "&day2=", mday(date2), "&", sep="")

# 4) Create directory to store downloaded data
# (full download weights about 7-8 GB)
if (!(file.exists("Raw_data"))){
  dir.create("Raw_data") 
}

# 5) Loop on stations
i <- 1
N <- nrow(stations)
for (s in stations$StationID){
  s <- gsub(pattern = " ", replacement = "", s)
  uri <- str_c(service, "station=", s)
  download.file(uri, paste0("Raw_data/",s,".csv"), "auto")
  # message notifying the download took place
  print(paste0("Station:",i,"/",N," ok"))
  i <- i + 1
  # wait for 5 sec
  Sys.sleep(5)
}
                 
