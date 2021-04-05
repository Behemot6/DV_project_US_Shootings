import pandas as pd
import plotly.express as px  #(version 4.7.0)
import plotly.graph_objects as go
import dash  #pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import warnings
warnings.filterwarnings('ignore')

# Read data
median_household_income_2019 = pd.read_csv("median_household_income_2019.csv")
population_2019 = pd.read_csv("population_2019.csv")
police_kills = pd.read_csv("PoliceKillingsUS.csv", encoding = 'ISO-8859-1')
states_abb = pd.read_csv("state-abbrevs.csv")
share_race_by_state_2019 = pd.read_csv("share_race_by_state_2019.csv")
share_race_us = pd.read_excel('percentage-of-us-population-by-race.xlsx', sheet_name='Data')
kills_by_state = pd.read_csv("kills_groupby.csv")  

police_kills['year'] = pd.DatetimeIndex(police_kills['date']).year
df = police_kills.groupby(['state',"year"])[['id']].count()
df.reset_index(inplace=True)
states_abb = states_abb.rename(columns={"state": "state name", "abbreviation": "state"})
df = pd.merge(states_abb,df,left_on = ["state"], right_on  = ["state"])
df = df.rename(columns={"id": "Number of Fatal Shootings"})
df = kills_by_state

median_household_income_2019[['state','Median Income']] = median_household_income_2019['Location'].str.split(",",expand=True,)
median_household_income_2019.drop(columns=["Location","Median Annual Household Income"], inplace=True)
median_household_income_2019['Median Income'] = median_household_income_2019['Median Income'].str.replace('"','')
median_household_income_2019['Median Income'] = median_household_income_2019['Median Income'].str.replace('$','')

population_2019[['state','Total Population']] = population_2019['Location'].str.split(",",expand=True,)
population_2019.drop(columns=["Location","Total Residents"], inplace=True)
population_2019['Total Population'] = population_2019['Total Population'].str.replace('"','')

share_race_by_state_2019[['state','Percentage of White Race',"Percentage of Black Race","Hispanic","Asian","Native1","Native2","Other","Total"]] = share_race_by_state_2019['Location'].str.split(",",expand=True)
share_race_by_state_2019 = share_race_by_state_2019[["state","Percentage of White Race","Percentage of Black Race"]]

share_race_by_state_2019['Percentage of White Race'] = share_race_by_state_2019['Percentage of White Race'].str.replace('"','')
share_race_by_state_2019['Percentage of White Race'] = share_race_by_state_2019['Percentage of White Race'].astype(float)
share_race_by_state_2019['Percentage of White Race'] = share_race_by_state_2019[['Percentage of White Race']] * 100
share_race_by_state_2019['Percentage of Black Race'] = share_race_by_state_2019['Percentage of Black Race'].str.replace('"','')
share_race_by_state_2019['Percentage of Black Race'] = share_race_by_state_2019['Percentage of Black Race'].astype(float)
share_race_by_state_2019['Percentage of Black Race'] = share_race_by_state_2019[['Percentage of Black Race']] * 100

df_race = police_kills.groupby("race")[["id"]].count()
df_race.reset_index(inplace=True)

share_race_us = share_race_us.rename(columns={"Unnamed: 0": "race"})

for i in range (len(share_race_us)):
    if (share_race_us['race'][i]=='Non-Hispanic White'):
        share_race_us['race'][i]='White'
    elif (share_race_us['race'][i]=='Hispanics (may be of any race)'):
        share_race_us['race'][i]='Hispanic'
    elif (share_race_us['race'][i]=='Black or African American'):
        share_race_us['race'][i]='Black'
    elif (share_race_us['race'][i]=='Asian'):
        share_race_us['race'][i]='Asian'
    elif (share_race_us['race'][i]=='American Indian and Alaska Native'):
        share_race_us['race'][i]='Native'
    elif (share_race_us['race'][i]=='Native Hawaiian and Other Pacific Islander'):
        share_race_us['race'][i]='Native'
    else:
        share_race_us['race'][i]='Other'

