from Analysis import create_data, filter_country, generate_multitrend,generate_onetrend,filter_measures,create_measures
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_table.FormatTemplate as FormatTemplate
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
from datetime import datetime
from datetime import timedelta  


# Set up the app
app = dash.Dash(__name__)
server = app.server

global country_df, measures_df,geojson_layer
global dict_countries

def make_country_table(countryName):
    '''This is the function for building df for Province/State of a given country'''
    countryTable = country_df[country_df['Country/Region'] == countryName]

    countryTable = countryTable.groupby(['Province/State','Country/Region','date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
    countryTable = countryTable.sort_values(by=['date_file'])
    countryTable.drop_duplicates(subset = ['Province/State','Country/Region'], keep = 'last', inplace = True)

    repeated_names = {
        "Mainland China":"China",
        "US": 'United States of America',
        "UK": 'United Kingdom'
    }
    coordinates = pd.read_csv("./data/coordinates.csv")
    coordinates['Country/Region'] = coordinates['Country/Region'].map(repeated_names).fillna(coordinates['Country/Region'])
    coordinates['Province/State'] = coordinates['Province/State'].fillna(coordinates['Country/Region'])
    coordinates = coordinates[coordinates['Country/Region'] == countryName]
    
    countryTable = pd.merge(countryTable,coordinates, on=['Province/State','Country/Region'])


    # Suppress SettingWithCopyWarning
    pd.options.mode.chained_assignment = None
    countryTable['Active'] = countryTable['Confirmed'] - countryTable['Recovered'] - countryTable['Deaths']
    countryTable['Death rate'] = countryTable['Deaths']/countryTable['Confirmed']
    countryTable = countryTable[['Province/State', 'Active', 'Confirmed', 'Recovered', 'Deaths', 'Death rate', 'Latitude', 'Longitude']]
    countryTable = countryTable.sort_values(
        by=['Active', 'Confirmed'], ascending=False).reset_index(drop=True)
    # Set row ids pass to selected_row_ids
    countryTable['id'] = countryTable['Province/State']
    countryTable.set_index('id', inplace=True, drop=False)
    # Turn on SettingWithCopyWarning
    pd.options.mode.chained_assignment = 'warn'
    return countryTable

def make_europe_table(europe_list):

    '''This is the function for building df for Europe countries'''
    europe_table = country_df.loc[country_df['Country/Region'].isin(europe_list)]

    europe_table = europe_table.groupby(['Province/State','Country/Region','date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
    europe_table = europe_table.sort_values(by=['date_file'])
    europe_table.drop_duplicates(subset = ['Province/State','Country/Region'], keep = 'last', inplace = True)
    repeated_names = {
        "Mainland China":"China",
        "US": 'United States of America',
        "UK": 'United Kingdom'
    }
    coordinates = pd.read_csv("./data/coordinates.csv")
    coordinates['Country/Region'] = coordinates['Country/Region'].map(repeated_names).fillna(coordinates['Country/Region'])
    coordinates['Province/State'] = coordinates['Province/State'].fillna(coordinates['Country/Region'])
    coordinates = coordinates[coordinates['Country/Region'].isin(europe_list)]    
    europe_table = pd.merge(europe_table,coordinates, on=['Province/State','Country/Region'])

    # Suppress SettingWithCopyWarning
    pd.options.mode.chained_assignment = None
    europe_table['Active'] = europe_table['Confirmed'] - europe_table['Recovered'] - europe_table['Deaths']
    europe_table['Death rate'] = europe_table['Deaths']/europe_table['Confirmed']
    europe_table = europe_table[['Country/Region', 'Active', 'Confirmed', 'Recovered', 'Deaths', 'Death rate', 'Latitude', 'Longitude']]
    europe_table = europe_table.sort_values(
            by=['Active', 'Confirmed'], ascending=False).reset_index(drop=True)
    # Set row ids pass to selected_row_ids
    europe_table['id'] = europe_table['Country/Region']
    europe_table.set_index('id', inplace=True, drop=False)
    # Turn on SettingWithCopyWarning
    pd.options.mode.chained_assignment = 'warn'
    return europe_table

def make_dcc_country_tab(countryName, dataframe):
    '''This is for generating tab component for country table'''
    return dcc.Tab(label=countryName,
            value=countryName,
            className='custom-tab',
            selected_className='custom-tab--selected',
            children=[dash_table.DataTable(
                    id='datatable-interact-location-{}'.format(countryName),
                    # Don't show coordinates
                    columns=[{"name": i, "id": i, "type": "numeric","format": FormatTemplate.percentage(2)}
                             if i == 'Death rate' else {"name": i, "id": i}
                             for i in dataframe.columns[0:6]],
                    # But still store coordinates in the table for interactivity
                    data=dataframe.to_dict("rows"),
                    row_selectable="single" if countryName != 'Schengen' else False,
                    sort_action="native",
                    style_as_list_view=True,
                    style_cell={'font_family': 'Arial',
                                  'font_size': '1.1rem',
                                  'padding': '.1rem',
                                  'backgroundColor': '#f4f4f2', },
                    fixed_rows={'headers': True, 'data': 0},
                    style_table={'minHeight': '800px',
                                 'height': '800px',
                                 'maxHeight': '800px',
                                 #'overflowX': 'scroll'
                                 },
                    style_header={'backgroundColor': '#f4f4f2',
                                    'fontWeight': 'bold'},
                    style_cell_conditional=[{'if': {'column_id': 'Province/State'}, 'width': '26%'},
                                            {'if': {'column_id': 'Country/Region'}, 'width': '26%'},
                                            {'if': {'column_id': 'Active'}, 'width': '14.2%'},
                                            {'if': {'column_id': 'Confirmed'}, 'width': '15.8%'},
                                            {'if': {'column_id': 'Recovered'}, 'width': '15.8%'},
                                            {'if': {'column_id': 'Deaths'}, 'width': '14.2%'},
                                            {'if': {'column_id': 'Death rate'}, 'width': '14%'},
                                            {'if': {'column_id': 'Active'}, 'color':'#e36209'},
                                            {'if': {'column_id': 'Confirmed'}, 'color': '#d7191c'},
                                            {'if': {'column_id': 'Recovered'}, 'color': '#1a9622'},
                                            {'if': {'column_id': 'Deaths'}, 'color': '#6c6c6c'},
                                            {'textAlign': 'center'}],
                        )
            ]
          )

def create_dict_list_of_countries():
    dictlist = []
    unique_list = list(country_df["Country/Region"].unique())
    unique_list.append("World")
    for product_title in unique_list:
        dictlist.append({'value': product_title, 'label': product_title})
    return dictlist


country_df = create_data()
measures_data_df = create_measures()  


data_global = country_df.groupby(['Province/State','Country/Region','date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
data_global = data_global.sort_values(by=['date_file'], ascending = False ).reset_index(drop=True)
data_global = data_global[data_global['date_file'] == data_global['date_file'][0]]

# Save numbers into variables to use in the app
confirmedCases = data_global['Confirmed'].sum()
deathsCases = data_global['Deaths'].sum()
recoveredCases = data_global['Recovered'].sum()

# Construct confirmed cases dataframe for line plot and 24-hour window case difference
df_confirmed = country_df[['date_file','Confirmed']]
df_confirmed = df_confirmed.groupby('date_file', as_index=False).agg({'Confirmed': 'sum'})
df_confirmed = df_confirmed.sort_values(by=['date_file'],ascending = False)
df_confirmed.reset_index(inplace = True)
df_confirmed['plusNum'] = df_confirmed['Confirmed'].diff(periods=-1).fillna(0)
plusConfirmedNum = df_confirmed['plusNum'][0]
df_confirmed['plusPercentNum'] = df_confirmed['plusNum']/df_confirmed['Confirmed']
plusPercentNum1 = df_confirmed['plusPercentNum'][0]

# Construct recovered cases dataframe for line plot and 24-hour window case difference
df_recovered = country_df[['date_file','Recovered']]
df_recovered = df_recovered.groupby('date_file', as_index=False).agg({'Recovered': 'sum'})
df_recovered = df_recovered.sort_values(by=['date_file'],ascending = False)
df_recovered.reset_index(inplace = True)
df_recovered['plusNum'] = df_recovered['Recovered'].diff(periods=-1).fillna(0)
plusRecoveredNum = df_recovered['plusNum'][0]
df_recovered['plusPercentNum'] = df_recovered['plusNum']/df_recovered['Recovered']
plusPercentNum2 = df_recovered['plusPercentNum'][0]

# Construct death case dataframe for line plot and 24-hour window case difference
df_deaths = country_df[['date_file','Deaths']]
df_deaths = df_deaths.groupby('date_file', as_index=False).agg({'Deaths': 'sum'})
df_deaths = df_deaths.sort_values(by=['date_file'],ascending = False)
df_deaths.reset_index(inplace = True)
df_deaths['plusNum'] = df_deaths['Deaths'].diff(periods=-1).fillna(0)
plusDeathNum = df_deaths['plusNum'][0]
df_deaths['plusPercentNum'] = df_deaths['plusNum']/df_deaths['Deaths']
plusPercentNum3 = df_deaths['plusPercentNum'][0]

# Construct remaining case dataframe for line plot and 24-hour window case difference
country_df['Remained'] = country_df['Confirmed'] - country_df['Recovered']
df_remaining = country_df[['date_file','Remained']]
df_remaining = df_remaining.groupby('date_file', as_index=False).agg({'Remained': 'sum'})
df_remaining = df_remaining.sort_values(by=['date_file'],ascending = False)
df_remaining.reset_index(inplace = True)
df_remaining['plusNum'] = df_remaining['Remained'].diff(periods=-1).fillna(0)
plusRemainedNum = df_remaining['plusNum'][0]
df_remaining['plusPercentNum'] = df_remaining['plusNum']/df_remaining['Remained']
plusPercentNum3 = df_remaining['plusPercentNum'][0]

# Create data table to show in app
# Generate sum values for Country/Region level
dfCase = country_df.groupby(by='Country/Region', sort=False).sum().reset_index()
dfCase = dfCase.sort_values(
    by=['Confirmed'], ascending=False).reset_index(drop=True)
# As lat and lon also underwent sum(), which is not desired, remove from this table.
dfCase = dfCase.drop(columns=['Latitude', 'Longitude'])

# Grep lat and lon by the first instance to represent its Country/Region
dfGPS = country_df.groupby(
    by='Country/Region', sort=False).first().reset_index()
dfGPS = dfGPS[['Country/Region', 'Latitude', 'Longitude']]

# Merge two dataframes
dfSum = pd.merge(dfCase, dfGPS, how='inner', on='Country/Region')
dfSum = dfSum.replace({'Country/Region': 'China'}, 'Mainland China')
dfSum['Active'] = dfSum['Confirmed'] - dfSum['Recovered'] - dfSum['Deaths']
dfSum['Death rate'] = dfSum['Deaths']/dfSum['Confirmed']
# Rearrange columns to correspond to the number plate order
dfSum = dfSum[['Country/Region', 'Active',
    'Confirmed', 'Recovered', 'Deaths', 'Death rate', 'Latitude', 'Longitude']]
# Sort value based on Active cases and then Confirmed cases
dfSum = dfSum.sort_values(
    by=['Active', 'Confirmed'], ascending=False).reset_index(drop=True)
# Set row ids pass to selected_row_ids
dfSum['id'] = dfSum['Country/Region']
dfSum.set_index('id', inplace=True, drop=False)

# Create tables for tabs
CNTable = make_country_table('China')
AUSTable = make_country_table('Australia')
USTable = make_country_table('United States of America')
CANTable = make_country_table('Canada')

europe_list = ['Austria', 'Belgium', 'Czechia', 'Denmark', 'Estonia',
                  'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Iceland',
                  'Italy', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg',
                  'Malta', 'Netherlands', 'Norway', 'Poland', 'Portugal', 'Slovakia',
                  'Slovenia', 'Spain', 'Sweden', 'Switzerland']
EuroTable = make_europe_table(europe_list)

# Remove dummy row of recovered case number in USTable
USTable = USTable.dropna(subset=['Province/State'])

# Remove dummy row of recovered case number in USTable
CANTable = CANTable.dropna(subset=['Province/State'])

# Save numbers into variables to use in the app
latestDate_1 = datetime.strptime(df_confirmed['date_file'][0],'%m/%d/%Y') 
latestDate = datetime.strftime(latestDate_1, '%b %d, %Y %H:%M AEDT')

secondLastDate_1 = datetime.strptime(df_confirmed['date_file'][1],'%m/%d/%Y') 
secondLastDate = datetime.strftime(secondLastDate_1, '%b %d')

daysOutbreak = (latestDate_1 - datetime.strptime('12/31/2019', '%m/%d/%Y')).days

# Read cumulative data of a given region from ./cumulative_data folder
#dfs_curve = pd.read_csv('./lineplot_data/dfs_curve.csv')

# Pseduo data for logplot
pseduoDay = np.arange(1, daysOutbreak+1)
y1 = 100*(1.85)**(pseduoDay-1)  # 85% growth rate
y2 = 100*(1.35)**(pseduoDay-1)  # 35% growth rate
y3 = 100*(1.15)**(pseduoDay-1)  # 15% growth rate
y4 = 100*(1.05)**(pseduoDay-1)  # 5% growth rate

dict_countries = create_dict_list_of_countries()
dict_data_types = [{'value': "Confirmed", 'label': "Confirmed"},
                    {'value': "Deaths", 'label': "Deaths"},
                    {'value': "Recovered", 'label': "Recovered"}]

app.config['suppress_callback_exceptions'] = True

app.layout = html.Div(style={'backgroundColor': '#151515'},
    children=[
        html.Div(id="number-plate",
            style={'marginLeft': '1.5%','marginRight': '1.5%', 'marginBottom': '.5%'},
                 children=[
                     html.Div(
                         style={'width': '24.4%', 'backgroundColor': '#f9f5f5', 'display': 'inline-block','marginRight': '.8%', 'verticalAlign': 'middle'},
                              children=[
                                  html.H3(style={'textAlign': 'center',
                                                 'fontWeight': 'bold', 'color': '#151515'},
                                               children=[
                                                   html.P(style={'color': '#151515', 'padding': '.5rem'},
                                                   children = "Days Since Outbreak"),
                                                   '{}'.format(daysOutbreak),
                                               ]),
                                  html.H5(style={'textAlign': 'center', 'color': '#151515', 'padding': '.1rem'},
                                               children="Days")
                                       ]),
                     html.Div(
                         style={'width': '24.4%', 'backgroundColor': '#f9f5f5', 'display': 'inline-block',
                                'marginRight': '.8%', 'verticalAlign': 'top'},
                              children=[
                                  html.H3(style={'textAlign': 'center',
                                                 'fontWeight': 'bold', 'color': '#151515'},
                                                children=[
                                                    html.P(style={'padding': '.5rem'},
                                                              children='Confirmed Cases'),
                                                    '{:,d}'.format(
                                                        int(confirmedCases))
                                                         ]),
                                  html.H5(style={'textAlign': 'center', 'color': '#151515', 'padding': '.1rem'},
                                               children="People")
                                       ]),
                     html.Div(
                         style={'width': '24.4%', 'backgroundColor': '#f9f5f5', 'display': 'inline-block',
                                'marginRight': '.8%', 'verticalAlign': 'top'},
                              children=[
                                  html.H3(style={'textAlign': 'center',
                                                       'fontWeight': 'bold', 'color': '#151515'},
                                               children=[
                                                   html.P(style={'padding': '.5rem'},
                                                              children='Recovered Cases'),
                                                   '{:,d}'.format(
                                                       int(recoveredCases)),
                                               ]),
                                  html.H5(style={'textAlign': 'center', 'color': '#151515', 'padding': '.1rem'},
                                               children="People")
                                       ]),
                     html.Div(
                         style={'width': '24.4%', 'backgroundColor': '#f9f5f5', 'display': 'inline-block',
                                'verticalAlign': 'top'},
                              children=[
                                  html.H3(style={'textAlign': 'center',
                                                       'fontWeight': 'bold', 'color': '#151515'},
                                                children=[
                                                    html.P(style={'padding': '.5rem'},
                                                              children='Death Cases'),
                                                    '{:,d}'.format(int(deathsCases))
                                                ]),
                                  html.H5(style={'textAlign': 'center', 'color': '#151515', 'padding': '.1rem'},
                                               children="People")
                                       ])
                          ]),

        html.Div(id='dcc-map', style={'marginLeft': '1.5%', 'marginRight': '1.5%', 'marginBottom': '.5%'},
                 children=[
                     html.Div(style={'width': '100%', 'marginRight': '.8%', 'display': 'inline-block', 'verticalAlign': 'top'},
                              children=[
                                  dcc.Graph(
                                      id='datatable-interact-map',
                                      style={'height': '800px'},),
                                #   dcc.Tabs(
                                #       id="tabs-plots", 
                                #       value='Cumulative Cases',
                                #       parent_className='custom-tabs',
                                #       className='custom-tabs-container', 
                                #       children=[dcc.Tab(className='custom-tab',
                                #                         selected_className='custom-tab--selected',
                                #                         label='Cumulative Cases', 
                                #                         value='Cumulative Cases'),
                                #                 dcc.Tab(className='custom-tab',
                                #                         selected_className='custom-tab--selected',
                                #                         label='Confirmed Case Trajectories', 
                                #                         value='Confirmed Case Trajectories'),
                                #       ]
                                #   ),
                                  html.Div(id='tabs-content-plots')])]),

        html.Div(style={'width': '100%', 'display': 'inline-block', 'verticalAlign': 'top'},
                              children=[
                                  dcc.Tabs(
                                      id="tabs-table",
                                      value='The World',
                                      parent_className='custom-tabs',
                                      className='custom-tabs-container',
                                      children=[
                                          dcc.Tab(label='The World',
                                              value='The World',
                                              className='custom-tab',
                                              selected_className='custom-tab--selected',
                                              children=[
                                                  dash_table.DataTable(
                                                      id='datatable-interact-location',
                                                      # Don't show coordinates
                                                      columns=[{"name": i, "id": i, "type": "numeric","format": FormatTemplate.percentage(2)}
                                                               if i == 'Death rate' else {"name": i, "id": i}
                                                               for i in dfSum.columns[0:6]],
                                                      # But still store coordinates in the table for interactivity
                                                      data=dfSum.to_dict(
                                                          "rows"),
                                                      row_selectable="single",
                                                      sort_action="native",
                                                      style_as_list_view=True,
                                                      style_cell={'font_family': 'Arial',
                                                                  'font_size': '1.1rem',
                                                                  'padding': '.1rem',
                                                                  'backgroundColor': '#f4f4f2', },
                                                      fixed_rows={
                                                          'headers': True, 'data': 0},
                                                      style_table={'minHeight': '800px',
                                                                   'height': '800px',
                                                                   'maxHeight': '800px'},
                                                      style_header={'backgroundColor': '#f4f4f2',
                                                                    'fontWeight': 'bold'},
                                                      style_cell_conditional=[{'if': {
                                                                                  'column_id': 'Country/Regions'}, 'width': '26%'},
                                                                              {'if': {
                                                                                  'column_id': 'Active'}, 'width': '14.2%'},
                                                                              {'if': {
                                                                                  'column_id': 'Confirmed'}, 'width': '15.8%'},
                                                                              {'if': {
                                                                                  'column_id': 'Recovered'}, 'width': '15.8%'},
                                                                              {'if': {
                                                                                  'column_id': 'Deaths'}, 'width': '14.2%'},
                                                                              {'if': {
                                                                                  'column_id': 'Death rate'}, 'width': '14%'},
                                                                              {'if': {
                                                                                  'column_id': 'Active'}, 'color':'#e36209'},
                                                                              {'if': {
                                                                                  'column_id': 'Confirmed'}, 'color': '#d7191c'},
                                                                              {'if': {
                                                                                  'column_id': 'Recovered'}, 'color': '#1a9622'},
                                                                              {'if': {
                                                                                  'column_id': 'Deaths'}, 'color': '#6c6c6c'},
                                                                              {'textAlign': 'center'}],
                                                  )
                                          ]),
                                          make_dcc_country_tab(
                                              'Australia', AUSTable),
                                          make_dcc_country_tab(
                                              'Canada', CANTable),
                                          make_dcc_country_tab(
                                               'Europe', EuroTable),
                                          make_dcc_country_tab(
                                              'Mainland China', CNTable),
                                          make_dcc_country_tab(
                                              'United States', USTable),
                                      ]
                                  )
                              ]),
        html.Div(
            id='dcc-drop-countries',
            style={'marginLeft': '1.5%', 'marginRight': '1.5%',
                'marginBottom': '.35%', 'marginTop': '.5%'},
                 children=[
                     html.Div(
                         style={'width': '32.79%', 'display': 'inline-block',
                             'marginRight': '.8%', 'verticalAlign': 'top'},
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#16cde7',
                                                 'color': '#fdf7f7', 'padding': '1rem', 'marginBottom': '0'},
                                               children='Select Countries to compare'),
                                          dcc.Dropdown(id='country-dropdown', options=dict_countries, multi=True, value = ["World","Australia"])]),
                    html.Div(
                         style={'width': '32.79%', 'display': 'inline-block',
                             'marginRight': '.8%', 'verticalAlign': 'top'},
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#16cde7',
                                                 'color': '#fdf7f7', 'padding': '1rem', 'marginBottom': '0'},
                                               children='Select Data type to compare'),
                                          dcc.Dropdown(id='data-types-dropdown', options=dict_data_types, multi=False, value = "Confirmed")])                                         
                                          
                                          ]),
        html.Div(
            id='dcc-plot',
            style={'marginLeft': '1.5%', 'marginRight': '1.5%',
                'marginBottom': '.35%', 'marginTop': '.5%'},
                 children=[
                     html.Div(
                         style={'width': '67%', 'display': 'inline-block',
                             'marginRight': '.8%', 'verticalAlign': 'top'},
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#16cde7',
                                                 'color': '#fdf7f7', 'padding': '1rem', 'marginBottom': '0'},
                                               children='Confirmed Case Timeline'),
                                  dcc.Graph(style={'height': '300px'}, id='country-like-trend')]),
                     html.Div(
                         style={'width': '30%', 'display': 'inline-block',
                             'marginRight': '.8%', 'verticalAlign': 'top'},
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#16cde7',
                                                 'color': '#fdf7f7', 'padding': '1rem', 'marginBottom': '0'},
                                               children='Active/Recovered/Death Case Timeline'),
                                  dcc.Graph(style={'height': '300px'}, id='country-like-world')])                               
                            ]
                )                           
        
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

