import fastf1
import numpy as np
import pandas as pd
import re
from datetime import date

def load_races(year: int):
    """
    Lädt den Rennkalender für ein bestimmtes Jahr und gibt ihn zurück. Für das aktuelle Jahr werden nur Rennen
    berücksichtigt, die bereits stattgefunden haben.
    Parameter: year
    Return: calendar
    """
    calendar = fastf1.get_event_schedule(year, include_testing=False)
    #create custom event name and also remove the doubling of event locations with regex
    calendar['CustomEventName'] = np.where(
        calendar.apply(lambda row: re.search(r'\b' + re.escape(row['Location']) + r'\b', row['EventName'], re.IGNORECASE),
                       axis=1),
        calendar['EventName'] + " - " + "Rennen " + calendar['RoundNumber'].astype(str),
        calendar['EventName'] + " - " + calendar['Location'] + " - " + "Rennen " + calendar['RoundNumber'].astype(str)
    )

    #limit races on calendar if year is 2025
    if year == 2025:
        today = pd.to_datetime(date.today())
        calendar = calendar[calendar['EventDate'] < today]

    return calendar

def load_data(year: int, race_nr: str):
    """
    Lädt die Session des gewünschten Rennens und gibt sie zurück. Dies ist nicht in den data_cleaner integriert, um das
    abrufen weitere Elemente der Session in den Visualisierungen zu ermöglichen.
    Parameter: year, race_nr
    Return: session
    """
    session = fastf1.get_session(year, race_nr, 'R')
    session.load()
    return session

def data_cleaner(session):
    """
    Bereitet die Daten für die Visualisierung auf und gibt dataframes mit den Fahrerinfos sowie den Runden
    des gewünschten Rennens zurück.
    Parameter: session
    Return: driver_info, laps
    """
    #load session results, choose columns to just have driver info
    driver_info = session.results[['DriverNumber', 'Abbreviation', 'FullName', 'TeamName', 'ClassifiedPosition']]
    #change markers for DNF, DSQ and DNS in ClassifiedPosition, customize driver name
    driver_info['ClassifiedPosition'] = driver_info['ClassifiedPosition'].replace({'R': 'DNF', 'E': 'DNF', 'D': 'DSQ',
                                                                                   'F': 'DNS', 'W': 'DNF', 'N': 'DNF'})
    driver_info['CustomDriverName'] = (driver_info['DriverNumber'] + " - " + driver_info['FullName']
                                       + " - " + driver_info['TeamName'])

    laps = session.laps.copy()  # ensures we're not modifying a view

    # Ensure Position is float
    laps['Position'] = laps['Position'].astype(float)

    # Initialize TimeBehindLeader with proper dtype
    laps['TimeBehindLeader'] = pd.NaT

    # Loop to compute TimeBehindLeader
    for lap in laps['LapNumber'].dropna().unique():
        lap_data = laps[laps['LapNumber'] == lap]
        leader_row = lap_data[lap_data['Position'] == 1.0]

        if not leader_row.empty:
            leader_time = leader_row['Time'].iloc[0]
        else:
            leader_time = lap_data['Time'].min()

        for idx in lap_data.index:
            laps.at[idx, 'TimeBehindLeader'] = laps.at[idx, 'Time'] - leader_time

    # Set lap 1 to 0 delta
    laps.loc[laps['LapNumber'] == 1.0, 'TimeBehindLeader'] = pd.Timedelta(0)

    laps['TimeBehindLeader'] = pd.to_timedelta(laps['TimeBehindLeader'])
    laps["TimeBehindLeaderSeconds"] = laps["TimeBehindLeader"].dt.total_seconds()

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

    #needed transformation for correct plotting
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

    #rename missing values in tyre data (seen in 2018 data)
    laps['Compound'] = laps['Compound'].replace('nan', 'NODATA')

    return driver_info, laps
