import plotly.express as px
import pandas as pd
from sys import argv
import demjson

cnf, dth, rec, act = '#393e46', '#ff2e63', '#21bf73', '#fe9801'

json = argv[1]
data = demjson.decode(json)

df=pd.read_json(data,orient='records')
print(df)
fig = px.area(df,
              x="Date",
              y="Count",
              color='Case',
              height=600,
              color_discrete_sequence = [rec, dth, act],
	          line_group="Case")

fig.show()