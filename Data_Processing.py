import re
import datetime as dt
import os
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta  


def create_data():
    directory = r"C:\\repos\COVID-19\csse_covid_19_data\csse_covid_19_daily_reports"
    #directory = r"/mnt/c/repos/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports"
    data = []
    repeated_names = {
        "Mainland China":"China",
        "US": 'United States of America',
        "UK": 'United Kingdom'
    }
    for root,dirs,files in os.walk(directory):    
        for csvfile in files:
            if csvfile.endswith(".csv"):
                path = directory + "\\" + csvfile
                #path = directory + "/" + csvfile
                tempData = pd.read_csv(path)
                change_names = {
                "Province_State":"Province/State",
                "Country_Region": 'Country/Region',
                "Lat": 'Latitude',
                "Long_":"Longitude",
                "Last_Update":"Last Update" }
                tempData.rename(columns=change_names,inplace=True)
                tempData['date_file'] = csvfile.split(".")[0]
                tempData['date_file'] = pd.to_datetime(tempData['date_file'], infer_datetime_format= True)
                tempData['date_file'] = tempData['date_file'].dt.strftime('%m/%d/%Y')
                tempData['Province/State'] = tempData['Province/State'].fillna(tempData['Country/Region'])
                tempData['Country/Region'] = tempData['Country/Region'].map(repeated_names).fillna(tempData['Country/Region'])
                tempData['Confirmed'] = tempData['Confirmed'].fillna(0)
                tempData['Deaths'] = tempData['Deaths'].fillna(0)
                tempData['Recovered'] = tempData['Recovered'].fillna(0)
                tempData['Last Update'] = pd.to_datetime(tempData['Last Update'], infer_datetime_format= True)
                tempData['Last Update'] = tempData['Last Update'].dt.strftime('%m/%d/%Y')
                data.append(tempData)
    return pd.concat(data)


