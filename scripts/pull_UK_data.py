'''
Created by ROSEMARY HE on Apr.14
generates a .csv file documenting COVID-19 cases by zip code in the UK, the data is updated daily and script should run daily to add new data
data source from https://github.com/tomwhite/covid-19-uk-data by tomwhite, who pulls from government website including but not limited to:
 https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public#number-of-cases
 www.gov.scot/coronavirus-covid-19
 for full list of documentation please visit his repository https://github.com/tomwhite/covid-19-uk-data
'''

import numpy as np
import pandas as pd


url = 'https://raw.githubusercontent.com/tomwhite/covid-19-uk-data/master/data/covid-19-cases-uk.csv'
df = pd.read_csv(url, index_col=False, usecols=['Date','AreaCode','TotalCases'])

'''
##use if url doesn't work, download file from github, then open locally
url = 'covid-19-cases-uk.csv'
df = pd.read_csv(open(url,'r'), index_col=False, usecols=['Date','AreaCode','TotalCases'])
'''

##keep last information if same area published more than once daily
df = df.drop_duplicates(subset=['AreaCode','Date'], keep='last')
##get rid of any cases without area code
df = df.dropna(subset=['AreaCode'])
##place date in MM/DD/YY format
df['date'] = [str(x[5:7] + '/' + str(x[8:10] + '/' + str(x[2:4]))) for x in df['Date']]
df = df.set_index(['AreaCode','date'], drop=True)
df = df.drop(['Date'], axis=1)

##get header
dates = np.unique([x[1] for x in df.index.values])
df = df.unstack()

##export to .csv file
df.to_csv('UK_cases_by_zip.csv', index_label=None, header=dates, na_rep='NA', float_format='%.0f')