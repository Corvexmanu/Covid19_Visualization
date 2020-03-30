from Data_Processing import *
from Map_Generation import make_dcc_country_tab
from dash.dependencies import Input, Output
import dash
import dash_table
import dash_table.FormatTemplate as FormatTemplate
import dash_core_components as dcc
import dash_html_components as html
import dbm
import plotly.graph_objs as go
import re
import numpy as np
import plotly.express as px
import math
import pandas as pd
from datetime import datetime
from datetime import timedelta  


global country_df, measures_df,geojson_layer
global dict_countries, mapbox_access_token

mapbox_access_token = "pk.eyJ1IjoiY29ydmV4IiwiYSI6ImNrODlvc2VzOTA4eHEzbW94d3RqMW13OWwifQ.4dmKFuWwbs6mtpBRbctJwA"

###########################################################################
    # Execute Data Processing
###########################################################################

#Get initial datasets
country_df = create_data()
measures_data_df = create_measures() 

#Get variables to be used in Visualization
confirmedCases, deathsCases, recoveredCases = Extract_three_main_trends(country_df)
plusPercentNum1, df_confirmed = get_confirmed_dataset(country_df)
plusPercentNum2, df_recovered = get_recovered_dataset(country_df)
plusPercentNum3, df_deaths = get_deaths_dataset(country_df)
plusPercentNum4, df_remaining = get_remaining_dataset(country_df)
dfCase,dfGPS,dfSum = get_df_CGS(country_df)

# Create tables for tabs
CNTable = make_country_table('China',country_df)
AUSTable = make_country_table('Australia',country_df)
USTable = make_country_table('United States of America',country_df)
USTable = USTable.dropna(subset=['Province/State'])
CANTable = make_country_table('Canada',country_df)
CANTable = CANTable.dropna(subset=['Province/State'])
EuroTable = make_europe_table(country_df)

#Get days Outbreak
daysOutbreak = get_daysOutbreak(df_confirmed)

###########################################################################
    # Set Up Dash App 
    # Define HTML structure
###########################################################################

app = dash.Dash(__name__)
server = app.server
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
                                          dcc.Dropdown(id='country-dropdown', options=create_dict_list_of_countries(country_df), multi=True, value = ["World","Australia"])]),
                    html.Div(
                         style={'width': '32.79%', 'display': 'inline-block',
                             'marginRight': '.8%', 'verticalAlign': 'top'},
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#16cde7',
                                                 'color': '#fdf7f7', 'padding': '1rem', 'marginBottom': '0'},
                                               children='Select Data type to compare'),
                                          dcc.Dropdown(id='data-types-dropdown', options=get_dict_data_types(), multi=False, value = "Confirmed")])                                         
                                          
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


###########################################################################
    # Set Up figure methods
###########################################################################

@app.callback(Output('country-like-trend', 'figure'), [Input('country-dropdown', 'value'), Input("data-types-dropdown", "value")])
def update_graph(selected_dropdown_value_country, selected_dropdown_value_dataType):

    #Get initial data required
    length = {}
    for country in selected_dropdown_value_country:
        data_country = filter_country(country_df,country)
        length[country] = len(data_country)     
    Countries = [k for (k,v) in sorted(length.items(), key=lambda x: x[1])]

    # Create Output Figure
    figure = {
            'data' : [go.Scatter(x = np.arange(len(list(filter_country(country_df,country).index))), 
                                y = filter_country(country_df,country)[selected_dropdown_value_dataType], 
                                mode = "markers+lines", 
                                name = country) for country in Countries],
            'layout' : go.Layout(title = "COVID-19 {} Cases".format(selected_dropdown_value_dataType), xaxis = {'title': 'Days'}, yaxis = {'title': 'People'})
        }

    return figure

@app.callback(Output('country-like-world', 'figure'), [Input('country-dropdown', 'value'), Input("data-types-dropdown", "value")])
def update_Australia(selected_dropdown_value_country,selected_dropdown_value_dataType):   

    #Get initial data required  
    data = get_data_coordinates(country_df) 

    # Generate a list for hover text display
    textList = []
    for area, region in zip(data['Province/State'], data['Country/Region']):
        textList.append(area+', '+region)

    # Generate a list for color gradient display
    colorList = []
    for comfirmed, recovered, deaths in zip(data['Confirmed'], data['Recovered'], data['Deaths']):
        remaining = comfirmed - deaths - recovered
        colorList.append(remaining)

    # Create Output Figure
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

    #Get initial data required
    data = get_data_coordinates(country_df) 
    if value == 'The World':
        dff,latitude,longitude,zoom = get_data_world(dfSum,derived_virtual_selected_rows, selected_row_ids)
    elif value == 'Australia':
        dff,latitude,longitude,zoom = get_data_Australia(AUSTable,Australia_derived_virtual_selected_rows, Australia_selected_row_ids)
    elif value == 'Canada':
        dff,latitude,longitude,zoom = get_data_Canada(CANTable,Canada_derived_virtual_selected_rows, Canada_selected_row_ids)
    elif value == 'Mainland China':
        dff,latitude,longitude,zoom = get_data_Mainland_China(CNTable,CHN_derived_virtual_selected_rows, CHN_selected_row_ids)
    elif value == 'United States':
        dff,latitude,longitude,zoom = get_data_United_States(USTable,US_derived_virtual_selected_rows, US_selected_row_ids)
    elif value == 'Europe':
        dff,latitude,longitude,zoom = get_data_Europe(EuroTable,Europe_derived_virtual_selected_rows, Europe_selected_row_ids)

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

    #Create Output Figure 
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
