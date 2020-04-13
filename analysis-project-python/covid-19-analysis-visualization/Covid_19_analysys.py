import math
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import calmap
import folium

from pandas.plotting import register_matplotlib_converters
from datetime import timedelta
from plotly.offline import plot, iplot, init_notebook_mode

# https://www.kaggle.com/imdevskp/covid-19-analysis-visualization-comparisons/comments

# init_notebook_mode(connected=True)

cnf, dth, rec, act = '#393e46', '#ff2e63', '#21bf73', '#fe9801'
register_matplotlib_converters()
pd.set_option('display.max_columns', None)

full_table = pd.read_csv('../data/covid_19_clean_complete.csv', parse_dates=['Date'])
# print(full_table.sample(6))


# 数据处理---------------------------
# 赛筛选数据
ship_rows = full_table['Province/State'].str.contains('Grand Princess') | \
            full_table['Province/State'].str.contains('Diamond Princess') | \
            full_table['Country/Region'].str.contains('Diamond Princess') | \
            full_table['Country/Region'].str.contains('MS Zaandam')

ship = full_table[ship_rows]
# print(ship)

full_table = full_table[~(ship_rows)]
# print(full_table.size)

ship_latest = ship[ship['Date'] == max(ship['Date'])]

# 数据清理--------------------------
# 各个国家存活的 ->  确诊-死亡-出院=存活的
full_table['Active'] = full_table['Confirmed'] - full_table['Deaths'] - full_table['Recovered']

full_table['Country/Region'] = full_table['Country/Region'].replace('Mainland China', 'China')

# 清理异常值,空值
full_table[['Province/State']] = full_table[['Province/State']].fillna('')
full_table[['Confirmed', 'Deaths', 'Recovered', 'Active']] = full_table[['Confirmed', 'Deaths', 'Recovered', 'Active']].fillna(0)

full_table['Recovered'] = full_table['Recovered'].astype(int)
# print(full_table.sample(6))

# 统计每个国家,每天数据
full_grouped = full_table.groupby(['Date', 'Country/Region'])[
    'Confirmed', 'Deaths', 'Recovered', 'Active'].sum().reset_index()
# print(full_grouped)


# 新增病例
temp = full_grouped.groupby(['Country/Region', 'Date'])['Confirmed', 'Deaths', 'Recovered']
temp = temp.sum().diff().reset_index()

mask = temp['Country/Region'] != temp['Country/Region'].shift(1)

temp.loc[mask, 'Confirmed'] = np.nan
temp.loc[mask, 'Deaths'] = np.nan
temp.loc[mask, 'Recovered'] = np.nan

print(temp)

# 重命名
temp.columns = ['Country/Region', 'Date', 'New cases', 'New deaths', 'New recovered']

# 合并新值
full_grouped = pd.merge(full_grouped, temp, on=['Country/Region', 'Date'])

# 用0填充na
full_grouped = full_grouped.fillna(0)

# 修复数据类型
cols = ['New cases', 'New deaths', 'New recovered']
full_grouped[cols] = full_grouped[cols].astype('int')

full_grouped['New cases'] = full_grouped['New cases'].apply(lambda x: 0 if x < 0 else x)

# print(full_grouped.head())

# table
day_wise = full_grouped.groupby('Date')['Confirmed', 'Deaths', 'Recovered', 'Active', 'New cases'].sum().reset_index()

# 按每100箱计算
day_wise['Deaths / 100 Cases'] = round((day_wise['Deaths'] / day_wise['Confirmed']) * 100, 2)
day_wise['Recovered / 100 Cases'] = round((day_wise['Recovered'] / day_wise['Confirmed']) * 100, 2)
day_wise['Deaths / 100 Recovered'] = round((day_wise['Deaths'] / day_wise['Recovered']) * 100, 2)

# 按照国家排名
day_wise['No. of countries'] = full_grouped[full_grouped['Confirmed'] != 0].groupby('Date')[
    'Country/Region'].unique().apply(len).values

