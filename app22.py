import webbrowser
import pandas as pd
import dash
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_core_components as dcc
import plotly.graph_objects as go
import plotly.express as px
from dash.exceptions import PreventUpdate


app = dash.Dash()

def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

def load_dataset():
   
    global data
    data = pd.read_csv("global_terror.csv")

    pd.options.mode.chained_assignment = None
    global month_list
    month = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        "June": 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    month_list = [{"label": key, "value": value} for key, value in month.items()]
    print("\n month list = ", month_list)
    
    global year_list
    year_list = list(sorted(data['iyear'].unique()))

    global year_dict
    year_dict = {str(year): str(year) for year in year_list}

    global date_list
    date_list = [{"label": str(x), "value": str(x)} for x in range(1, 32)]
    print("\n date list = ", date_list)

    
    global region_list
    tmp_region = list(sorted(data['region_txt'].unique()))
    region_list = [{'label': str(i), 'value': str(i)} for i in tmp_region]
    print("\n region list = ", region_list)

    global country_list
    country_list = dict(data.groupby("region_txt")["country_txt"].unique().apply(list))
    print('\n country list ', country_list)
    
    global state_list
    state_list = dict(data.groupby("country_txt")["provstate"].unique().apply(list))
    
    global city_list
    city_list = dict(data.groupby("provstate")['city'].unique().apply(list))

    global attack_type_list
    tmp_attack = list(sorted(data['attacktype1_txt'].unique()))
    attack_type_list = [{'label': str(i), 'value': str(i)} for i in tmp_attack]
    #print("\n attack type ", attack_type_list)

    global chart_dropdown_values
    chart_dropdown_values = {
                            "Terrorist Organisation":"gname",
                            'Target Nationality' : "natlty_txt",
                            " Target Type" : "targttype1_txt",
                            " Type of Attack" : "attacktype1_txt",
                            "Weapon Type" : "weaptype1_txt",
                            "Region" : "region_txt",
                            "Country Attacked": " country_txt"
                                }
    chart_dropdown_values = [{"label": key, "value" : value} for key,value in chart_dropdown_values.items()]

def create_app_ui():
    main_layout = html.Div([
        html.H1(id="heading", children='Terrorism analysis'),

        dcc.Tabs(id="Tabs", value="Map", children=[
            dcc.Tab(label="Map Tool", id="Map tool", value="Map", children=[
                dcc.Tabs(id="subtabs", value="WorldMap", children=[
                    dcc.Tab(label="World Map Tool", id="World", value="WorldMap"),
                    dcc.Tab(label="India Map Tool",id="India",value="IndiaMap")]),

                dcc.Dropdown(id="month_drop",
                                         options=month_list, multi=True, placeholder='Select Month',
                                         ),
                dcc.Dropdown(id="date_drop",
                                         options=date_list, multi=True, placeholder='Select date',
                                        ),
                dcc.Dropdown(id="day_drop",value=1,
                                         options=date_list, multi=True, placeholder='Select Day',
                                            ),
                dcc.Dropdown(id="region_drop",
                                         options=region_list, multi=True, placeholder='Select Region',
                                        ),
                dcc.Dropdown(id="country_drop",
                                         options=country_list, multi=True, placeholder='Select Country',
                                         ),
                dcc.Dropdown(id="state_drop",
                                         options=state_list, multi=True, placeholder='Select Sate',
                                         ),
                dcc.Dropdown(id="city_drop",
                                         options=city_list, multi=True, placeholder='Select City',
                                         ),
                dcc.Dropdown(id="attack_drop",
                                         options=attack_type_list, multi=True, placeholder='Select Attack-type',
                                        ),
            html.Title(children="Select the year range"),
            dcc.RangeSlider(id="range-slider",
                                        min=min(year_list),
                                        max=max(year_list),
                                        value=[min(year_list), max(year_list)],
                                        marks=year_dict,
                                        step=None
                                        ),
            html.Br(),
            ]),
        dcc.Tab(label="Chart Tool", id="chart tool", value="Chart", children=[
            dcc.Tabs(id="subtabs2", value="WorldChart", children=[
                dcc.Tab(label="World Chart tool", id="WorldC", value="WorldChart"),
                dcc.Tab(label="India Chart tool", id="IndiaC", value="IndiaChart")]),
            dcc.Dropdown(id="Chart_drop", options=chart_dropdown_values, placeholder="Select option",
                         value="region_txt"),
            html.Br(),
            html.Br(),
            html.Hr(),
            dcc.Input(id="search", placeholder="Search Filter"),
            html.Hr(),
            html.Br(),
            dcc.RangeSlider(
                id='cyear_slider',
                min=min(year_list),
                max=max(year_list),
                value=[min(year_list), max(year_list)],
                marks=year_dict,
                step=None
            ),
            html.Br()
        ]),
    ]),
    html.Div(id = "graph-object", children="space for graph"),
    ])

    return main_layout
@app.callback(
    dash.dependencies.Output('graph-object', 'figure '),
    [
        dash.dependencies.Input('Tabs', 'value'),
        dash.dependencies.Input('month_drop', 'value'),
        dash.dependencies.Input('date_drop', 'value'),
        dash.dependencies.Input('region_drop','value'),
        dash.dependencies.Input('country_drop', 'value'),
        dash.dependencies.Input('attack_drop', 'value'),
        dash.dependencies.Input('city_drop', 'value'),
        dash.dependencies.Input('state_drop', 'value'),
        dash.dependencies.Input('day_drop', 'value'),
        dash.dependencies.Input('year_slider', 'value'),
        dash.dependencies.Input('cyear_slider', 'value'),
        dash.dependencies.Input("Chart_drop","value"),
        dash.dependencies.Input('search', 'value'),
        dash.dependencies.Input('subtabs2', 'value'),

    ]
    )
