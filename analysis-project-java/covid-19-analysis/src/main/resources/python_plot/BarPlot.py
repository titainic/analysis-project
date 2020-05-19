import plotly.express as px
import pandas as pd
from sys import argv
import demjson
from plotly.subplots import make_subplots

dth, act = '#ff2e63', '#fe9801'
json = argv[1]
print(json)
data = demjson.decode(json)

day_wise = pd.read_json(data, orient='records')

print(day_wise)

fig_c = px.bar(day_wise, x="Date", y="Confirmed", color_discrete_sequence=[act])
fig_d = px.bar(day_wise, x="Date", y="Deaths", color_discrete_sequence=[dth])

fig = make_subplots(rows=1, cols=2, shared_xaxes=False, horizontal_spacing=0.1,
                    subplot_titles=('确诊', '死亡'))

fig.add_trace(fig_c['data'][0], row=1, col=1)
fig.add_trace(fig_d['data'][0], row=1, col=2)

fig.update_layout(height=480)
fig.show()
