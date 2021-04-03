import os
import pathlib
import re
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf
import pandas as pd
import plotly.express as px  #(version 4.7.0)
import plotly.graph_objects as go
import dash  #pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import warnings
warnings.filterwarnings('ignore') 

police_kills = pd.read_csv("PoliceKillingsUS.csv", encoding = 'ISO-8859-1')
median_household_income_2015 = pd.read_csv("MedianHouseholdIncome2015.csv", encoding = 'ISO-8859-1')
percentage_people_below_poverty_level = pd.read_csv("PercentagePeopleBelowPovertyLevel.csv", encoding = 'ISO-8859-1')
percent_over_25_completed_highSchool = pd.read_csv("PercentOver25CompletedHighSchool.csv", encoding = 'ISO-8859-1')
states_abb = pd.read_csv("state-abbrevs.csv")

police_kills['year'] = pd.DatetimeIndex(police_kills['date']).year
df = police_kills.groupby(['state',"year"])[['id']].count()
df.reset_index(inplace=True)
states_abb = states_abb.rename(columns={"state": "state name", "abbreviation": "state"})
df = pd.merge(df,states_abb,left_on = ["state"], right_on  = ["state"])

police_kills['body_camera'] = police_kills['body_camera'].astype(str)

for i in range (len(police_kills)):
    if (police_kills['body_camera'][i]=='False'):
        police_kills['body_camera'][i]='0'
    else:
        police_kills['body_camera'][i]='1'

police_kills['body_camera'] = police_kills['body_camera'].astype(int)
df_cams = police_kills.groupby(['state',"year"])[['body_camera']].mean()
df_cams.reset_index(inplace=True)
df_cams["body_camera"] = df_cams["body_camera"] * 100

df_age = police_kills.groupby(['state',"year"])[['age']].mean()
df_age.reset_index(inplace=True)

df = police_kills.groupby(['state',"year"])[['id']].count()
df.reset_index(inplace=True)

percent_over_25_completed_highSchool = percent_over_25_completed_highSchool[percent_over_25_completed_highSchool.percent_completed_hs != "-"]
percent_over_25_completed_highSchool["percent_completed_hs"] = percent_over_25_completed_highSchool["percent_completed_hs"].astype(float)
percent_over_25_completed_highSchool = percent_over_25_completed_highSchool.groupby("Geographic Area")[["percent_completed_hs"]].mean().sort_values(by='percent_completed_hs')

percentage_people_below_poverty_level = percentage_people_below_poverty_level[percentage_people_below_poverty_level.poverty_rate != "-"]
percentage_people_below_poverty_level["poverty_rate"] = percentage_people_below_poverty_level["poverty_rate"].astype(float)
percentage_people_below_poverty_level = percentage_people_below_poverty_level.groupby("Geographic Area")[["poverty_rate"]].mean().sort_values(by='poverty_rate')

median_household_income_2015 = median_household_income_2015[median_household_income_2015["Median Income"] != "-"]
median_household_income_2015 = median_household_income_2015[median_household_income_2015["Median Income"] != "(X)"]
median_household_income_2015 = median_household_income_2015[median_household_income_2015["Median Income"] != "2,500-"]
median_household_income_2015 = median_household_income_2015[median_household_income_2015["Median Income"] != "250,000+"]
median_household_income_2015["Median Income"] = median_household_income_2015["Median Income"].astype(float)
median_household_income_2015 = median_household_income_2015.groupby("Geographic Area")[["Median Income"]].mean().sort_values(by='Median Income')

median_household_income_2015.reset_index(inplace=True)
percentage_people_below_poverty_level.reset_index(inplace=True)
percent_over_25_completed_highSchool.reset_index(inplace=True)

df1 = pd.merge(median_household_income_2015,percentage_people_below_poverty_level,left_on = ["Geographic Area"], right_on  = ["Geographic Area"])
df_features = pd.merge(df1,percent_over_25_completed_highSchool,left_on = ["Geographic Area"], right_on  = ["Geographic Area"])
df_features = df_features.rename(columns={"poverty_rate": "Poverty Rate", "percent_completed_hs": "Percent Completed High School", "Geographic Area": "States"})

# Initialize app

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server

# Load data

YEARS = [2015,2016,2017,2018,2019]

DEFAULT_OPACITY = 0.8

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

