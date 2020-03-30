from Analysis import create_data, filter_country, generate_multitrend,generate_onetrend,filter_measures,create_measures
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dbm
import plotly.graph_objs as go
import re
import numpy as np
import plotly.express as px
import json
import math
import pandas as pd

# Set up the app
app = dash.Dash(__name__)
server = app.server

global country_df, measures_df,geojson_layer
global dict_countries


def create_dict_list_of_countries():
    dictlist = []
    unique_list = list(country_df["Country/Region"].unique())
    unique_list.append("World")
    for product_title in unique_list:
        dictlist.append({'value': product_title, 'label': product_title})
    return dictlist


country_df = create_data()
measures_data_df = create_measures()  
# path = r"C:\\repos\Covid_Impact_Mobility\data\Igismap\Australia_Polygon"
# with open(path) as geofile:
#     geojson_layer = json.load(geofile)


dict_countries = create_dict_list_of_countries()
dict_data_types = [{'value': "Confirmed", 'label': "Confirmed"},
                    {'value': "Deaths", 'label': "Deaths"},
                    {'value': "Recovered", 'label': "Recovered"}]

app.layout = html.Div([
    html.Div([
        html.H1('COVID-19 Country Visualization'),
        html.H2('Choose a country name'),
        dcc.Dropdown(
            id='country-dropdown',
            options=dict_countries,
            multi=True,
            value = ["World"]),
        html.H2('Choose a type of Graph'),
        dcc.Dropdown(
            id='data-types-dropdown',
            options=dict_data_types,
            value = "Confirmed"),
        html.H2('Map'),
        dcc.Graph(
            id='country-like-world'
        ),
        dcc.Graph(
            id='country-like-trend'
        )
    ], style={'width': '100%','height':'1000px', 'display': 'inline-block'})
])

@app.callback(Output('country-like-trend', 'figure'), [Input('country-dropdown', 'value'), Input("data-types-dropdown", "value")])
def update_graph(selected_dropdown_value_country, selected_dropdown_value_dataType):

    Countries = selected_dropdown_value_country
    type_data = selected_dropdown_value_dataType

    length = {}
    for country in Countries:
        data_country = filter_country(country_df,country)
        length[country] = len(data_country)

    Countries = [k for (k,v) in sorted(length.items(), key=lambda x: x[1])]
    Lines = [go.Scatter(x = np.arange(len(list(filter_country(country_df,country).index))), 
                                y = filter_country(country_df,country)[type_data], 
                                mode = "markers+lines", 
                                name = country) for country in Countries]
    figure = {
            'data' : Lines,
            'layout' : go.Layout(title = "COVID-19 {} Cases".format(type_data), xaxis = {'title': 'Days'}, yaxis = {'title': 'People'})
        }

    return figure

# @app.callback(Output('country-like-map', 'figure'), [Input('country-dropdown', 'value'), Input("data-types-dropdown", "value")])
# def update_map(selected_dropdown_value_country,selected_dropdown_value_dataType):   

#     Countries = selected_dropdown_value_country
#     type_data = selected_dropdown_value_dataType

#     df_ISO = measures_data_df[['ISO','COUNTRY']]
#     df_ISO.drop_duplicates(keep='first',inplace=True)

#     d = {}
#     for i in range(len(df_ISO)):
#         d[df_ISO.iloc[i]['COUNTRY']] = df_ISO.iloc[i]['ISO']

#     df = country_df.groupby(["Country/Region",'date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
#     df = df.groupby("Country/Region", as_index=False).agg({'Confirmed': 'max', 'Deaths':'max','Recovered':'max'})
    
#     df['CODE'] = df['Country/Region'].map(d) 

#     figure = go.Figure(data=go.Choropleth(
#     locations = df['CODE'],
#     z = df[type_data],
#     text = df['Country/Region'],
#     colorscale = 'Blues',
#     autocolorscale=False,
#     reversescale=False,
#     marker_line_color='darkgray',
#     marker_line_width=0.5,
#     colorbar_tickprefix = '',
#     colorbar_title = 'People',
#     ))