def filter_country(data,Country):
    if Country == 'World':
        data = data.groupby(['Province/State','Country/Region','date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
        data = data.sort_values(by=['date_file'])
        data = data.groupby('date_file', as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
    else:
        data = data[data["Country/Region"] == Country]
        data = data.groupby(['Province/State','Country/Region','date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
        data = data.sort_values(by=['date_file'])
        data = data.groupby(["Country/Region",'date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})

    data.set_index('date_file',inplace=True)
    indexNames = data[ data['Confirmed'] == 0 ].index
    data.drop(indexNames , inplace=True)
    data = data.sort_values(by=['date_file'])  
    data.index = np.arange(1, len(data) + 1)   
    return data

def filter_country_dates(data,Country):
    if Country == 'World':
        data = data.groupby(['Province/State','Country/Region','date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
        data = data.sort_values(by=['date_file'])
        data = data.groupby('date_file', as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})    
    else:
        data = data[data["Country/Region"] == Country]
        data = data.groupby(['Province/State','Country/Region','date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
        data = data.sort_values(by=['date_file'])
        data = data.groupby(["Country/Region",'date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})

    data.set_index('date_file',inplace=True)
    indexNames = data[ data['Confirmed'] == 0 ].index
    data.drop(indexNames , inplace=True)
    data = data.sort_values(by=['date_file'])  
    dates = list(data.index)  
    data.index = np.arange(1, len(data) + 1) 
    return data,dates

def create_measures():
    path = r"C:\\repos\Covid19_Visualization\data\Measures.csv"
    #path = r"/mnt/c/repos/Covid19_Visualization/data/Measures.csv"
    tempData = pd.read_csv(path, encoding = "ISO-8859-1")
    tempData['Date'] = pd.to_datetime(tempData['DATE_IMPLEMENTED'], format= "%d/%m/%Y")
    tempData['Date'] = tempData['Date'].dt.strftime('%m/%d/%Y')
    return tempData
    
def filter_measures(data_measures,Country):
    measures_countries_df = data_measures[data_measures["COUNTRY"] == Country]
    measures_countries_df = measures_countries_df.sort_values(by=['Date'])
    measures_countries_df = measures_countries_df.groupby(['Date','COUNTRY'], as_index=False)['MEASURE'].apply(list).reset_index(name='Measures')
    measures_countries_df = measures_countries_df.sort_values(by=['Date'])
    data = create_data()
    cases_countries_df,dates = filter_country_dates(data,Country)
    measures_countries_mapped = map_date_measures(cases_countries_df,measures_countries_df,dates)  
    return measures_countries_mapped

def map_date_measures(cases_countries_df,measures_countries_df,dates):
    d = {}
    for i,j in enumerate(dates):
        d[j] = int(i+1)
    measures_countries_df['Date'] = measures_countries_df['Date'].map(d)
    measures_countries_df.set_index('Date',inplace=True)
    return measures_countries_df

def get_dict_data_types():
    dict_data_types = [{'value': "Confirmed", 'label': "Confirmed"},
                    {'value': "Deaths", 'label': "Deaths"},
                    {'value': "Recovered", 'label': "Recovered"}]
    return dict_data_types

def make_country_table(countryName, country_df):
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

def make_europe_table(country_df):

    europe_list = ['Austria', 'Belgium', 'Czechia', 'Denmark', 'Estonia',
                  'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Iceland',
                  'Italy', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg',
                  'Malta', 'Netherlands', 'Norway', 'Poland', 'Portugal', 'Slovakia',
                  'Slovenia', 'Spain', 'Sweden', 'Switzerland']

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

def make_Latin_America_table(country_df):

    LatinAmerica_list = ['Brazil', 'Argentina', 'Colombia', 'Peru', 'Chile',
                  'Ecuador', 'Venezuela', 'Bolivia', 'Uruguay', 'Paraguay', 'Guyana',
                  'Mexico', 'Guatemala', 'Cuba', 'Honduras', 'Nicaragua', 'Panama' ]

    LatinAmerica_table = country_df.loc[country_df['Country/Region'].isin(LatinAmerica_list)]

    LatinAmerica_table = LatinAmerica_table.groupby(['Province/State','Country/Region','date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
    LatinAmerica_table = LatinAmerica_table.sort_values(by=['date_file'])
    LatinAmerica_table.drop_duplicates(subset = ['Province/State','Country/Region'], keep = 'last', inplace = True)
    repeated_names = {
        "Mainland China":"China",
        "US": 'United States of America',
        "UK": 'United Kingdom'
    }
    coordinates = pd.read_csv("./data/coordinates.csv")
    coordinates['Country/Region'] = coordinates['Country/Region'].map(repeated_names).fillna(coordinates['Country/Region'])
    coordinates['Province/State'] = coordinates['Province/State'].fillna(coordinates['Country/Region'])
    coordinates = coordinates[coordinates['Country/Region'].isin(LatinAmerica_list)]    
    LatinAmerica_table = pd.merge(LatinAmerica_table,coordinates, on=['Province/State','Country/Region'])

    # Suppress SettingWithCopyWarning
    pd.options.mode.chained_assignment = None
    LatinAmerica_table['Active'] = LatinAmerica_table['Confirmed'] - LatinAmerica_table['Recovered'] - LatinAmerica_table['Deaths']
    LatinAmerica_table['Death rate'] = LatinAmerica_table['Deaths']/LatinAmerica_table['Confirmed']
    LatinAmerica_table = LatinAmerica_table[['Country/Region', 'Active', 'Confirmed', 'Recovered', 'Deaths', 'Death rate', 'Latitude', 'Longitude']]
    LatinAmerica_table = LatinAmerica_table.sort_values(
            by=['Active', 'Confirmed'], ascending=False).reset_index(drop=True)
    # Set row ids pass to selected_row_ids
    LatinAmerica_table['id'] = LatinAmerica_table['Country/Region']
    LatinAmerica_table.set_index('id', inplace=True, drop=False)
    # Turn on SettingWithCopyWarning
    pd.options.mode.chained_assignment = 'warn'
    return LatinAmerica_table

def create_dict_list_of_countries(country_df):
    dictlist = []
    unique_list = list(country_df["Country/Region"].unique())
    unique_list.append("World")
    for product_title in unique_list:
        dictlist.append({'value': product_title, 'label': product_title})

    return dictlist

def Extract_three_main_trends(country_df):

    #Creating data global values
    data_global = country_df.groupby(['Province/State','Country/Region','date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
    data_global = data_global.sort_values(by=['date_file'], ascending = False ).reset_index(drop=True)
    data_global = data_global[data_global['date_file'] == data_global['date_file'][0]]

    # Save numbers into variables to use in the app
    confirmedCases = data_global['Confirmed'].sum()
    deathsCases = data_global['Deaths'].sum()
    recoveredCases = data_global['Recovered'].sum()

    return confirmedCases, deathsCases, recoveredCases

def get_confirmed_dataset(country_df):

    # Construct confirmed cases dataframe for line plot and 24-hour window case difference
    df_confirmed = country_df[['date_file','Confirmed']]
    df_confirmed = df_confirmed.groupby('date_file', as_index=False).agg({'Confirmed': 'sum'})
    df_confirmed = df_confirmed.sort_values(by=['date_file'],ascending = False)
    df_confirmed.reset_index(inplace = True)
    df_confirmed['plusNum'] = df_confirmed['Confirmed'].diff(periods=-1).fillna(0)
    plusConfirmedNum = df_confirmed['plusNum'][0]
    df_confirmed['plusPercentNum'] = df_confirmed['plusNum']/df_confirmed['Confirmed']
    plusPercentNum1 = df_confirmed['plusPercentNum'][0]

    return plusPercentNum1, df_confirmed

def get_recovered_dataset(country_df):

    # Construct recovered cases dataframe for line plot and 24-hour window case difference
    df_recovered = country_df[['date_file','Recovered']]
    df_recovered = df_recovered.groupby('date_file', as_index=False).agg({'Recovered': 'sum'})
    df_recovered = df_recovered.sort_values(by=['date_file'],ascending = False)
    df_recovered.reset_index(inplace = True)
    df_recovered['plusNum'] = df_recovered['Recovered'].diff(periods=-1).fillna(0)
    plusRecoveredNum = df_recovered['plusNum'][0]
    df_recovered['plusPercentNum'] = df_recovered['plusNum']/df_recovered['Recovered']
    plusPercentNum2 = df_recovered['plusPercentNum'][0]

    return plusPercentNum2, df_recovered

def get_deaths_dataset(country_df):

    # Construct death case dataframe for line plot and 24-hour window case difference
    df_deaths = country_df[['date_file','Deaths']]
    df_deaths = df_deaths.groupby('date_file', as_index=False).agg({'Deaths': 'sum'})
    df_deaths = df_deaths.sort_values(by=['date_file'],ascending = False)
    df_deaths.reset_index(inplace = True)
    df_deaths['plusNum'] = df_deaths['Deaths'].diff(periods=-1).fillna(0)
    plusDeathNum = df_deaths['plusNum'][0]
    df_deaths['plusPercentNum'] = df_deaths['plusNum']/df_deaths['Deaths']
    plusPercentNum3 = df_deaths['plusPercentNum'][0]

    return plusPercentNum3, df_deaths

def get_remaining_dataset(country_df):

    # Construct remaining case dataframe for line plot and 24-hour window case difference
    country_df['Remained'] = country_df['Confirmed'] - country_df['Recovered']
    df_remaining = country_df[['date_file','Remained']]
    df_remaining = df_remaining.groupby('date_file', as_index=False).agg({'Remained': 'sum'})
    df_remaining = df_remaining.sort_values(by=['date_file'],ascending = False)
    df_remaining.reset_index(inplace = True)
    df_remaining['plusNum'] = df_remaining['Remained'].diff(periods=-1).fillna(0)
    plusRemainedNum = df_remaining['plusNum'][0]
    df_remaining['plusPercentNum'] = df_remaining['plusNum']/df_remaining['Remained']
    plusPercentNum4 = df_remaining['plusPercentNum'][0]

    return plusPercentNum4, df_remaining

def get_df_CGS(country_df):


    data = country_df.groupby(['Province/State','Country/Region','date_file'], as_index=False).sum().reset_index()
    data = data.sort_values(by=['date_file'], ascending = False ).reset_index(drop=True)
    data = data[data['date_file'] == data['date_file'][0]]  

    # Create data table to show in app
    # Generate sum values for Country/Region level
    dfCase = data.groupby(by='Country/Region', sort=False).sum().reset_index()
    dfCase = dfCase.sort_values(by=['Confirmed'], ascending=False).reset_index(drop=True)

    # As lat and lon also underwent sum(), which is not desired, remove from this table.
    dfCase = dfCase.drop(columns=['Latitude', 'Longitude'])

    # Grep lat and lon by the first instance to represent its Country/Region
    dfGPS = country_df.groupby(by='Country/Region', sort=False).first().reset_index()
    dfGPS = dfGPS[['Country/Region', 'Latitude', 'Longitude']]

    # Merge two dataframes
    dfSum = pd.merge(dfCase, dfGPS, how='inner', on='Country/Region')
    dfSum = dfSum.replace({'Country/Region': 'China'}, 'Mainland China')
    dfSum['Active'] = dfSum['Confirmed'] - dfSum['Recovered'] - dfSum['Deaths']
    dfSum['Death rate'] = dfSum['Deaths']/dfSum['Confirmed']

    # Rearrange columns to correspond to the number plate order
    dfSum = dfSum[['Country/Region', 'Active','Confirmed', 'Recovered', 'Deaths', 'Death rate', 'Latitude', 'Longitude']]

    # Sort value based on Active cases and then Confirmed cases
    dfSum = dfSum.sort_values(by=['Active', 'Confirmed'], ascending=False).reset_index(drop=True)

    # Set row ids pass to selected_row_ids
    dfSum['id'] = dfSum['Country/Region']
    dfSum.set_index('id', inplace=True, drop=False)

    return dfCase,dfGPS,dfSum

def get_daysOutbreak(df_confirmed):

    # Save numbers into variables to use in the app
    latestDate_1 = datetime.strptime(df_confirmed['date_file'][0],'%m/%d/%Y') 
    latestDate = datetime.strftime(latestDate_1, '%b %d, %Y %H:%M AEDT')
    secondLastDate_1 = datetime.strptime(df_confirmed['date_file'][1],'%m/%d/%Y') 
    secondLastDate = datetime.strftime(secondLastDate_1, '%b %d')
    daysOutbreak = (latestDate_1 - datetime.strptime('12/31/2019', '%m/%d/%Y')).days

    return daysOutbreak

def get_data_coordinates(country_df):

    coordinates = pd.read_csv("./data/coordinates.csv")
    state_names = {
        "Mainland China":"China",
        "US": 'United States of America',
        "UK": 'United Kingdom'
    }
    coordinates['Country/Region'] = coordinates['Country/Region'].map(state_names).fillna(coordinates['Country/Region'])
    coordinates['Province/State'] = coordinates['Province/State'].fillna(coordinates['Country/Region'])

    data = country_df.groupby(['Province/State','Country/Region','date_file'], as_index=False).agg({'Confirmed': 'sum', 'Deaths':'sum','Recovered':'sum'})
    data = data.sort_values(by=['date_file'], ascending = False ).reset_index(drop=True)
    data = data[data['date_file'] == data['date_file'][0]]    

    data = pd.merge(data,coordinates, on=['Province/State',"Country/Region"])
    data.dropna(inplace=True) 

    return data

def get_data_world(dfSum,derived_virtual_selected_rows,selected_row_ids):

    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    dff = dfSum
    latitude = 14.056159 if len(derived_virtual_selected_rows) == 0 else dff.loc[selected_row_ids[0]].Latitude
    longitude = 6.395626 if len(derived_virtual_selected_rows) == 0 else dff.loc[selected_row_ids[0]].Longitude
    zoom = 1.02 if len(derived_virtual_selected_rows) == 0 else 4

    return dff,latitude,longitude,zoom

def get_data_Australia(AUSTable,Australia_derived_virtual_selected_rows, Australia_selected_row_ids):

    if Australia_derived_virtual_selected_rows is None:
        Australia_derived_virtual_selected_rows = []
    dff = AUSTable
    latitude = -25.931850 if len(Australia_derived_virtual_selected_rows) == 0 else dff.loc[Australia_selected_row_ids[0]].Latitude
    longitude = 134.024931 if len(Australia_derived_virtual_selected_rows) == 0 else dff.loc[Australia_selected_row_ids[0]].Longitude
    zoom = 3 if len(Australia_derived_virtual_selected_rows) == 0 else 12

    return dff,latitude,longitude,zoom

def get_data_Canada(CANTable,Canada_derived_virtual_selected_rows, Canada_selected_row_ids):
    
    if Canada_derived_virtual_selected_rows is None:
        Canada_derived_virtual_selected_rows = []
    dff = CANTable
    latitude = 55.474012 if len(Canada_derived_virtual_selected_rows) == 0 else dff.loc[Canada_selected_row_ids[0]].Latitude
    longitude = -97.344913 if len(Canada_derived_virtual_selected_rows) == 0 else dff.loc[Canada_selected_row_ids[0]].Longitude
    zoom = 3 if len(Canada_derived_virtual_selected_rows) == 0 else 12

    return dff,latitude,longitude,zoom

def get_data_Mainland_China(CNTable,CHN_derived_virtual_selected_rows, CHN_selected_row_ids):
    
    if CHN_derived_virtual_selected_rows is None:
        CHN_derived_virtual_selected_rows = []
    dff = CNTable
    latitude = 33.471197 if len(CHN_derived_virtual_selected_rows) == 0 else dff.loc[CHN_selected_row_ids[0]].Latitude
    longitude = 106.206780 if len(CHN_derived_virtual_selected_rows) == 0 else dff.loc[CHN_selected_row_ids[0]].Longitude
    zoom = 2.5 if len(CHN_derived_virtual_selected_rows) == 0 else 12

    return dff,latitude,longitude,zoom

def get_data_United_States(USTable,US_derived_virtual_selected_rows, US_selected_row_ids):

    if US_derived_virtual_selected_rows is None:
        US_derived_virtual_selected_rows = []
    dff = USTable
    latitude = 40.022092 if len(US_derived_virtual_selected_rows) == 0 else dff.loc[US_selected_row_ids[0]].Latitude
    longitude = -98.828101 if len(US_derived_virtual_selected_rows) == 0 else dff.loc[US_selected_row_ids[0]].Longitude
    zoom = 3 if len(US_derived_virtual_selected_rows) == 0 else 12

    return dff,latitude,longitude,zoom

def get_data_Europe(EuroTable,Europe_derived_virtual_selected_rows, Europe_selected_row_ids):
    
    if Europe_derived_virtual_selected_rows is None:
        Europe_derived_virtual_selected_rows = []
    dff = EuroTable
    latitude = 52.405175 if len(Europe_derived_virtual_selected_rows) == 0 else dff.loc[Europe_selected_row_ids[0]].Latitude
    longitude = 11.403996 if len(Europe_derived_virtual_selected_rows) == 0 else dff.loc[Europe_selected_row_ids[0]].Longitude
    zoom = 2.5 if len(Europe_derived_virtual_selected_rows) == 0 else 12
    
    return dff,latitude,longitude,zoom

def get_data_LatinAmerica(LatinAmericaTable,LatinAmerica_derived_virtual_selected_rows, LatinAmerica_selected_row_ids):
    
    if LatinAmerica_derived_virtual_selected_rows is None:
        LatinAmerica_derived_virtual_selected_rows = []
    dff = LatinAmericaTable
    latitude = 5.62613 if len(LatinAmerica_derived_virtual_selected_rows) == 0 else dff.loc[LatinAmerica_selected_row_ids[0]].Latitude
    longitude = -77.680689 if len(LatinAmerica_derived_virtual_selected_rows) == 0 else dff.loc[LatinAmerica_selected_row_ids[0]].Longitude
    zoom = 3 if len(LatinAmerica_derived_virtual_selected_rows) == 0 else 12
    
    return dff,latitude,longitude,zoom