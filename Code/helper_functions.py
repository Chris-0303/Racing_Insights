import fastf1
import numpy as np
import re

def load_races(year: int):
    """
    Lädt den Rennkalender für ein bestimmtes Jahr und gibt ihn zurück.
    Parameter: Jahr
    Return: Rennkalender
    """
    calendar = fastf1.get_event_schedule(year, include_testing=False)
    #create custom event name and also remove the doubling of event locations with regex
    calendar['CustomEventName'] = np.where(
        calendar.apply(lambda row: re.search(r'\b' + re.escape(row['Location']) + r'\b', row['EventName'], re.IGNORECASE),
                       axis=1),
        "Race " + calendar['RoundNumber'].astype(str) + " - " + calendar['EventName'],
        "Race " + calendar['RoundNumber'].astype(str) + " - " + calendar['EventName'] + " - " + calendar['Location']
    )

    return calendar

def load_data(year: int, race_nr: str):
    """
    Lädt die Session des gewünschten Rennens und gibt sie zurück. Dies ist nicht in den data_cleaner integriert, um das
    abrufen weitere Elemente der Session in den Visualisierungen zu ermöglichen.
    Parameter: Jahr, Rennnummer
    Return: Session
    """
    session = fastf1.get_session(year, race_nr, 'R')
    session.load()
    return session

def data_cleaner(session):
    """
    Bereitet die Daten für die Visualisierung auf und gibt dataframes mit den Fahrerinfos sowie den Runden
    des gewünschten Rennens zurück.
    Parameter: Session
    Return: driver_info, laps
    """
    #load session results, choose columns to just have driver info, customize driver and return for user selection
    driver_info = session.results[['DriverNumber', 'Abbreviation', 'FullName', 'TeamName']]
    driver_info['CustomDriverName'] = (driver_info['DriverNumber'] + " - " + driver_info['FullName']
                                       + " - " + driver_info['TeamName'])

    #load laps dataset
    laps = session.laps

    #load weather dataset that contains marker raining / not raining once every minute, safe times where it does rain
    weather = session.weather_data
    rain_times = weather.loc[weather["Rainfall"] == True, "Time"].apply(
        lambda td: (td.components.hours, td.components.minutes)
    ).tolist()

    #add rain information to every lap in the laps dataset
    def is_raining(td):
        h = td.components.hours
        m = td.components.minutes
        return (h, m) in rain_times
    laps["Raining"] = laps["Time"].apply(is_raining)

    return driver_info, laps