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


def generate_multitrend(data,type_data,Countries):
    length = {}
    for country in Countries:
        data_country,dates = filter_country(data,country)
        length[country] = len(data_country)
    
    Countries = [k for (k,v) in sorted(length.items(), key=lambda x: x[1])] 

    for country in Countries:
        data_country,dates = filter_country(data,country)
        data_country = convert_days_from(country,data_country)
        x = np.arange(len(list(data_country.index)))
        plt.plot(x,data_country[type_data], label = country) 
        plt.legend()
        plt.xticks(x, data_country.index, rotation='vertical')
        plt.annotate("Day = {}\n{} = {:.2f}".format(np.amax(x),type_data,data_country[type_data].max()), xy=(np.amax(x), data_country[type_data].max()), xytext=(8, 0), textcoords='offset points')
    
    plt.ylabel(type_data)
    plt.show()

def generate_onetrend(data,country,type_data):
    data_country,dates = filter_country(data,country)
    data_country = convert_days_from(country,data_country)
    x = np.arange(len(list(data_country.index)))
    plt.plot(x,data_country[type_data]) 
    plt.legend()
    plt.xticks(x, data_country.index, rotation='vertical')
    plt.ylabel(type_data)
    plt.show()

def print_data_countries(cases_countries_df):
    print(cases_countries_df)

def print_measurements_countries(cases_countries_df,measures_countries_df,dates):
    measures_countries_mapped = map_date_measures(cases_countries_df,measures_countries_df,dates)
    print(measures_countries_mapped)

def input_data():
    print("1. Multitrend\
            2. One Trend\
            3. Print Dataset\
            4. Print Measures")
    trends = input()

    print("1. Confirmed\
            2. Deaths\
            3. Recovered")
    type_data = input()

    convert = {"1":"Confirmed",
                "2":"Deaths",
                "3":"Recovered"}
    type_data = convert[type_data]

    if trends in ['2','3','4']:
        print("Insert Country Name")
        country = input()
    
    return trends,type_data,country

def execute_logic(dates,trends,type_data,cases_data_df,cases_countries_df,measures_data_df,measures_countries_df):
    if trends == '1':
        print("Insert Number of countries")
        numCountries = input()
        countries = []
        for i in range(int(numCountries)):
            print("Insert country #{}".format(i+1))
            countries.append(input())
        generate_multitrend(cases_data_df,type_data,countries)
    elif trends == '2':
        print("Insert Country Name")
        country = input()
        generate_onetrend(cases_data_df,country,type_data)
    elif trends =='3':
        print_data_countries(cases_countries_df)
    elif trends =='4':
        print_measurements_countries(cases_countries_df,measures_countries_df,dates)        


if __name__ == "__main__":
    trends,type_data,country = input_data()

    cases_data_df = create_data()
    cases_countries_df,dates = filter_country_dates(cases_data_df,country)

    measures_data_df = create_measures()
    measures_countries_df = filter_measures(measures_data_df,country)
    print(measures_countries_df)

    # execute_logic(dates,trends,type_data,cases_data_df,cases_countries_df,measures_data_df,measures_countries_df)