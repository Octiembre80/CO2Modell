#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 18:29:03 2017

@author: felix
"""

import pandas as pd
import numpy as np
import bs4 as bs
import requests
import datetime as dt
import pytz

tz = pytz.timezone('Europe/Berlin') 
date = tz.localize(dt.datetime.today())

def master_file(date):
    index = index_day(date.year,date.month,date.day,'')
    master_df = pd.DataFrame(index = index,columns = ['day_ahead','actual'])
    load_df = load_crwaler(date)
    gen_df = gen_crwaler(date)
    imexport_df = imex_port_crawler(date)
    
    master_df = pd.concat([load_df,gen_df,imexport_df[['import','export']]],axis = 1)
    
    return master_df

def load_crwaler(date):
    DATE =  dt.datetime.strftime(date,'%d.%m.%Y')
    url = 'https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime='+DATE+'+00:00|CET|DAY&biddingZone.values=CTY|10Y1001A1001A83F!CTY|10Y1001A1001A83F&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)'
    res = requests.get(url)
    if res.ok == False:
        print(res)
    html = res.text
    soup = bs.BeautifulSoup(html,'lxml')
    result = soup.find_all('td' ,{'class': 'first','class':'dv-value-cell',
                                                   'class':'dv-value-cell'})
    crawler_index = index_day(date.year,date.month,date.day,'crawler')
    crawler_df = pd.DataFrame(index = crawler_index,columns = ['load_day_ahead','load_actual'])

    l = 0
    for i in range(0,len(result)):
        c = i%2
        try:
            crawler_df.iat[l,c] = int(result[i].text)
        except ValueError:
            crawler_df.iat[l,c] = np.nan
        if c == 1:
            l += 1
    
    index = index_day(date.year,date.month,date.day,'')
    load_df = pd.DataFrame(index = index,columns = ['load_day_ahead','load_actual'])
    for h in load_df.index:
        for c in load_df.columns:
            load_df.at[h,c] = crawler_df.loc[dt.datetime.strftime(h,'%Y%m%d %H'),c].sum()/4
    
    return load_df

def gen_crwaler(date):
    DATE =  dt.datetime.strftime(date,'%d.%m.%Y')
    url = 'https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&datepicker-day-offset-select-dv-date-from_input=D&dateTime.dateTime=20.02.2017+00:00|CET|DAYTIMERANGE&dateTime.endDateTime='+DATE+'+00:00|CET|DAYTIMERANGE&area.values=CTY|10Y1001A1001A83F!CTY|10Y1001A1001A83F&productionType.values=B01&productionType.values=B02&productionType.values=B03&productionType.values=B04&productionType.values=B05&productionType.values=B06&productionType.values=B07&productionType.values=B08&productionType.values=B09&productionType.values=B10&productionType.values=B11&productionType.values=B12&productionType.values=B13&productionType.values=B14&productionType.values=B20&productionType.values=B15&productionType.values=B16&productionType.values=B17&productionType.values=B18&productionType.values=B19&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)'
    res = requests.get(url)
    html = res.text
    soup = bs.BeautifulSoup(html,'lxml')
    result = soup.find_all('td' ,{'class':'first','class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell',
                                  'class':'dv-value-cell','class':'dv-value-cell'})
    
    columns = ['biomass','biomass_consum','lignite','lignite_consum',
               'deriv_coal','deriv_coal_consum','gas','gas_consum',
               'coal','coal_consum','oil','oil_consum',
               'shell_oil','shell_oil_consum','peat','peat_consum',
               'geotherm','geotherm_consum','pumped_storage','pumped_storage_consum',
               'run_of_river','run_of_river_consum','hydro_reservoir','hydro_reservoir_consum',
               'marine','marine_consum','nuklear','nuklear_consum',
               'other','other_consum','other_ree','other_ee_consum',
               'solar','solar_consum','wast','wast_consum',
               'wind_of_shore','wind_of_shore_consum','wind','wind_consum']
               
    crawler_index = index_day(date.year,date.month,date.day,'crawler')
    crawler_df = pd.DataFrame(index = crawler_index,columns = columns)
    l = 0
    for i in range(0,len(result)):
        c = i%40
        try:
            crawler_df.iat[l,c] = int(result[i].text)
        except ValueError:
            crawler_df.iat[l,c] = np.nan
        if c == 39:
            l += 1
    
    index = index_day(date.year,date.month,date.day,'')
    gen_df = pd.DataFrame(index = index,columns = columns)
    for h in gen_df.index:
        for c in gen_df.columns:
            gen_df.at[h,c] = crawler_df.loc[dt.datetime.strftime(h,'%Y%m%d %H'),c].sum()/4

    return gen_df

def imex_port_crawler(date):
    DATE =  dt.datetime.strftime(date,'%d.%m.%Y')
    imexport_index = index_day(date.year,date.month,date.day,'')
    imexport_df = pd.DataFrame(index =  imexport_index,columns = ['import','export'])
    crossing = ['10YAT-APG------L','10YCZ-CEPS-----N','10Y1001A1001A65H','10YFR-RTE------C', 
                '10YLU-CEGEDEL-NQ','10YNL----------L','10YPL-AREA-----S','10YSE-1--------K',
                '10YCH-SWISSGRIDZ']
    im, ex = [], []
    for cross in crossing:
        url = 'https://transparency.entsoe.eu/transmission-domain/physicalFlow/show?name=&defaultValue=false&viewType=TABLE&areaType=BORDER_CTY&atch=false&dateTime.dateTime='+DATE+'+00:00|CET|DAY&border.values=CTY|10Y1001A1001A83F!CTY_CTY|10Y1001A1001A83F_CTY_CTY|'+cross+'&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)'
        res = requests.get(url)
        html = res.text
        soup = bs.BeautifulSoup(html,'lxml')
        result = soup.find_all('td' ,{'class': 'first','class':'dv-value-cell',
                                                       'class':'dv-value-cell'})
        crawler_index = index_day(date.year,date.month,date.day,'')
        crawler_df = pd.DataFrame(index = crawler_index,columns = ['import_'+cross[3:5],
                                                                   'export_'+cross[3:5]])
        im += ['import_'+cross[3:5]]
        ex += ['export_'+cross[3:5]]
        l = 0
        for i in range(0,len(result)):
            c = i%2
            try:
                crawler_df.iat[l,c] = int(result[i].text)
            except ValueError:
                crawler_df.iat[l,c] = np.nan
            if c == 1:
                l += 1
        
        imexport_df = pd.concat([imexport_df,crawler_df],axis = 1)
    
    imexport_df['import'],imexport_df['export'] = imexport_df[im].sum(axis=1),imexport_df[ex].sum(axis=1)
    
    return imexport_df

    
url = 'https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTA&atch=false&dateTime.dateTime=22.02.2017+00:00|CET|DAY&biddingZone.values=CTY|10Y1001A1001A83F!CTA|10YDE-VE-------2&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)#'
'''
50H 10YDE-VE-------2 https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTA&atch=false&dateTime.dateTime=22.02.2017+00:00|CET|DAY&biddingZone.values=CTY|10Y1001A1001A83F!CTA|10YDE-VE-------2&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)#
Amp 10YDE-RWENET---I https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTA&atch=false&dateTime.dateTime=22.02.2017+00:00|CET|DAY&biddingZone.values=CTY|10Y1001A1001A83F!CTA|10YDE-RWENET---I&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)#
Ten 10YDE-EON------1 https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTA&atch=false&dateTime.dateTime=22.02.2017+00:00|CET|DAY&biddingZone.values=CTY|10Y1001A1001A83F!CTA|10YDE-EON------1&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)#
TBW 10YDE-ENBW-----N https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTA&atch=false&dateTime.dateTime=22.02.2017+00:00|CET|DAY&biddingZone.values=CTY|10Y1001A1001A83F!CTA|10YDE-ENBW-----N&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)#
'''

def index_day(year, month, day, typ):
    startdate = tz.localize(dt.datetime(year, month, day, hour=0, minute= 0))
    Datum  = range(25,32)
    for i in Datum:
        d = tz.localize(dt.datetime(year, 3, i,0,0))
        b = tz.localize(dt.datetime(year, 10, i,0,0))
        if d.weekday() == 6:
            ds = d
        if b.weekday() == 6:
            dh = b
    if startdate < ds:
        enddate = startdate + dt.timedelta(minutes = 59,hours = 23,)
    elif startdate == ds:
        enddate = startdate + dt.timedelta(minutes = 59,hours = 22)    
    elif startdate > ds and startdate < dh:
        startdate = startdate - dt.timedelta(hours = 1)
        enddate = startdate + dt.timedelta(minutes = 59,hours = 23)    
    elif startdate == dh:
        startdate = startdate - dt.timedelta(hours = 1)
        enddate = startdate + dt.timedelta(minutes = 59,hours = 24)
    if startdate > dh:
        enddate = startdate + dt.timedelta(minutes = 59,hours = 23)
    
    if typ == 'crawler':
        index = pd.date_range(startdate, enddate, freq = '15min')
    else:
        index = pd.date_range(startdate, enddate, freq = 'H')
    return (index)