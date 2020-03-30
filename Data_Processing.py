import re
import datetime as dt
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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