#随时间推移-数据分析可视化
import pandas as pd
import plotly.express as px

cnf, dth, rec, act = '#393e46', '#ff2e63', '#21bf73', '#fe9801'
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

full_table = pd.read_csv('../data/covid_19_clean_complete.csv', parse_dates=['Date'])

# 数据清理--------------------------
# 各个国家存活的 ->  确诊-死亡-出院=存活的
full_table['Active'] = full_table['Confirmed'] - full_table['Deaths'] - full_table['Recovered']

# 清理异常值,空值
full_table[['Province/State']] = full_table[['Province/State']].fillna('')
full_table[['Confirmed', 'Deaths', 'Recovered', 'Active']] = full_table[['Confirmed', 'Deaths', 'Recovered', 'Active']].fillna(0)

full_table['Recovered'] = full_table['Recovered'].astype(int)

temp = full_table.groupby('Date')['Recovered', 'Deaths', 'Active'].sum().reset_index()

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