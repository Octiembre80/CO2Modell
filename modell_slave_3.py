# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 15:16:23 2016

@author: felix
"""

import numpy as np
import pandas as pd
import datetime as dt
import os

path = os.path.dirname(os.path.realpath(__file__))
ZP = 5 #Zertifikatskosten

Emis   = {'Erdgas':0.202,'Steinkohle':0.339,'Braunkohle':0.404,'Minaraloel':0.28, 
          'Import':0.4718}

#year, month, day = 2015, 4, 8
#year, month, day = 2013, 07, 10
#date = dt.datetime(year,month,day, tzinfo = pytz.timezone('Europe/Berlin'))


###############################################################################
'''
Alle Funktionen mit 'Get' Lesenexterne Datein ein. Zumteil werden in diesen
Fuktionen noch weitere Dateispezifische Prozesse vollzogen.
'''
###############################################################################

def get_yearly_active_plants(year):
    '''Die Funktion liest die Matser-Kraftwerksliste der aktiven Kraftwerke ein.
    Dependence: Keine, wird aufgerufen von Verteilung()
    '''    

    Plants = pd.read_csv(path + '/Daten/Kraftwerke/Kranftwerksliste_Master.csv')

    for i in range(0,len(Plants)):
        Plants.at[i ,'Baujahr'] = float(Plants.at[i,'Baujahr'])
        Plants.at[i,'Leistung'] = float(Plants.at[i,'Leistung'])
        if Plants.at[i,'Voraus_Stillegung'] == '--':
            Plants.at[i,'Voraus_Stillegung'] = 2100
        else:
            Plants.at[i,'Voraus_Stillegung'] = float(Plants.at[i,'Voraus_Stillegung'])
            
    

    NewP_I = Plants[(Plants['Betriebstand'] == 'In Bau') | (Plants['Betriebstand'] == 'In Planung') | (Plants['Betriebstand'] == 'in Betrieb')]
    NewP = NewP_I[(NewP_I.Voraus_Stillegung >= year)]
    NewP = NewP[NewP.Baujahr <= int(year)]

    index = np.arange(len(NewP))
    NewP = NewP.set_index(index)
    
    return NewP


def grenzkosten(Plant):
    '''Die Funktion berechnet die Grenzkosten eines Kraftwerks. Die Berechnung
    stütz sich auf den Energieträger und die Größe des jeweiligen Kraftwerkes,
    nur bei Gaskraftweken kommt es zu einer weiteren Unterscheidung
    (GuD:Ja/Nein). Die Funktionen zur Berechnung deWirkungsgrade und der 
    Betriebskosten(Vk) sind der BA-Stöckmann entnommen.\n
    Dependence: Keine, wird aufgerufen von MeritOrder()
    '''
    def gk_func(Et,Ar,LG):
        Emissionen  = {'Erdgas':0.202, 'Steinkohle':0.339, 
                       'Braunkohle':0.404, 'Minaraloel':5}

        if Et == 'Erdgas':
            if Ar == 'GuD':
                Wg = 0.000126*LG+0.47614
            else:
                Wg = 0.0274*np.log(LG)+0.223
            Vk = 0.0000018*LG**2-0.0061*LG + 9.1
            EF = Emissionen['Erdgas']
            Bk = 29
        
        elif Et == 'Steinkohle':
            if LG > 800:
                Wg = 0.0000001768*(LG**2)-0.00010586*LG+0.3715707
            elif LG <=800:
                Wg = 0.00011713*LG+ 0.30629575
            Vk = 0.000002*LG**2-0.009*LG+17
            EF = Emissionen['Steinkohle']
            Bk = 15        

        elif Et == 'Braunkohle':
            Wg = 0.0304*np.log(LG)+0.18
            Vk = 0.000002*LG**2-0.01*LG+19.5
            EF = Emissionen['Braunkohle']
            Bk = 3.8          

        elif Et == 'Kernenergie':
            Wg = 1
            Vk = 0.000002*LG**2-0.01*LG+19.5
            EF = 0
            Bk = 1

        elif Et == 'Mineralölprodukte':
            Wg = 0.35
            Vk = 0.0000018*LG**2-0.0061*LG + 9.1# Wie Erdgas
            EF = Emissionen['Minaraloel']
            Bk = 28
        
        Gk = Bk/Wg + ZP * EF/Wg + Vk
    
        return (Gk,Wg)
    
    Et = Plant['Energietraeger']
    Ar = Plant['Kraftwerksart']
    LG = Plant['Leistung']
    
    GK,Wg = gk_func(Et,Ar,LG)
    
    return (GK,Wg)


def merit_order(year):
    '''Erstellt aus der Kraftwerksliste die Merit-Order und wählt die Kraftweke 
    zum KWK-Betrieb aus die mit Vorrang in das Netz speisen.\n
    Dependence: Get_YearlyActivePlants(), Grenzkosten()
    '''
    NewP = get_yearly_active_plants(year)
    
    col  = list(NewP.columns) + list(['Grenzkosten','Wirkungsgrad'])
    MO_Year = pd.DataFrame(columns = col)
    
    for i in NewP.index:
        Plant = NewP.iloc[i]
        try:
            GK = float("%.2f"%grenzkosten(Plant)[0])
            Wg = float("%.4f"%grenzkosten(Plant)[1])
            GkP = np.append(Plant.values, [GK, Wg])
            d = pd.DataFrame(data = [GkP],columns = col,index = None)
            MO_Year  = MO_Year.append([d])
        except UnboundLocalError:
            pass

    MO_Year = MO_Year.sort_values(by = 'Grenzkosten')
    index = np.arange(len(MO_Year))
    MO_Year = MO_Year.set_index(index)

    return MO_Year
