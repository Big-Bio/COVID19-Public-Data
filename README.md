# COVID-19 Public Data Curation

This repository stores public time series data for any COVID-19 related features, such as case counts, death counts, hospital resource usage, etc. We are sepcifically looking at data more finescale than at the county level. The datasets are at the city, zipcode or neighborhood level, and will be used in models we have created for surge predictions in hospitals. This is an effort of the [STOP COVID-19 TOGETHER](https://stopcovid19together.org) team.

## Where should you put the cleaned data?

Make sure you're working on a fork of this repository. When you're done, submit a pull request and we'll make it live!

Each data file will have a specific feature that it reports (such as number of cases, deaths, hospital beds, etc). In the `processed_data` directory, there will be a subdirectory for each of these features. 
If you do not see a feature that you are working on, feel free to create the subdirectory.

Within the subdirectory, there will be location based folders. These will separate data into Global (if it reports across the world), or within the country of origin. Again, if a country is not here, feel free to add
the directory.

The file you are adding will be named as follows:

`{sample-name}_{feature-name}.csv`

where `{sample-name}` will describe the scope of your data (such as Los Angeles County) and `{feature-name}` will be the name of the feature. For example, we have 
number of cases reported for cities in southern California stored as

`processed_data/cases/US/southern-california_cases.csv`

## How should the data be formatted?

We are generating comma-delimited files with quotations around each field. The first column will be row names corresponding to sub-locations of the place you are processing. The remaining column names will
be the date in `M/DD/YY` format. Each entry has a numeric value for the feature at each date. All days should be included in the file and if there is missing data, fill in the entry with `NA`. 

Please see the example CSV above.

## How should I document this data?

For each data file you generate, make a file with the same name but with a `.txt` extension that briefly describes the data, where it came from (sources are very important), and the name of the script used to generate it.
For example, the `processed_data/cases/US/southern-california_cases.csv` file has an accompanying `processed_data/cases/US/southern-california_cases.txt` file

Scripts for generating these files should ideally be shared so we can keep this repo up to date. These can be stored in the `scripts` parent directory. Since scripts may generate multiple processed data files, the best way to reference these scripts is to include their name in the `{sample-name}_{feature-name}.txt` file that accompanies the processed data.

If you have geographic data (latitude or longitude) for the samples in your file, please add it to the `geo_data` directory as `{sample_name}_coords.csv`. These should have the place name as rows and a `lat` and `lon` column.  
