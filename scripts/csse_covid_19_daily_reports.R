library(plyr)
library(RCurl)

filter_csse_daily_report <- function(report, Country=NULL, State=NULL, City=NULL,
                                country.csv=NULL, state.csv=NULL){
  if (!is.null(state.csv)){
    # just assume we care about US only
    state.geo <- read.csv(state.csv, stringsAsFactors = FALSE)
    rownames(state.geo) <- state.geo$name
    report <- report[report$Country_Region == "US",]
    report <- plyr::ddply(report, .(Province_State), summarize,
                          Confirmed = sum(Confirmed),
                          Deaths = sum(Deaths),
                          Recovered=sum(Recovered),
                          Active=sum(Active))
    report[["Lat"]] <- state.geo[report$Province_State,"latitude"]
    report[["Long_"]] <- state.geo[report$Province_State, "longitude"]
    report <- report[complete.cases(report),]
    colnames(report)[colnames(report) == "Province_State"] <- "Combined_Key"
  }
  if (!is.null(country.csv)){
    # just assume we care about US only
    country.geo <- read.csv(country.csv, stringsAsFactors = FALSE)
    rownames(country.geo) <- country.geo$name
    report <- plyr::ddply(report, .(Country_Region), summarize,
                          Confirmed = sum(Confirmed),
                          Deaths = sum(Deaths),
                          Recovered=sum(Recovered),
                          Active=sum(Active))
    report[["Lat"]] <- country.geo[report$Country_Region,"latitude"]
    report[["Long_"]] <- country.geo[report$Country_Region, "longitude"]
    #report <- report[complete.cases(report),]
    colnames(report)[colnames(report) == "Country_Region"] <- "Combined_Key"
  }
  if (!is.null(Country)){
    report <- report[report$Country_Region == Country,]
  }
  if (!is.null(State)){
    report <- report[report$Province_State == State,]
  }
  if (!is.null(City)){
    report <- report[report$Admin2 == City,]
  }
  # This removes boats and some city data that is merged in at the state level
  report <- report[!is.na(report$Lat) & !is.na(report$Long_),]
  return(report)
}

convert_report <- function(report, file.names, var.name){
  lines <- c(sprintf("var %s = [", var.name))
  for (i in 1:nrow(report)){
    row.str <- 	sprintf("\t{ place: \"%s\", confirmed: %i, deaths: %i, recovered: %i, active: %i, coord:[%f,%f]}",
                        report[i,"Combined_Key"], report[i,"Confirmed"], report[i,"Deaths"],
                        report[i,"Recovered"], report[i,"Active"], report[i, "Lat"], report[i, "Long_"])
    if (i != nrow(report)){
      row.str <- paste0(row.str, ",")
    }
    lines <- c(lines, row.str)
  }
  lines <- c(lines, "];")
  for (out.file in file.names){
    fileConn<-file(out.file)
    writeLines(lines, fileConn)
    close(fileConn)
  }
}

#' Generates JS files for CSSE COVID-19 daily report
#'
#' Currently drops all entries that do not show up in state or country csvs. All non-boat
#' locations are in these files as of 04-01-2020.
#' 
#' @param state.csv CSV with state geo data (states_geo.txt)
#' @param country.csv CSV with country geo data (contries_geo.txt)
#' @param latest.dir Directory to store latest scraped data with constant name
#' @param archive.dir Directory to store dated scraped data
#' @param max.tries How many dates to try to pull before failing. Will start with today, then yesterday,
#'                  and previous day until max.tries reached or first date to return results.
#' @return NULL
main <- function(state.csv, country.csv, latest.dir, archive.dir, max.tries=3){
  for (i in 0:(max.tries-1)){
    cdate <- format(Sys.Date()-i,"%m-%d-%Y")
    report.csv <- sprintf("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_daily_reports/%s.csv", cdate)
    if (!RCurl::url.exists(report.csv)){
      report.csv <- NULL
      message(sprintf("Data for %s not found in CSSEGISandData/COVID-19 repo", cdate))
    }
    else{
      break
    }
  }
  if (is.null(report.csv)){
    stop(sprintf("Could not find data for the past %i days", max.tries))
  }
  report <- read.csv(report.csv,stringsAsFactors = FALSE)
  us.county.report <- filter_csse_daily_report(report, Country = "US")
  us.state.report <- filter_csse_daily_report(report, state.csv = state.csv)
  country.report <- filter_csse_daily_report(report, country.csv = country.csv)
  us.state.files <- c(sprintf("%s/us_states_latest.js", latest.dir),
                      sprintf("%s/us_states_%s.js", archive.dir, cdate))
  us.county.files <- c(sprintf("%s/us_counties_latest.js", latest.dir),
                      sprintf("%s/us_counties_%s.js", archive.dir, cdate))
  country.files <- c(sprintf("%s/global_countries_latest.js", latest.dir),
                     sprintf("%s/global_countries_%s.js", archive.dir, cdate))
  convert_report(us.state.report, us.state.files, "usStatesData")
  convert_report(us.county.report, us.county.files, "usCountiesData")
  convert_report(country.report, country.files, "globalData")
}

state.csv <- "../geo_data/states_geo.txt"
country.csv <- "../geo_data/countries_geo.txt"
latest.dir <- "../latest"
archive.dir <- "../archive"
main(state.csv, country.csv, latest.dir, archive.dir, max.tries=3)



