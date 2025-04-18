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

        #cache data so it doesnt always re load when choosing drivers (has to be done with a function)
        @st.cache_data(show_spinner=False)
        def get_race_data(year, race_nr):
            dat = load_data(year, race_nr)
            driver_info, laps = data_cleaner(dat)
            return dat, driver_info, laps

        with st.spinner("Daten werden geladen ..."):
            dat, driver_info, laps = get_race_data(year, race_nr)

        #ask user to choose driver(s), number of drivers to compare and convert to their driver abbreviation
        driver_options = sorted(driver_info['CustomDriverName'].tolist())
        drivers_str = st.multiselect("Wähle 2 oder 4 Fahrer zum Vergleich:", options=driver_options, default=[])

        if drivers_str:
            #print warning and stop code execution if not 2 or 4 drivers are selected
            if len(drivers_str) not in (2, 4):
                st.warning("Achtung: Wähle 2 oder 4 Fahrer zum Vergleich")
                st.stop()

            # Fahrer-Abkürzungen laden
            driver_info = sess.results[['Abbreviation', 'FullName']]
            drivers_abbr = driver_info.loc[driver_info['FullName'].isin(drivers_str), 'Abbreviation'].tolist()

            fig, ax = plt.subplots(figsize=(12, 6.75))
            fig.suptitle(f'{race_name} {year} – Speed Map der schnellsten Runden', fontsize=20, y=0.95)
            ax.axis('off')

            vmin, vmax = np.inf, -np.inf  # für gemeinsame Farbskala
            segments_list = []
            speeds_list = []
            styles = {}

            # Schleife über ausgewählte Fahrer
            for drv in drivers_str:
                laps = sess.laps.pick_driver(drv).pick_fastest()
                tel = laps.telemetry['Speed']
                x = laps.telemetry['X']
                y = laps.telemetry['Y']  

                # Track-Segmente
                points = np.array([x, y]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)
                segments_list.append((segments, tel))

                # Farbgrenzen aktualisieren
                vmin = min(vmin, tel.min())
                vmax = max(vmax, tel.max())

                # Stil holen (Farbe pro Fahrer)
                abbr = sess.laps[sess.laps['Driver'] == laps['Driver'].iloc[0]]['Driver'].iloc[0]
                style = plotting.get_driver_style(abbr, session=sess)
                styles[drv] = style

            # Normierung über alle Fahrer
            norm = plt.Normalize(vmin, vmax)
            cmap = mpl.cm.plasma

            # Alle Fahrer visualisieren
            for (segments, speed), drv in zip(segments_list, drivers_str):
                lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=4)
                lc.set_array(speed)
                lc.set_label(drv)
                lc.set_color(styles[drv]['color'])  # Fahrerfarbe
                ax.add_collection(lc)

            # Farbskala
            cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.03])
            mpl.colorbar.ColorbarBase(cbaxes, norm=norm, cmap=cmap, orientation='horizontal')
            cbaxes.set_title("Geschwindigkeit [km/h]")

            ax.legend(title="Fahrer", loc='upper right')

            st.pyplot(fig)
