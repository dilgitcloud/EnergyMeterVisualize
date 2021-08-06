import dash
#import dash_design_kit as ddk
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import json


myfile = open("EnergyMeterData.txt","r")#SensorDataStream-3-2021-07-26.csv","r")
mychar = myfile.read(1)
#################################################################### Retrieving the Energy Meter data from the file into a pandas dataframe 'df'      ##########################
df = pd.DataFrame()
my_str=""
ij=0	
while mychar:    
#    print(dict1)
    if mychar=='}':
        myline = my_str + "}"
        my_str = ""
        dictline = myline.strip()
        #print(dictline)
        datajs = json.loads(dictline)
        df = df.append(datajs,ignore_index=True)
        ij=ij+1	
        #print(ij)
    else:
        my_str = my_str + mychar	
    mychar = myfile.read(1)	
#print(dictline)
myfile.close()

############################################################################################################################################

#df = pd.read_csv("EnergyMeterData_ManuallyCreated.csv")	#"sensor_v2_28-06-2021.csv")
df.loc[8,["ApparentPower"]] = 200		#manual modification to see if logics work
df["Time"] = pd.to_datetime(df["Time"])

time_gap_between_readings_in_secs = 10

n_readings_in_a_min = int(60/time_gap_between_readings_in_secs)
tm = [i for i in range(0,len(df)*time_gap_between_readings_in_secs,time_gap_between_readings_in_secs)]
#print(tm)
#breakpoint()
fig_current_timewise = px.scatter(df, x=df["Time"], y=df["Current"],title="Current vs Time")
fig_actp_timewise = px.scatter(df, x=df["Time"], y=df["ActivePower"],title="ActivePower vs Time")
fig_appp_timewise = px.scatter(df, x=df["Time"], y=df["ApparentPower"],title="ApparentPower vs Time")

fig_current_hist = px.histogram(df, x="Current",title="Current Histogram")
fig_actp_hist = px.histogram(df, x="ActivePower",title="ActivePower Histogram")
fig_appp_hist = px.histogram(df, x="ApparentPower",title="ApparentPower Histogram")


mx_vi = round(max(df["Voltage"]*df["Current"]),2)

VI_msg = "My peak V*I is "+str(mx_vi)

data_of_the_minute = df["ApparentPower"].iloc[n_readings_in_a_min*0:n_readings_in_a_min*1]	
mn = round(data_of_the_minute.mean(),2)

fig_gauge_peakVI = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = mn,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Variation of Average Usage (App-Power) across months"}))

#fig_gauge_peakVI.show()

curr_mn = round(df["Current"].mean(),4)
curr_stdev = round(df["Current"].std(),4)
load_variation = "Mean Current is "+str(curr_mn)+" and Standard Deviation of Current is "+str(curr_stdev)

#breakpoint()

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1(children='Energy Visualisation'),	
    dcc.Tabs([
        dcc.Tab(label='Tab one Graphical', children=[
    #html.H1(children='Graphical'),

    #html.Div(children='''
    #    Dash: A web application framework for Python.
    #'''),
    html.Div(
    dcc.RadioItems(id='Radio-graphselect1',
    options=[
        {'label': 'Current', 'value': 'CURR'},
        {'label': 'ActivePower', 'value': 'ACTP'},
        {'label': 'ApparentPower', 'value': 'APPP'}
    ],

    value='CURR',
    labelStyle={'display': 'block'}

    ),style={"padding": "10px",'width': 1000}
    ),
	
    dcc.Graph(
        id='curr_actp_appp-graph_time'
    ),
    
    dcc.Graph(
        id='curr_actp_appp-graph_hist'
    )	
    ]),

    dcc.Tab(label='Tab two Measures', children=[html.Div([
            #html.H1('Measures')
        #])
    dbc.Row([dbc.Col(html.Div([
    html.Label("Move the slider to know mean apparent power for each month"),
    dcc.Slider(
        id='my-minute-slider',
	marks={i:'{}st month'.format(i) for i in range(0,int(tm[-1]/60)+1)},
        min=0,
        max=tm[-1]/60,#in minutes
        step=1,
        value=2,
    ),
    html.Div(id='slider-show-selection'),

    dcc.Graph(figure=fig_gauge_peakVI,
        id='peakVI_gauge'
    ),

    ]),
    width={'size': 6, 'offset': 3}, style={'border': '1px solid'}
    ),
    
    ]),
    ],style={'marginBottom': 50, 'marginTop': 25,'textAlign': 'center'}),
    
    dbc.Row([dbc.Col(	
    dbc.Alert([
    html.Div(
            children=VI_msg,
            id="alert-auto",
            #is_open=True,
            style={'textAlign': 'center'}
        ),
    ]), 
    	#html.Label(load_variation) 
    	#]),#style={'marginBottom': 50, 'marginTop': 25,'textAlign': 'center'}),
    width={'size': 6, 'offset': 3},align="center" 
    )]),

    dbc.Row([dbc.Col(	
    dbc.Alert([
    html.Div(
            children=load_variation,
            id="alert-auto2",
            #is_open=True,
            style={'textAlign': 'center'}
        ),
    ]), 
    #html.Label(load_variation) 
    #]),#style={'marginBottom': 50, 'marginTop': 25,'textAlign': 'center'}),
    width={'size': 6, 'offset': 3},align="center" 
    )]),
    
    #dcc.Graph(figure=fig_gauge_peakVI,
    #    id='peakVI_gauge'
    #),
 	
    ])
    ])
])

#style={'width': '50%','padding-left':'25%', 'padding-right':'25%'}

@app.callback(
    Output('curr_actp_appp-graph_time', 'figure'),
    Output('curr_actp_appp-graph_hist', 'figure'),
    Output('peakVI_gauge','figure'),	
    #Output('slider-show-selection','children'),	
    Input('Radio-graphselect1', 'value'),
    Input('my-minute-slider', 'value'))

def update_graph(choose_which_graph,minute_count):
    #breakpoint()	
    data_of_the_minute = df["ApparentPower"].iloc[n_readings_in_a_min*minute_count:n_readings_in_a_min*(minute_count+1)]	
    mn = round(data_of_the_minute.mean(),2)
    
    fig_gauge_peakVI = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = mn,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Variation of Average Usage (App-Power) across months"}))

    #fig_gauge_peakVI.add_trace(go.Indicator(value = mn)) 	
    if	choose_which_graph=='CURR':
        return fig_current_timewise, fig_current_hist,fig_gauge_peakVI#"Mean Apparent power in " + str(minute_count)+ "th minute  is "+str(mn)
    elif choose_which_graph=='ACTP': 	
        return fig_actp_timewise, fig_actp_hist,fig_gauge_peakVI#"Mean Apparent power in " + str(minute_count)+ "th minute  is "+str(mn)
    elif choose_which_graph=='APPP': 	
        return fig_appp_timewise, fig_appp_hist,fig_gauge_peakVI#"Mean Apparent power in " + str(minute_count)+ "th minute  is "+str(mn)

if __name__ == '__main__':
    app.run_server(debug=True)

