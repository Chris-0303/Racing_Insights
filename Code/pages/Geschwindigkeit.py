import streamlit as st
import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from utils.helper_functions import load_races, load_data, data_cleaner

import fastf1 as ff1
from fastf1 import plotting

plotting.setup_mpl()

# --- User selections ---
st.title("F1 Speed Map Visualisierung von der schnellsten Runde")

# Jahr auswählen
year = st.selectbox("Wähle eine Saison", [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
                    index=None, placeholder="Saison")

if year: #only continue in code once year has been chosen by user
    #load race calendar for that year
    calendar = load_races(year)

    #ask user to choose race from that year
    race_str = st.selectbox("Wähle ein Rennen", calendar['CustomEventName'], index=None)

    if race_str: #only continue in code once race has been chosen by user
        #convert race string to race number (expecting just one value to be correct, therefore using iloc[0])
        race_nr = calendar.loc[calendar['CustomEventName'] == race_str, 'RoundNumber'].iloc[0]

        #race name for viz
        race_name = calendar.loc[calendar['CustomEventName'] == race_str, 'EventName'].iloc[0]

        # Session laden
        sess = ff1.get_session(year, race_name, 'R')
        sess.load()

        # Fahrer-Auswahl aus tatsächlichen Teilnehmern
        drivers = sorted(sess['CustomDriverName'].tolist())
        driver = st.multiselect("Wähle 2 oder 4 Fahrer zum Vergleich:", options=drivers, default=[])

        if drivers_str: #only continue in code once driver(s) have been chosen by user
            #print warning and stop code execution if not 2 or 4 drivers are selected
            if len(driver) not in (2, 4):
                st.warning(f"Achtung: Wähle 2 oder 4 Fahrer zum Vergleich")
                st.stop()

            #find abbreviations of selected drivers in driver_info
            drivers_abbr = drivers.loc[drivers['CustomDriverName'].isin(driver), 'Abbreviation'].tolist()

            #calc number of rows need in viz based on drivers_amount
            rows = 1 if len(driver) == 2 else 2


        if driver:
            #print warning and stop code execution if not 2 or 4 drivers are selected
            if len(driver) not in (2, 4):
                st.warning(f"Achtung: Wähle 2 oder 4 Fahrer zum Vergleich")
                st.stop()

            #find abbreviations of selected drivers in driver_info
            drivers_abbr = drivers.loc[drivers['CustomDriverName'].isin(driver), 'Abbreviation'].tolist()

            #calc number of rows need in viz based on drivers_amount
            rows = 1 if len(driver) == 2 else 2
            lap = sess.laps.pick_drivers(driver).pick_fastest()

            # Telemetriedaten
            x = lap.telemetry['X']
            y = lap.telemetry['Y']
            color = lap.telemetry['Speed']

            # Linien-Segmente vorbereiten
            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            # Plot erstellen
            fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
            fig.suptitle(f'{race_name} {year} - {driver} - Speed', size=24, y=0.97)

            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
            ax.axis('off')

            # Hintergrund-Track
            ax.plot(x, y, color='black', linestyle='-', linewidth=16, zorder=0)

            # Farbverlauf für Speed
            norm = plt.Normalize(color.min(), color.max())
            colormap = mpl.cm.plasma
            lc = LineCollection(segments, cmap=colormap, norm=norm, linestyle='-', linewidth=5)
            lc.set_array(color)
            ax.add_collection(lc)

            # Farbskala
            cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
            normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
            mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal")

            # Plot anzeigen
            st.pyplot(fig)
