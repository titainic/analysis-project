#随时间推移-数据分析可视化
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

cnf, dth, rec, act = '#393e46', '#ff2e63', '#21bf73', '#fe9801'
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


temp = full_table.groupby('Date')['Recovered', 'Deaths', 'Active'].sum().reset_index()

print('----------')
#行列互换
temp = temp.melt(id_vars="Date",
                 value_vars=['Recovered', 'Deaths', 'Active'],
                 var_name='Case',
                 value_name='Count')


fig = px.area(temp,
              x='Date',
              y='Count',
              color='Case',
              height=600,
              title='时间线显示存活,死亡,治愈',
              color_discrete_sequence = [rec, dth, act])
fig.update_layout(xaxis_rangeslider_visible=True)
fig.show()