# App layout

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.Img(id="logo", src=app.get_asset_url("nova-logo.png")),
                html.H4(children="Fatal Police Shootings in the US"),
                html.P(
                    id="description",
                    children='''In recent years, police brutality has become a controversial issue in the United States. The number of people killed by law enforcement has been increasing over the years. 
                             Our data only contains death by firearms and does not include deaths of individuals in police custody, or fatal shootings by off-duty policemen. 
                             Here are the numbers of fatal police shootings:''',
                ),
            ],
        ),
        html.Br(),
        html.Div(
            id="div_card",
            children=[
                html.Div(
                    id="card1",
                    children=[
                        html.P(id="desc1",children="FATAL POLICE SHOOTINGS IN 2015:"),
                        html.H1(id="num1",children="➣ 965"),
                    ],
                ),
                html.Div(
                    id="card2",
                    children=[
                        html.P(id="desc2",children="FATAL POLICE SHOOTINGS IN 2016:"),
                        html.H1(id="num2",children="➣ 896"),
                    ],
                ),
                html.Div(
                    id="card3",
                    children=[
                        html.P(id="desc3",children="FATAL POLICE SHOOTINGS IN 2017:"),
                        html.H1(id="num3",children="➣ 903"),
                    ],
                ),
                html.Div(
                    id="card4",
                    children=[
                        html.P(id="desc4",children="FATAL POLICE SHOOTINGS IN 2018:"),
                        html.H1(id="num4",children="➣ 878"),
                    ],
                ),
                html.Div(
                    id="card5",
                    children=[
                        html.P(id="desc5",children="FATAL POLICE SHOOTINGS IN 2019:"),
                        html.H1(id="num5",children="➣ 853"),
                    ],
                ),
                html.Div(
                    id="card6",
                    children=[
                        html.P(id="desc6",children="TOTAL FATAL POLICE SHOOTINGS:"),
                        html.H1(id="num6",children="➣ 4 495"),
                    ],
                ),
            ],
        ),
        html.Br(),
        html.Br(),
           html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the year:",
                                ),
                                dcc.Slider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=min(YEARS),
                                    marks={
                                        str(year): {
                                            "label": str(year),
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for year in YEARS
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Heatmap of Police Fatal Shoots in the US by State in year {0}".format(
                                        min(YEARS)
                                    ),
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=dict(
                                        layout=dict(
                                            mapbox=dict(
                                                layers=[],
                                                accesstoken=mapbox_access_token,
                                                style=mapbox_style,
                                                center=dict(
                                                    lat=38.72490, lon=-95.61446
                                                ),
                                                pitch=0,
                                                zoom=3.5,
                                            ),
                                            autosize=True,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select chart:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Median Household Income",
                                    "value": "Median Income",
                                },
                                {
                                    "label": "Percentage People Below Poverty Level",
                                    "value": "Poverty Rate",
                                },
                                {
                                    "label": "Percentage Over 25 Completed High School",
                                    "value": "Percent Completed High School",
                                },
                            ],
                            value="Median Income",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)

@app.callback(
    [Output(component_id='county-choropleth', component_property='children'),
     Output(component_id='county-choropleth', component_property='figure')],
    [Input(component_id='years-slider', component_property='value')]
)
def update_graph(option_slctd):
    container = "The year chosen by user was: {}".format(option_slctd)

    dff = df.copy()
    dff = dff[dff["year"] == option_slctd]

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state',
        scope="usa",
        color='id',
        hover_data= ["id","state"],
        color_continuous_scale=px.colors.sequential.Darkmint,
        labels={'id': 'Fatal Shootings'},
        template='plotly_dark'
    )
    
    return container, fig

@app.callback(Output("heatmap-title", "children"), [Input("years-slider", "value")])
def update_map_title(year):
    return "Heatmap of fatal police shootings \
				by state in year {0}".format(
        year
    )

@app.callback(
   Output(component_id='selected-data', component_property='figure'),
       Input(component_id='chart-dropdown', component_property='value')
)
def interactiveGraph(value):
    df = df_features.copy()
    df = df.sort_values(value)
    fig = px.bar(data_frame=df[['States',value]], x='States', y=value,color_discrete_sequence =['#92ddc8'],template='plotly_dark')
    fig.update_xaxes(title_text="States")
    fig.update_xaxes(title_font_size=15)  
    fig.update_yaxes(title_font_size=15) 
    fig.update_layout(
    xaxis = dict(
    tickfont = dict(size=8)))
    return fig

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)