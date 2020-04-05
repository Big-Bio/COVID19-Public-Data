# covidweb scraper

These scripts will grab the most up-to-date COVID-19 case information from [LA County Public Health](http://publichealth.lacounty.gov/media/Coronavirus/locations.htm)
and from [Johns Hopkins CSSE](http://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports).

Data is dumped into JS files in the `archive` directory with suffix `MM-DD-YYYY.js` and into the `latest` directory with a constant suffix.

# Requirements

R scripts require `stringr`, `plyr`, `RCurl` packages.

JS script requires `cheerio` and `request` packages

# Usage

From the scripts directory (i.e. make sure `scripts` is your working directory)

`Rscript csse_covid_19_daily_reports.R`

`Rscript la_county_daily_reports.R`
