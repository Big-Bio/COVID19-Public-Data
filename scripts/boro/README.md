## Description
The program `boroProcess.py` fetches the latest data on [NYC Health](https://github.com/nychealth/coronavirus-data/blob/master/boro.csv) and saves the latest data as the COVID-19 data for the execution day. The program will automatically format the data to satisfy the requirement. Currently, the correctness of the program depends on the following assumptions:
- The format of [NYC Health boro dataset](https://github.com/nychealth/coronavirus-data/blob/master/boro.csv) will be consistent in the future. 
- [NYC Health](https://github.com/nychealth/) has updated its dataset for the day when the program is executed.
- The data provided by [NYC Health](https://github.com/nychealth/) is correct.
- Other assumptions.


## Set up the environment
```
$ pip install -r scripts/boro/requirements.txt 
$ mkdir log
```
The program is running on Python 2.7.15.

## Run the program
```
$ python scripts/boro/boroProcess.pyboroProcess.py ${input_directory} ${output_fliename}
```

For example: 
```
$ python scripts/boro/boroProcess.py raw_data/boro_data/ processed_data/cases/nyc_cases.csv
```
The file tree will be like:
```
.
├── README.md
├── raw_data
│   └── boro_data
│       ├── boro04012020
│       └── ...
├── geo_data
│   └── ...
├── log
│   └── boroProcess.log -> The execution log
├── processed_data
│   ├── cases
│   │   ├── nyc_cases.csv
│   │   └── ...
│   └── ...
└── scripts
    ├── boro
    │   ├── README.md
    │   ├── boroProcess.py
    │   └── requirements.txt
    └── ...
```
