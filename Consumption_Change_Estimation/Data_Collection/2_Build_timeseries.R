#####################################################
# This script builds country-specific population-weighted HDD/CDD daily timeseries
# from the previously downloaded weather-station-level measurements
#####################################################
rm(list = ls())
library(dplyr)
library(gtools)

# 1) Load list of stations scrapped
stations <- read.csv("metafile.csv", stringsAsFactors = F)

# Create directory to store results
if (!(file.exists("Output"))){
  dir.create("Output") 
}

# 2) Timezones (weather measurements are in UTC time)
# Retrieved from: https://www.zeitverschiebung.net/en/city/3448439
list_countries <- c(
  "Austria",
  "Belgium",
  "Bosnia",
  "Bulgaria",
  "Croatia",
  "Cyprus",
  "Czech_Republic",
  "Denmark",
  "Estonia",
  "Finland",
  "France",
  "Germany",
  "Greece",
  "Hungary",
  "Ireland",
  "Italy",
  "Latvia",
  "Lithuania",
  "Luxembourg",
  "Netherlands",
  "Norway",
  "Poland",
  "Portugal",
  "Romania",
  "Serbia",
  "Slovakia",
  "Slovenia",
  "Spain",
  "Sweden",
  "Switzerland",
  "Ukraine",
  "United-Kingdom",
  "NZ",
  "ontario",
  "SA",
  "QLD",
  "NSW",
  "TAS",
  "VIC",
  "WA",
  "NT",
  "singapore",
  "india",
  "japan",
  "korea",
  "brazil",
  "chile",
  "russia",
  "south_africa",
  "british_columbia",
  "thailand",
  "argentina",
  "mexico",
  "china",
  "alberta",
  "kenya"
)

time_zone_country <- c(
  "Europe/Vienna",
  "Europe/Brussels",
  "Europe/Sarajevo",
  "Europe/Sofia",
  "Europe/Zagreb",
  "Europe/Nicosia",
  "Europe/Prague",
  "Europe/Copenhagen",
  "Europe/Tallinn",
  "Europe/Helsinki",
  "Europe/Paris",
  "Europe/Berlin",
  "Europe/Athens",
  "Europe/Budapest",
  "Europe/Dublin",
  "Europe/Rome",
  "Europe/Riga",
  "Europe/Vilnius",
  "Europe/Luxembourg",
  "Europe/Amsterdam",
  "Europe/Oslo",
  "Europe/Warsaw",
  "Europe/Lisbon",
  "Europe/Bucharest",
  "Europe/Belgrade",
  "Europe/Bratislava",
  "Europe/Ljubljana",
  "Europe/Madrid",
  "Europe/Stockholm",
  "Europe/Zurich",
  "Europe/Kiev",
  "Europe/London",
  "Pacific/Auckland",
  "America/Toronto",
  "Australia/Adelaide",
  "Australia/Brisbane",
  "Australia/Sydney",
  "Australia/Hobart",
  "Australia/Melbourne",
  "Australia/Perth",
  "Australia/Darwin",
  "Asia/Singapore",
  "Asia/Kolkata",
  "Asia/Tokyo",
  "Asia/Seoul",
  "America/Sao_Paulo",
  "America/Santiago",
  "Europe/Moscow",
  "Africa/Johannesburg",
  "America/Vancouver",
  "Asia/Bangkok",
  "America/Argentina/Buenos_Aires",
  "America/Mexico_City",
  "Asia/Shanghai",
  "America/Edmonton",
  "Africa/Nairobi"
)
names(time_zone_country) <- list_countries

# 3) Loop on countries
for (c in unique(stations$Country)){
  # Select stations in the country of intereest
  sample_stations <- stations %>% filter(Country == c)
  # Output dataframe
  result <- data.frame(
    day = as.Date(character(0)),
    # population weighted HDD/CDD 
    hdd_us = as.numeric(),
    cdd_us = as.numeric(),
    # New HDD/CDD observation
    population = as.numeric()
  )
  
  # Loop on weather stations, whose hdd/cdd are weighted by population
  for(s in 1:nrow(sample_stations)){
    station <- sample_stations$StationID[s]
    # Load temperature
    temperature <- read.csv(paste0("Raw_data/",station,".csv"), quote = "", skip = 5, stringsAsFactors = F)
    # Convert timetag in POSIX
    temperature$valid <- as.POSIXct(temperature$valid, tz = "UTC", format = "%Y-%m-%d %H:%M")
    # Extract day in local time
    temperature$day <- as.Date(temperature$valid, format("%Y-%m-%d"), tz = time_zone_country[c])
    # Correct variable type
    temperature$tmpf <- as.numeric(temperature$tmpf)

    # HDD and CDD:
    DD_daily <- temperature %>% group_by(day) %>% summarise(
      new_hdd_us = sum(pmax(65-tmpf,0))/n(),
      new_cdd_us = sum(pmax(tmpf-65,0))/n()
    )
    
    # Add new timeseries to dataset
    result <- full_join(result,DD_daily, by = "day") %>% arrange(day)
    rm(DD_daily)
    
    # Replace NAs with zeros
    result$hdd_us[is.na(result$hdd_us)] <- 0
    result$cdd_us[is.na(result$cdd_us)] <- 0
    result$population[is.na(result$population)] <- 0
    
    # Update values
    new_population <- sample_stations$Population[s]
    result$hdd_us <- result$hdd_us+new_population*na.replace(result$new_hdd_us,0)
    result$cdd_us <- result$cdd_us+new_population*na.replace(result$new_cdd_us,0)
    result$population <- result$population + as.numeric(!is.na(result$hdd_us))*new_population
    
    # Get rid of auxiliary variables
    result$new_hdd_us <- NULL
    result$new_cdd_us <- NULL
  }
  
  # Average by population
  result$hdd_us <- result$hdd_us/result$population
  result$cdd_us <- result$cdd_us/result$population
  result$population <- NULL
  
  # Only keep 1 Jan 2015 to 15 Nov 2020 
  result <- result %>% filter(
    difftime(as.Date("2015-01-01"),result$day) <= 0 & 
    difftime(as.Date("2020-11-15"),result$day) >= 0
  ) %>% as.data.frame()
  
  # End of loop
  # Save timeseries for the country of interest
  write.csv(result, file = paste0("Output/",c,".csv"), row.names = F)
  #print(warnings())
  print(paste(c,"ok"))
}
                 