@app.callback(Output('country-like-world', 'figure'), [Input('country-dropdown', 'value'), Input("data-types-dropdown", "value")])
def update_Australia(selected_dropdown_value_country,selected_dropdown_value_dataType):   

    Countries = selected_dropdown_value_country
    type_data = selected_dropdown_value_dataType

    mapbox_access_token = "pk.eyJ1IjoiY29ydmV4IiwiYSI6ImNrODlvc2VzOTA4eHEzbW94d3RqMW13OWwifQ.4dmKFuWwbs6mtpBRbctJwA"

    data  = country_df.copy()
    data = data.groupby(['Province/State','Country/Region','date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
    data = data.sort_values(by=['date_file'], ascending = False ).reset_index(drop=True)
    data = data[data['date_file'] == data['date_file'][0]]

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
        lat=data['Latitude'],
        lon=data['Longitude'],
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
            font=dict(size=10, color='#fdf7f7'),
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

@app.callback(
    Output('datatable-interact-map', 'figure'),
    [Input('tabs-table', 'value'),
     Input('datatable-interact-location', 'derived_virtual_selected_rows'),
     Input('datatable-interact-location', 'selected_row_ids'),
     Input('datatable-interact-location-Australia', 'derived_virtual_selected_rows'),
     Input('datatable-interact-location-Australia', 'selected_row_ids'),
     Input('datatable-interact-location-Canada', 'derived_virtual_selected_rows'),
     Input('datatable-interact-location-Canada', 'selected_row_ids'),
     Input('datatable-interact-location-Europe', 'derived_virtual_selected_rows'),
     Input('datatable-interact-location-Europe', 'selected_row_ids'),
     Input('datatable-interact-location-Mainland China', 'derived_virtual_selected_rows'),
     Input('datatable-interact-location-Mainland China', 'selected_row_ids'),
     Input('datatable-interact-location-United States', 'derived_virtual_selected_rows'),
     Input('datatable-interact-location-United States', 'selected_row_ids'),
     ]
)
def update_figures(value, derived_virtual_selected_rows, selected_row_ids, 
  Australia_derived_virtual_selected_rows, Australia_selected_row_ids,
  Canada_derived_virtual_selected_rows, Canada_selected_row_ids,
  Europe_derived_virtual_selected_rows, Europe_selected_row_ids,
  CHN_derived_virtual_selected_rows, CHN_selected_row_ids,
  US_derived_virtual_selected_rows, US_selected_row_ids
  ):

    data  = country_df.copy()
    data = data.groupby(['Province/State','Country/Region','date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
    data = data.sort_values(by=['date_file'], ascending = False ).reset_index(drop=True)
    data = data[data['date_file'] == data['date_file'][0]]

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
    

    if value == 'The World':
      if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

      dff = dfSum
      latitude = 14.056159 if len(derived_virtual_selected_rows) == 0 else dff.loc[selected_row_ids[0]].Latitude
      longitude = 6.395626 if len(derived_virtual_selected_rows) == 0 else dff.loc[selected_row_ids[0]].Longitude
      zoom = 1.02 if len(derived_virtual_selected_rows) == 0 else 4

    elif value == 'Australia':
      if Australia_derived_virtual_selected_rows is None:
        Australia_derived_virtual_selected_rows = []

      dff = AUSTable
      latitude = -25.931850 if len(Australia_derived_virtual_selected_rows) == 0 else dff.loc[Australia_selected_row_ids[0]].Latitude
      longitude = 134.024931 if len(Australia_derived_virtual_selected_rows) == 0 else dff.loc[Australia_selected_row_ids[0]].Longitude
      zoom = 3 if len(Australia_derived_virtual_selected_rows) == 0 else 12

    elif value == 'Canada':
      if Canada_derived_virtual_selected_rows is None:
        Canada_derived_virtual_selected_rows = []

      dff = CANTable
      latitude = 55.474012 if len(Canada_derived_virtual_selected_rows) == 0 else dff.loc[Canada_selected_row_ids[0]].Latitude
      longitude = -97.344913 if len(Canada_derived_virtual_selected_rows) == 0 else dff.loc[Canada_selected_row_ids[0]].Longitude
      zoom = 3 if len(Canada_derived_virtual_selected_rows) == 0 else 12

    elif value == 'Mainland China':
      if CHN_derived_virtual_selected_rows is None:
        CHN_derived_virtual_selected_rows = []

      dff = CNTable
      latitude = 33.471197 if len(CHN_derived_virtual_selected_rows) == 0 else dff.loc[CHN_selected_row_ids[0]].Latitude
      longitude = 106.206780 if len(CHN_derived_virtual_selected_rows) == 0 else dff.loc[CHN_selected_row_ids[0]].Longitude
      zoom = 2.5 if len(CHN_derived_virtual_selected_rows) == 0 else 12

    elif value == 'United States':
      if US_derived_virtual_selected_rows is None:
        US_derived_virtual_selected_rows = []

      dff = USTable
      latitude = 40.022092 if len(US_derived_virtual_selected_rows) == 0 else dff.loc[US_selected_row_ids[0]].Latitude
      longitude = -98.828101 if len(US_derived_virtual_selected_rows) == 0 else dff.loc[US_selected_row_ids[0]].Longitude
      zoom = 3 if len(US_derived_virtual_selected_rows) == 0 else 12

    elif value == 'Europe':
      if Europe_derived_virtual_selected_rows is None:
        Europe_derived_virtual_selected_rows = []

      dff = EuroTable
      latitude = 52.405175 if len(Europe_derived_virtual_selected_rows) == 0 else dff.loc[Europe_selected_row_ids[0]].Latitude
      longitude = 11.403996 if len(Europe_derived_virtual_selected_rows) == 0 else dff.loc[Europe_selected_row_ids[0]].Longitude
      zoom = 2.5 if len(Europe_derived_virtual_selected_rows) == 0 else 12


    mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

    # Generate a list for hover text display
    textList = []
    for area, region in zip(data['Province/State'], data['Country/Region']):

        if type(area) is str:
            if region == "Hong Kong" or region == "Macau" or region == "Taiwan":
                textList.append(area)
            else:
                textList.append(area+', '+region)
        else:
            textList.append(region)

    # Generate a list for color gradient display
    colorList = []

    for comfirmed, recovered, deaths in zip(data['Confirmed'], data['Recovered'], data['Deaths']):
        remaining = comfirmed - deaths - recovered
        colorList.append(remaining)

    fig2 = go.Figure(go.Scattermapbox(
        lat=data['Latitude'],
        lon=data['Longitude'],
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
    fig2.update_layout(
        plot_bgcolor='#151920',
        paper_bgcolor='#cbd2d3',
        margin=go.layout.Margin(l=10, r=10, b=10, t=0, pad=40),
        hovermode='closest',
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
            style="satellite",
            # The direction you're facing, measured clockwise as an angle from true north on a compass
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=latitude,
                lon=longitude
            ),
            pitch=0,
            zoom=zoom
        )
    )

    return fig2

if __name__ == '__main__':
    app.run_server(debug=True)
