'''
Created by ROSEMARY HE on Apr.10
generates four .csv files documenting COVID-19 cases and death in each province and city in CHINA, the data is updated daily and script should run daily
to add new data
data source from https://github.com/BlankerL/DXY-COVID-19-Crawler by BlankerL, who pulls from Ding Xiang Yuan(https://ncov.dxy.cn/ncovh5/view/pneumonia)
'''

import pandas as pd
import numpy as np

url = 'https://raw.githubusercontent.com/BlankerL/DXY-COVID-19-Data/master/csv/DXYArea.csv'
df = pd.read_csv(url, index_col=False, usecols=['countryEnglishName','provinceEnglishName','province_confirmedCount','province_deadCount','updateTime','cityEnglishName','city_confirmedCount','city_deadCount'])

'''
##use if url doesn't work, download file from github, then open locally
url = 'DXYArea.csv'
df = pd.read_csv(open(url,'r'), index_col=False, usecols=['countryEnglishName','provinceEnglishName','province_confirmedCount','province_deadCount','updateTime','cityEnglishName','city_confirmedCount','city_deadCount'])
'''

##filter out only CHINA cases
df = df[df.countryEnglishName == 'China']
##get year-month-date in format MM/DD/YY
df['date'] = [str(x[5:7]+'/'+x[8:10]+'/'+x[2:4]) for x in df['updateTime']]
#in format YYYY-MM-DD
#df['date'] = [x[0:10] for x in df['updateTime']]

##China province confirmed count
df_province_c = df.loc[:,['provinceEnglishName','province_confirmedCount','date']]
df_province_c = df_province_c.drop_duplicates(subset=['provinceEnglishName','date'], keep='last')
df_province_c = df_province_c.set_index(['provinceEnglishName','date'])
##get header
dates = np.unique([x[1] for x in df_province_c.index.values])
df_province_c = df_province_c.unstack()

##China province death count
df_province_d = df.loc[:,['provinceEnglishName','province_deadCount','date']]
df_province_d = df_province_d.drop_duplicates(subset=['provinceEnglishName','date'], keep='last')
df_province_d = df_province_d.set_index(['provinceEnglishName','date'])
df_province_d = df_province_d.unstack()

##China city confirmed count
df_city_c = df.loc[:,['cityEnglishName','city_confirmedCount','date']]
df_city_c = df_city_c.drop_duplicates(subset=['cityEnglishName','date'], keep='last')
df_city_c = df_city_c.dropna(axis=0, subset=['cityEnglishName'])
df_city_c = df_city_c.set_index(['cityEnglishName','date'])
##get header
dates_city = np.unique([x[1] for x in df_city_c.index.values])
df_city_c = df_city_c.unstack()

##China city death count
df_city_d = df.loc[:,['cityEnglishName','city_deadCount','date']]
df_city_d = df_city_d.drop_duplicates(subset=['cityEnglishName','date'], keep='last')
df_city_d = df_city_d.dropna(axis=0, subset=['cityEnglishName'])
df_city_d = df_city_d.set_index(['cityEnglishName','date'])
df_city_d = df_city_d.unstack()

##export to .csv files
df_province_c.to_csv('China_cases_by_province.csv', index_label=None, header=dates, na_rep='NA', float_format='%.0f')
df_province_d.to_csv('China_death_by_province.csv', index_label=None, header=dates, na_rep='NA', float_format='%.0f')
df_city_c.to_csv('China_cases_by_city.csv', index_label=None, header=dates_city, na_rep='NA', float_format='%.0f')
df_city_d.to_csv('China_death_by_city.csv', index_label=None, header=dates_city, na_rep='NA', float_format='%.0f')