#     figure.update_layout(
#     title_text='COVID-19 Cases',
#     geo=dict(
#         showframe=False,
#         showcoastlines=False,
#         projection_type='orthographic'
#     ),
#     annotations = [dict(
#         x=0.55,
#         y=0.1,
#         xref='paper',
#         yref='paper',
#         showarrow = False)],
#     height=600, 
#     margin={"r":0,"t":0,"l":0,"b":0}
#     )
    
#     return figure

@app.callback(Output('country-like-world', 'figure'), [Input('country-dropdown', 'value'), Input("data-types-dropdown", "value")])
def update_Australia(selected_dropdown_value_country,selected_dropdown_value_dataType):   

    Countries = selected_dropdown_value_country
    type_data = selected_dropdown_value_dataType

    mapbox_access_token = "pk.eyJ1IjoiY29ydmV4IiwiYSI6ImNrODlvc2VzOTA4eHEzbW94d3RqMW13OWwifQ.4dmKFuWwbs6mtpBRbctJwA"

    data  = country_df.copy()
    data = data.groupby(['Province/State',"Country/Region"], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})

    repeated_names = {
        "Mainland China":"China",
        "US": 'United States of America',
        "UK": 'United Kingdom'
    }
    coordinates = pd.read_csv("./data/coordinates.csv")
    coordinates['Country/Region'] = coordinates['Country/Region'].map(repeated_names).fillna(coordinates['Country/Region'])
    coordinates['Province/State'] = coordinates['Province/State'].fillna(coordinates['Country/Region'])

    data = pd.merge(data,coordinates, on=['Province/State',"Country/Region"])

    data.dropna(inplace=True) 

    textList = []
    for area, region in zip(data['Province/State'], data['Country/Region']):
        if type(area) is str:
            if region == "Hong Kong" or region == "Macau" or region == "Taiwan":
                textList.append(area)
            else:
                textList.append(area+', '+region)
        else:
            textList.append(region)

    colorList = []

    for comfirmed, recovered, deaths in zip(data['Confirmed'], data['Recovered'], data['Deaths']):
        remaining = comfirmed - deaths - recovered
        colorList.append(remaining)

    figure = go.Figure(go.Scattermapbox(
        lat=data['lat'],
        lon=data['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            color=['#d7191c' if i > 0 else '#1a9622' for i in colorList],
            size=[i**(1/3) for i in data['Confirmed']],
            sizemin=1,
            sizemode='area',
            sizeref=2.*max([math.sqrt(i)
                           for i in data['Confirmed']])/(100.**2),
        ),
        text=textList,
        hovertext=['Confirmed: {:,d}<br>Recovered: {:,d}<br>Death: {:,d}<br>Death rate: {:.2%}'.format(int(i), int(j), int(k), t) for i, j, k, t in zip(data['Confirmed'],
                                                                                                                                         data['Recovered'],
                                                                                                                                         data['Deaths'],
                                                                                                                                         data['Deaths']/data['Confirmed'])],
        hovertemplate="<b>%{text}</b><br><br>" +
                        "%{hovertext}<br>" +
                        "<extra></extra>")
    )
    figure.update_layout(
        plot_bgcolor='#151920',
        paper_bgcolor='#ffffff',
        margin=go.layout.Margin(l=10, r=10, b=10, t=0, pad=40),
        hovermode='closest',
        height=800,
        transition={'duration': 50},
        annotations=[
        dict(
            x=.5,
            y=-.01,
            align='center',
            showarrow=False,
            text="Points are placed based on data geolocation levels.<br>Province/State level - Australia, China, Canada, and United States; Country level- other countries.",
            xref="paper",
            yref="paper",
            font=dict(size=10, color='#292929'),
        )],
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            style="dark",
            # The direction you're facing, measured clockwise as an angle from true north on a compass
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=14.056159,
                lon=6.395626
            ),
            pitch=0,
            zoom=1.02
        )
    )
        
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
