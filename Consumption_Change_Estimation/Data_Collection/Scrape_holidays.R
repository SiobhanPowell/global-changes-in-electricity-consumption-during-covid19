rm(list = ls())
library(rvest)
library(stringr)
library(dplyr)

# List of countries for which special days need to be recovered
list_countries <- c(
  "austria",
  "belgium",
  "bosnia",
  "bulgaria",
  "croatia",
  "cyprus",
  "czech",
  "denmark",
  "estonia",
  "finland",
  "france",
  "germany",
  "greece",
  "hungary",
  "ireland",
  "italy",
  "latvia",
  "lithuania",
  "luxembourg",
  "netherlands",
  "norway",
  "poland",
  "portugal",
  "romania",
  "serbia",
  "slovakia",
  "slovenia",
  "spain",
  "sweden",
  "switzerland",
  "ukraine",
  "uk",
  "us",
  "new-zealand",
  "canada",
  "australia",
  "singapore",
  "india",
  "japan",
  "south-korea",
  "brazil",
  "chile",
  "russia",
  "south-africa",
  "thailand",
  "argentina",
  "mexico",
  "china",
  "kenya"
)

output <- data.frame(
  Date = as.Date(character(0)),
  Day = as.character(),
  Name = as.character(),
  Type = as.character(),
  Details = as.character(),
  Country = as.character(),
  stringsAsFactors = F
)

for (country in list_countries){
  #print(country)
  for (year in as.character(2015:2020)){
    #print(year)
    
    # Load webpage 
    webpage <- readLines(paste0("https://www.timeanddate.com/holidays/", country,"/",year), warn = F)
    
    # Extract the html line that contains the holiday table
    relevant_line <- webpage[grep(webpage, pattern = "<h2 id=holidays>")]
    relevant_line <- str_extract(relevant_line, "\\<table.+table\\>")
    rm(webpage)
    
    # Convert the html table into a dataframe
    table_as_df <- minimal_html(relevant_line) %>%
      html_node("table") %>%
      html_table(fill = T)
    
    # Add a "Details" column even when absent from the html table to remain
    # consistent the dimension of the dataframe
    if(ncol(table_as_df) == 4){
      table_as_df$Details <- ""
    }
    
    # Rename variables to keep them consistent
    names(table_as_df) <- c("Day",
                            "Week day",
                            "Name",
                            "Type",
                            "Details")
    
    # Remove rows introduced by footnotes and other miscellaneous formats
    table_as_df <- table_as_df %>% filter(
      !is.na(Type) & Type != "Type"
    )
    
    # Add year information (absent so far from variable "Day")
    table_as_df$Date <- paste(table_as_df$Day,year)
    table_as_df$Date <- as.Date(table_as_df$Date, format = "%b %d %Y")
    
    # Add country information
    table_as_df$Country <- country
    
    # Add to result dataframe
    output <- rbind(output,table_as_df)
    
    # Slow down scrapping
    Sys.sleep(3)
  }
}

# Export full result
output <- output %>% filter(
  !is.na(Date)
)
write.csv(output, file = "holidays_all.csv", row.names = F)

# Export main holidays only
output2 <- output %>% filter(Type %in% c("National holiday",
                                         "National Holiday",
                                         "Federal Holiday",
                                         "Bank holiday",
                                         "Public holiday"))

write.csv(output2, file = "holidays_main.csv", row.names = F)