share_race_us=share_race_us.groupby("race").sum()
share_race_us.reset_index(inplace=True)

df_features = pd.merge(share_race_by_state_2019,population_2019,left_on = ["state"], right_on  = ["state"])
df_features = pd.merge(df_features,median_household_income_2019,left_on = ["state"], right_on  = ["state"])
df_features = df_features.rename(columns={"state": "state name"})
df_features = pd.merge(states_abb,df_features,left_on = ["state name"], right_on  = ["state name"])
df_features["Total Population"] = df_features["Total Population"].astype(int)
df_features["Median Income"] = df_features["Median Income"].astype(int)
df_features["state name"] = df_features["state name"].astype(str)

df_race = police_kills.groupby(['race',"year"])[['id']].count()
df_race.reset_index(inplace=True)
df_race = df_race.rename(columns={"id": "Number of Fatal Shootings"})

# Initialize app

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],)
app.title = 'Fatal Police Shootings in the US'

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
        html.H4(id="title",children="Fatal Police Shootings in the US"),
        html.P(
            id="description",
            children='''In recent years, police brutality has become a controversial issue in the United States. Beginning in 2015, the Washington Post started to record every killing made by law enforcement, and it shows that the number of people killed by law enforcement has been increasing over the years. Our data only contains death by firearms and does not include deaths of individuals in police custody, or fatal shootings by off-duty policemen. Here are the numbers of fatal police shootings:''',
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
        html.P(
            id="description2",
            children='''The pie chart below shows a racial bias in US police killings. Even though the victims are a majority of white people (50.5%), compared to the distribution of the United States population by ethnicity, we realized that Black people are killed at a rate of 2.6 times more than White people, and Hispanics at a rate of 1.3 times more. Over the past five years, we can see that there haven’t been any changes in the racial disparity in deadly police shootings.  The rate of police killings of people of color is constant. ''',
                ),
        html.Div(
            id="app-container2",
            children=[
                html.Div(
                    id="left-column2",
                    children=[
                        html.Div(
                            id="heatmap-container2",
                            children=[
                                html.P(
                                    "Total population distribution by ethnicity in the US (2019)",
                                    id="heatmap-title2",
                                ),
                                dcc.Graph(
                                    id="county-choropleth2",
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
                    id="left-column3",
                    children=[
                        html.Div(
                            id="heatmap-container3",
                            children=[
                                html.P(
                                    "Fatal shootings distribution by ethnicity in the US (2015-2019)",
                                    id="heatmap-title3",
                                ),
                                dcc.Graph(
                                    id="county-choropleth3",
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
            ],
        ),
        html.P(
            id="description3",
            children='''The total number of deadly police shootings is only increasing every year. Is racial bias the only problem in US law enforcement? No, the following charts indicate that socioeconomic factors (income, population) have also an important influence on this issue. California, Texas, and Florida are the states with the most fatal shootings, as they are the most populated states. The chart of race share by states also shows that CA, TX, and FL are from the bottom 10 of “percentage of White population”.''',
            ),
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
            id="left-column4",
            children=[
                html.Div(
                    id="heatmap-container4",
                    children=[
                        html.P(id="heatmap-title4", children="Select chart:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Total Population (2019)",
                                    "value": "Total Population",
                                },
                                {
                                    "label": "Median Household Income (2019)",
                                    "value": "Median Income",
                                },
                                {
                                    "label": "Percentage of White Population (2019)",
                                    "value": "Percentage of White Race",
                                },
                                {
                                    "label": "Percentage of Black Population (2019)",
                                    "value": "Percentage of Black Race",
                                },
                            ],
                            value="Total Population",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="county-choropleth4",
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
        ),
        html.P(
            id="description4",
            children='''Police brutality in the United States has only been increasing over the past few years, and it remains a very current issue. Since the beginning of the year 2021, 213 people were shot and killed by US law enforcement. A new name was just added to the Washington Post records on Monday 29th of March: Adam Toledo, a 13-year-old boy that was killed by the Chicago Police. Our analyze, and visualization of Fatal police shootings in the United States indicates that socio-economic factors such as race, neighborhoods, social status, poverty, and age are all relevant.''',
        ),
        html.Div(
            id="cards_footer",
            children=[
                html.Div(
                    id="card7",
                    children=[
                        html.P(id="desc13",children="Authors:"),
                        html.P(id="desc7",children="Bruno Soares | m20200658"),
                        html.P(id="desc8",children="Edgardo Juarez | m20200749"),
                        html.P(id="desc9",children="Gonçalo Reis | m20200650"),
                        html.P(id="desc10",children="Li-lou Dang-Thai | m20200743"),
                        html.P(id="desc14",children="Data Source: Kaggle and KFF"),
                    ],
                ),
            ],
        ),
    ],
)

@app.callback(
    [Output(component_id='county-choropleth2', component_property='children'),
     Output(component_id='county-choropleth2', component_property='figure')],
    [Input(component_id='years-slider', component_property='value')]
)
def update_graph2(option_slctd):
    container = "The year chosen by user was: {}".format(option_slctd)

    fig = px.pie(share_race_us, values=2019, names='race',template='plotly_dark', color="race", color_discrete_map={'White':"#1b3338",
                                 'Black':'#437360',
                                 'Hispanic':'#5c9b71',
                                 'Asian':'#81b69d',
                                 'Native':'#92ddc8',
                                 'Other':'b9e6c9'})
    fig.update_traces(textposition='inside')
    fig.update_layout(uniformtext_minsize=18, uniformtext_mode='hide')
    
    return container, fig

@app.callback(Output("heatmap-title2", "children"), [Input("years-slider2", "value")])
def update_map_title(year):
    return "Population share race in US"

@app.callback(
    [Output(component_id='county-choropleth3', component_property='children'),
     Output(component_id='county-choropleth3', component_property='figure')],
    [Input(component_id='years-slider', component_property='value')]
)
def update_graph2(option_slctd):
    container = "The year chosen by user was: {}".format(option_slctd)

    fig = px.pie(df_race, values='Number of Fatal Shootings', names='race', labels={'id': 'Fatal Shootings', "race": "Race"}
             ,template='plotly_dark', color="race", color_discrete_map={'White':"#1b3338",
                                 'Black':'#437360',
                                 'Hispanic':'#5c9b71',
                                 'Asian':'#81b69d',
                                 'Native':'#92ddc8',
                                 'Other':'b9e6c9'})
    fig.update_traces(textposition='inside')
    fig.update_layout(uniformtext_minsize=18, uniformtext_mode='hide')
    
    return container, fig

@app.callback(Output("heatmap-title3", "children"), [Input("years-slider2", "value")])
def update_map_title(year):
    return "Fatal shootings by race in US"

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
        color='Number of Fatal Shootings',
        hover_data= ["state name"],
        color_continuous_scale=px.colors.sequential.Darkmint,
        labels={'Number of Fatal Shootings': 'Fatal Shootings'},
        template='plotly_dark'
    )
    
    return container, fig

@app.callback(Output("heatmap-title", "children"), [Input("years-slider", "value")])
def update_map_title(year):
    return "Heatmap of fatal police shootings by state in year {0}".format(year)

@app.callback(
   Output(component_id='county-choropleth4', component_property='figure'),
       [Input(component_id='chart-dropdown', component_property='value')]
)

def interactiveGraph(value):
    df = df_features.copy()
    df = df.sort_values(value)
    fig = px.bar(data_frame=df[["state name",'state',value]], x='state', y=value,color_discrete_sequence =['#92ddc8'],template='plotly_dark', hover_data=["state name"])
    fig.update_xaxes(title_text="States")
    fig.update_xaxes(title_font_size=15)  
    fig.update_yaxes(title_font_size=15) 
    fig.update_layout(
    xaxis = dict(
    tickfont = dict(size=10.5)))
    return fig

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)