def update_app_ui(Tabs, month_value , date_value , region_value , country_value , state_value , city_value , attack_value , year_value,
                  chart_year_selector , chart_dp_value , search , subtabs2):

    figure = None

    if Tabs=="Map":
        year_range=range(year_value[0],year_value[1]+1)
        new_data=data(data["iyear"].isin(year_range))
        if month_value==[] or month_value is None:
            pass
        else:
            if date_value==[] or date_value is None:
                new_data = new_data[new_data["imonth"].isin(month_value)]
            else:
                new_data = new_data[new_data["imonth"].isin(month_value) & new_data['iday'].isin(date_value)]
#= filtering the region ,country ,state, and city data
        if region_value == [] or region_value is None:
            pass
        else:
            if country_value == [] or country_value is None:
                pass
            else:
                if state_value == [] or state_value is None:
                    new_data = new_data[(new_data["region_txt"].isin(region_value))&
                                         (new_data["country_txt"].isin(country_value))]
                else:
                    if city_value == [] or city_value is None:
                        new_data = new_data[(new_data["region_txt"].isin(region_value))&
                                            (new_data["country_txt"].isin(country_value))&
                                            (new_data["provstate"].isi(state_value))]
                    else:
                        new_data = new_data[(new_data["region_txt"].isin(region_value)) &
                                            (new_data["country_txt"].isin(country_value)) &
                                            (new_data["provstate"].isin(state_value))
                                            (new_data["city"].isin(city_value))]

        if attack_value == [] or attack_value is None:
            pass
        else:
            new_data = new_data[new_data["attacktype1_txt"].isin(attack_value)]


        mapFigure=go.Figure()
        if new_data.shape[0]:
            pass
        else:
            new_data=pd.DataFrame(columns=['iyear','imonth','iday','country_txt','region_txt','provstate','city','latitude','longitude','attacktype1_txt','nkill'])
            new_data.loc[0] = [0,0,0,None,None,None,None,None,None,None,None]

        mapFigure = px.scatter_mapbox(new_data, lat="latitude", lon="longitude", color="attacktype1_txt", hover_name="city", hover_data=["region_txt","attackype1_txt","country_txt","provstate","nkill","iday","iyear","imonth"], zoom=1)
       
        mapFigure.update_layout(mapbox_style="open-street-map", autosize=True, margin=dict(l=0,r=0,t=25,b=20),)
        figure = mapFigure

    elif Tabs== "Chart":
        figure = None
        year_range_c = range(chart_year_selector[0],chart_year_selector[1]+1)
        chart_data = data[data["iyear"].isin(year_range_c)]

        if subtabs2 =="WorldChart" :
            pass
        elif subtabs2 == "IndiaChart":
            chart_data = chart_data[(chart_data["region_txt"] == "South Asia") & (chart_data['country_txt']=="India")]
        if chart_dp_value is not None and chart_data.shape[0]:
            if search is not None:
                chart_data = chart_data.groupby("iyear")[chart_dp_value].value_counts().reset_index(name="count")
                chart_data = chart_data[chart_data[chart_dp_value].str.contains(search , case = False)]
            else:
                chart_data = chart_data.groupby("iyear")[chart_dp_value].value_counts().reset_index(name="count")

        if chart_data.shape[0]:
            pass
        else:
            chart_data = pd.DataFrame(columns=["iyear","count", chart_dp_value])
            chart_data.loc[0] = [0,0,"No data"]

        chartFigure=px.area(chart_data,x= "iyear",y = "count",color=chart_dp_value)
        figure = chartFigure
    return dcc.Graph(figure = figure)

@app.callback(
    Output('date_drop','options'),
    [Input('month_drop','value')]
    )
def update_date(month):
    option = []
    if month:
        option = [{"label":m,"value":m} for m in date_list]
    return  option

@app.callback(
    [Output("region_drop","value"),
     Output("region_drop","disabled"),
     Output("country_drop","value"),
     Output("country_drop","disabled")],
    [Input("subtabs","value")]
)
def update_r(tab):
    region = None
    disabled_r = False
    country = None
    disabled_c = False
    if tab == "WorldMap":
        pass
    elif tab == "IndiaMap":
        region=["South Asia"]
        disabled_r = True
        country = ["India"]
        disabled_c = True

    return region,disabled_c,disabled_r,country,
@app.callback(
    Output("country_drop","options"),
    [Input("region_drop","value")]
    )
def set_country_options(region_value):
    option = []

    if region_value is None:
        raise PreventUpdate
    else:
        for var in region_value:
            if var in country_list.keys():
                option.extend(country_list[var])
    return [{"label":m , "value":m } for m in option]

@app.callback(
    Output("city_drop","options"),
    [Input("state_drop","value")]
            )

def set_city_options(state_value):
    option = []
    if state_value is None:
        raise PreventUpdate
    else:
        for var in state_value:
            if var in city_list.keys():
                option.extend(city_list[var])
    return [{'label':m,'value':m} for m in option]

@app.callback(
    Output("state_drop","options"),
    [Input("country_drop","value")]
)
def set_state_options(country_value):
    option = []
    if country_value is None:
        raise PreventUpdate
    else:
        for var in country_value:
            if var in state_list.keys():
               option.extend(state_list[var])
    return [{"label": m , "value": m} for m in option]

def main():
    print("THE TERRORISM ANALYSIS PROJECT")
    load_dataset()
    open_browser()

    global app
    app.layout = create_app_ui()
    app.title = "Terrorrism analysis with insight"
    print('PROGRAM RAN SUCCESSFULLY !')
    print('EXECUTION END !')

   
    app.run_server()

    data = None
    app = None

if __name__ == '__main__':
    main()

