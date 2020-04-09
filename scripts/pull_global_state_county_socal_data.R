library(stringr)

#' Pulls time series data from CSSE for global data
#' @return data.frame of time series data
read_csse_global_time_series_data <- function(csv.url){
  tol <- 1e-2
  raw.time.series <- read.csv(csv.url, check.names = FALSE, stringsAsFactors = FALSE)
  raw.time.series <- raw.time.series[abs(raw.time.series$Lat) > tol & abs(raw.time.series$Long) > tol,]
  place <- stringr::str_replace(paste(raw.time.series$`Province/State`, raw.time.series$`Country/Region`, sep=', '), "^, ", "")
  global.time.series <- raw.time.series[,5:ncol(raw.time.series)] # assuming first 4 columns are province, country, lat, and lon
  row.names(global.time.series) <- place
  return(global.time.series)
}

#' Pulls time series data from CSSE for US data
#' @return A list of state.level and county.level data.frames
read_csse_us_time_series_data <- function(csv.url){
  raw.time.series <- read.csv(csv.url, stringsAsFactors = FALSE, check.names = FALSE)
  tol <- 1e-2
  states.to.remove <- c("Grand Princess", "Diamond Princess")
  raw.time.series <- raw.time.series[!(raw.time.series$Province_State %in% states.to.remove),]
  # State level
  state.level.time.series <- aggregate(raw.time.series[,12:ncol(raw.time.series)],by=raw.time.series[,"Province_State",drop=F], FUN = sum )
  rownames(state.level.time.series) <- state.level.time.series[,"Province_State"]
  state.level.time.series <- state.level.time.series[,2:ncol(state.level.time.series)]
  # County level, remove places with no lat lon
  raw.time.series <- raw.time.series[abs(raw.time.series$Lat) > tol & abs(raw.time.series$Long_) > tol,]
  county.level.time.series <- raw.time.series[,12:ncol(raw.time.series)]
  rownames(county.level.time.series) <- raw.time.series[,"Combined_Key"]
  return(list(state.level=state.level.time.series, county.level=county.level.time.series))
}

#' Pulls time series data from LA Times for SoCal data
read_latimes_agency_data <- function(csv.url){
  socal.level.data <- read.csv(csv.url, check.names=FALSE, stringsAsFactors = FALSE)
  # remove complete duplicate rows
  socal.level.data <- socal.level.data[!duplicated(socal.level.data[,c("date", "county", "fips", "place")]),]
  losangeles.data <- socal.level.data[socal.level.data$county == "Los Angeles",]
  unincorporated.pattern <- "^Unincorporated - "
  unincorporated.cities <- grep(unincorporated.pattern, losangeles.data$place, value = TRUE)
  losangeles.pattern <- "^Los Angeles - "
  losangeles.cities <- grep(losangeles.pattern, losangeles.data$place, value = TRUE)
  cityof.pattern <- "^City of "
  cityof.cities <- grep(cityof.pattern, losangeles.data$place, value=TRUE)
  place.to.remove <- c("Under Investigation", "- Under Investigation", "Unknown", "Smaller Los Angeles neighborhoods",
                       "Unincorporated Florence-Firestone", "Unincorporated - Florence-Firestone", "Los Angeles - Florence-Firestone")
  place.to.remove <- c(place.to.remove, losangeles.cities, unincorporated.cities, cityof.cities)
  socal.level.data <- socal.level.data[!(socal.level.data$place %in% place.to.remove),]
  #unincorporated.la.cities <- stringr::str_replace(grep(unincorporated.pattern, losangeles.data$place, value = TRUE), unincorporated.pattern, "")
  #unincorporated.lat <- losangeles.data[grep(unincorporated.pattern, losangeles.data$place),]$y
  #unincorporated.lon <- losangeles.data[grep(unincorporated.pattern, losangeles.data$place),]$x
  
  #losangeles.la.cities <- stringr::str_replace(grep(losangeles.pattern, losangeles.data$place, value=TRUE), losangeles.pattern, "")
  #losangeles.lat <- losangeles.data[grep(losangeles.pattern, losangeles.data$place),]$y
  #losangeles.lon <- losangeles.data[grep(losangeles.pattern, losangeles.data$place),]$x
  places <- paste(socal.level.data$place, socal.level.data$county, sep=', ')
  times <- as.numeric(as.POSIXct(socal.level.data$date))
  dates <- format(as.POSIXct(times, origin="1970-01-01"), "%m/%d/%y")
  unique.dates <- unique(format(as.POSIXct(sort(times), origin="1970-01-01"), "%m/%d/%y"))
  unique.places <- unique(places)
  socal.time.series.data <- data.frame(row.names=unique.places)
  for (datestr in unique.dates){
    row.indices <- dates == datestr
    sub.df <- socal.level.data[row.indices,]
    rownames(sub.df) <- places[row.indices]
    new.col <- sub.df[unique.places,"confirmed_cases"]
    socal.time.series.data[[datestr]] <- new.col
  }
  return(socal.time.series.data)
}

main <- function(){
  out.dir <- "../processed_data/"
  
  global.cases.time.series.csv <- "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
  global.death.time.series.csv <- "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
  us.cases.time.series.csv <- "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
  us.death.time.series.csv <- "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"
  socal.time.series.csv <- "https://raw.githubusercontent.com/datadesk/california-coronavirus-data/master/latimes-place-totals.csv" # no deaths, just cases
  
  us.cases <- read_csse_us_time_series_data(us.cases.time.series.csv)
  us.deaths <- read_csse_us_time_series_data(us.death.time.series.csv)
  
  socal.cases <- read_latimes_agency_data(socal.time.series.csv)
  us.state.cases <- us.cases$state.level
  us.county.cases <- us.cases$county.level
  global.cases <- read_csse_global_time_series_data(global.cases.time.series.csv)
  
  us.state.deaths <- us.deaths$state.level
  us.county.deaths <- us.deaths$county.level
  global.deaths <- read_csse_global_time_series_data(global.death.time.series.csv)
  
  write.csv(socal.cases, sprintf("%s/cases/US/southern-california_cases.csv", out.dir))
  write.csv(us.state.cases, sprintf("%s/cases/US/us-state_cases.csv", out.dir))
  write.csv(us.county.cases, sprintf("%s/cases/US/us-county_cases.csv", out.dir))
  write.csv(global.cases, sprintf("%s/cases/global/global_cases.csv", out.dir))
  write.csv(us.state.deaths, sprintf("%s/deaths/US/us-state_deaths.csv", out.dir))
  write.csv(us.county.deaths, sprintf("%s/deaths/US/us-county_deaths.csv", out.dir))
  write.csv(global.deaths, sprintf("%s/deaths/global/global_deaths.csv", out.dir))
  
}

if (sys.nframe() == 0L) {
  main()
}
