# COVID-19 Public Data Curation

This repository stores public time series data for any COVID-19 related features, such as case counts, death counts, hospital resource usage, etc. We are sepcifically looking at data more finescale than at the county level. The datasets are at the city, zipode or neighborhood level, and will be used for surge predictions in hospitals.

These data should have consistent naming conventions for samples (such as location names) and structure. Specifically, data should be stored in the following manner:

The feature name will have a subdirectory in the `processed_data` parent directory, such as `cases` or `deaths`. Within this subdirectory, the file should be named `{sample_name}_{feature_name}.csv`. This file should be accompanied by a file named `{sample_name}_{feature_name}.txt` that describes the data in more detail, including its source. `sample_name` can be something like "los-angeles-county" or "ucla-reagan-hospital".  The data file should be comma separated with quotations. Row names should correspond to individual samples (such as Westwood in "los-angeles-county") and column names should be the date in `YYYY-MM-DD` format. Each entry corresponds to the value of the given feature on the given date. Missing values will be set to the "NA" string. 

Scripts for generating these files should ideally be shared as well. These can be stored in the `scripts` parent directory. Since scripts may generate multiple processed data files, the best way to reference these scripts is to include their name in the `{sample_name}_{feature_name}.txt` file that accompanies the processed data.

If you have geographic data (latitude or longitude) for the samples in your file, please add it to the `geo_data` directory as `{sample_name}_coords.csv`. These should have the place name as rows and a `lat` and `lon` column.  
