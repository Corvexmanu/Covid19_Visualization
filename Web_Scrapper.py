from bs4 import BeautifulSoup
from requests import get

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math 
import os


# Function for remove comma within numbers
def removeCommas(string): 
    string = string.replace(',','')
    return string 

def Get_Queensland_data():
    headers = ({'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
    worldometers = "https://www.qld.gov.au/health/conditions/health-alerts/coronavirus-covid-19/current-status/current-status-and-contact-tracing-alerts"
    response = get(worldometers, headers=headers)

    html_soup = BeautifulSoup(response.text, 'html.parser')

    table_contents = html_soup.find_all('tbody')
    table_header = html_soup.find_all('thead')

    # Header for the table
    header = []
    for head_title in table_header[0].find_all('th'):
        for head_strong in head_title.find_all('strong'):
            if len(head_strong) > 1:
                header.append(str(head_strong.contents[0]).strip())
            else:
                header.append(str(head_strong.contents[0]).strip())

    # Save value into columns
    HHS = []
    Cases = []

    for row in table_contents[0].find_all('tr'):
        cells = row.find_all('td')

        if len(cells[0].contents) >=1:
            HHS.append(str(cells[0].contents[0]).strip())
        else:
            HHS.append(0)
        
        if len(cells[1].contents) >=1:
            Cases.append(int(str(cells[1].contents[0]).strip()))
        else:
            Cases.append(0)
        
    Queensland_Regions = pd.DataFrame({'Province/Region': HHS,
                            'Confirmed': Cases
                            })  
    Queensland_Regions = Queensland_Regions[:-1]

    return Queensland_Regions

def Get_NewSouthWales_data():
    headers = ({'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
    worldometers_2 = "https://www.health.nsw.gov.au/Infectious/diseases/Pages/covid-19-lga.aspx#unknown"
    response = get(worldometers_2, headers=headers)

    html_soup = BeautifulSoup(response.text, 'html.parser')

    table_contents = html_soup.find_all('tbody')

    # Save value into columns
    Local_Government_Area = []
    Cases_Confirmed = []

    for row_2 in table_contents[0].find_all('tr'):
        cells_2 = row_2.find_all('td')

        if len(cells_2[0].contents) >=1:
            Local_Government_Area.append(str(cells_2[0].contents[0]).strip())
        else:
            Local_Government_Area.append(0)
        
        if len(cells_2[1].contents) >=1:
            Cases_Confirmed.append(int(str(cells_2[1].contents[0]).strip().split('-')[0]))
        else:
            Cases_Confirmed.append(0)


    NewSouthWales_Regions = pd.DataFrame({'Province/Region': Local_Government_Area,
                            'Confirmed': Cases_Confirmed,
                            })

    NewSouthWales_Regions = NewSouthWales_Regions[:-1]

    return NewSouthWales_Regions

