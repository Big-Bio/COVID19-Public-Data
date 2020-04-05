library(stringr)
library(plyr)

#' Runs JS script with node to pull data from
#' http://publichealth.lacounty.gov/media/Coronavirus/locations.htm
scrape_la_covid_data <- function(js.script.path){
  shell.cmd <- sprintf("node %s | sed -n '/^CITY.COMMUNITY/,/^-  Under/p;/^-  Under/q' | sed '$d'", js.script.path)
  first <- TRUE
  la.covid <- NULL
  for (row in system(shell.cmd, intern=TRUE)){
    if (first){
      first <- FALSE
      next
    }
    row <- as.vector(strsplit(row, ',')[[1]])
    la.covid <- rbind(la.covid, row)
  }
  la.covid <- data.frame(la.covid, stringsAsFactors = FALSE)
  colnames(la.covid) <- c("City", "Cases", "Rate")
  la.covid$City <- stringr::str_replace(la.covid$City, stringr::fixed("***"), "")
  la.covid$City <- stringr::str_replace(la.covid$City, "^City of ", "")
  la.covid$City <- stringr::str_replace(la.covid$City, "^Los Angeles - ", "")
  la.covid$City <- stringr::str_replace(la.covid$City, "^Unincorporated - ", "")
  la.covid$City <- paste(la.covid$City, ", Los Angeles", sep="")
  la.covid$Cases[la.covid$Cases == "--"] <- NA
  la.covid$Rate[la.covid$Rate == "--"] <- NA
  la.covid <- transform(la.covid, Cases = as.numeric(as.vector(Cases)), 
                        Rate = as.numeric(as.vector(Rate)))
  return(la.covid)
}

convert_report <- function(report, file.names){
  lines <- c("var laCitiesData = [")
  for (i in 1:nrow(report)){ # coord = lat lon # changed city to place, cases to confirmed, added deaths ,recovered, and active
    case.num <- report[i, "Cases"]
    if (is.na(case.num)){
      case.num <- -1
    }
    row.str <- 	sprintf("\t{ place: \"%s\", confirmed: %i, deaths: %i, recovered: %i, active: %i, coord:[%f,%f]}",
                        report[i,"City"], case.num, -1,
                        -1, -1, report[i, "lat"], report[i, "lon"])
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

#' Pulls current LA county city-level COVID cases and
#' writes to JS file
#' 
#' @param city.locs.csv CSV with LA city locations (la_county_city_geo.csv)
#' @param js.script.path JS file (la_county_daily_reports.js)
#' @param latest.dir Directory to write JS files to with constant name
#' @param archive.dir Directory to write same JS files to with date suffix
#' @return NULL
main <- function(city.locs.csv, js.script.path, latest.dir, archive.dir){
  la.covid <- scrape_la_covid_data(js.script.path)
  city.locs <- read.csv(city.locs.csv, row.names=1)
  la.covid <- plyr::ddply(la.covid, .(City), summarize, Cases = sum(Cases))
  la.covid$lat <- city.locs[la.covid$City,"lat"]
  la.covid$lon <- city.locs[la.covid$City,"lon"]
  #print(la.covid)
  file.names <- c(sprintf("%s/la_county_cities_%s.js",
                          archive.dir, format(Sys.Date(),"%m-%d-%Y")),
                  sprintf("%s/la_county_cities_latest.js", latest.dir))
  convert_report(la.covid, file.names)
}

city.locs.csv <- "../geo_data/la_county_city_geo.csv"
js.script.path <- "./la_county_daily_reports.js"
latest.dir <- "../latest"
archive.dir <- "../archive"
main(city.locs.csv, js.script.path, latest.dir, archive.dir)