cols = ['Deaths / 100 Cases', 'Recovered / 100 Cases', 'Deaths / 100 Recovered']
day_wise[cols] = day_wise[cols].fillna(0)

# print(day_wise.head())


# 获取最新数据
country_wise = full_grouped[full_grouped['Date'] == max(full_grouped['Date'])].reset_index(drop=True).drop('Date',
                                                                                                           axis=1)

# 按照国家统计
country_wise = country_wise.groupby('Country/Region')[
    'Confirmed', 'Deaths', 'Recovered', 'Active', 'New cases'].sum().reset_index()

# 百分比计算数据
country_wise['Deaths / 100 Cases'] = round((country_wise['Deaths'] / country_wise['Confirmed']) * 100, 2)
country_wise['Recovered / 100 Cases'] = round((country_wise['Recovered'] / country_wise['Confirmed']) * 100, 2)
country_wise['Deaths / 100 Recovered'] = round((country_wise['Deaths'] / country_wise['Recovered']) * 100, 2)

cols = ['Deaths / 100 Cases', 'Recovered / 100 Cases', 'Deaths / 100 Recovered']
country_wise[cols] = country_wise[cols].fillna(0)

print(country_wise.head())
print('-----------------------------')
# 加载人口数据集
pop = pd.read_csv("../data/population_by_country_2020.csv")

# 选择人口
pop = pop.iloc[:, :2]

# 重命名
pop.columns = ['Country/Region', 'Population']

# 合并数据
country_wise = pd.merge(country_wise, pop, on='Country/Region', how='left')

# 更新人口
cols = ['Burma', 'Congo (Brazzaville)', 'Congo (Kinshasa)', "Cote d'Ivoire", 'Czechia',
        'Kosovo', 'Saint Kitts and Nevis', 'Saint Vincent and the Grenadines',
        'Taiwan*', 'US', 'West Bank and Gaza']
pops = [54409800, 89561403, 5518087, 26378274, 10708981, 1793000,
        53109, 110854, 23806638, 330541757, 4543126]
for c, p in zip(cols, pops):
    country_wise.loc[country_wise['Country/Region'] == c, 'Population'] = p

# 缺失值
# country_wise.isna().sum()
# country_wise[country_wise['Population'].isna()]['Country/Region'].tolist()

# 群体的病例数
country_wise['Cases / Million People'] = round((country_wise['Confirmed'] / country_wise['Population']) * 1000000)

print(country_wise.head())
print('-----------------------------')
today = full_grouped[full_grouped['Date'] == max(full_grouped['Date'])].reset_index(drop=True).drop('Date', axis=1)[
    ['Country/Region', 'Confirmed']]
last_week = \
full_grouped[full_grouped['Date'] == max(full_grouped['Date']) - timedelta(days=7)].reset_index(drop=True).drop('Date',
                                                                                                                axis=1)[
    ['Country/Region', 'Confirmed']]

temp = pd.merge(today, last_week, on='Country/Region', suffixes=(' today', ' last week'))

# temp = temp[['Country/Region', 'Confirmed last week']]
temp['1 week change'] = temp['Confirmed today'] - temp['Confirmed last week']

temp = temp[['Country/Region', 'Confirmed last week', '1 week change']]

country_wise = pd.merge(country_wise, temp, on='Country/Region')

country_wise['1 week % increase'] = round(country_wise['1 week change'] / country_wise['Confirmed last week'] * 100, 2)

print(country_wise.head())

temp = full_table.groupby('Date')['Confirmed', 'Deaths', 'Recovered', 'Active'].sum().reset_index()
temp = temp[temp['Date']==max(temp['Date'])].reset_index(drop=True)

tm = temp.melt(id_vars="Date", value_vars=['Active', 'Deaths', 'Recovered'])
fig = px.treemap(tm, path=["variable"], values="value", height=225, width=1200,
                 color_discrete_sequence=[act, rec, dth])
fig.data[0].textinfo = 'label+text+value'
fig.show()
