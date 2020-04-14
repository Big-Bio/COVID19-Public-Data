## Description
We thank Definitive Healthcare for making these data public with no license at the time of retrieval from: https://coronavirus-disasterresponse.hub.arcgis.com/datasets/definitivehc::definitive-healthcare-usa-hospital-beds

## Set up the environment
```
$ pip install -r scripts/definitive_healthcare/requirements.txt 
$ mkdir log
```
The program is running on Python 2.7.15.

## Run the program
```
$ python scripts/definitive_healthcare/dhProcess.py ${input_directory} ${output_directory}
```

For example: 
```
$ python scripts/definitive_healthcare/dhProcess.py raw_data/definitive_healthcare/ processed_data/
```
