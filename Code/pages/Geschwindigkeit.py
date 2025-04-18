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
            driver_results = sess.results[['Abbreviation', 'FullName']]
            drivers_abbr = driver_results.loc[driver_results['FullName'].isin(drivers_str), 'Abbreviation'].tolist()

            # Plot-Setup
            rows = 1 if len(drivers_abbr) == 2 else 2
            cols = 2
            fig, axes = plt.subplots(rows, cols, figsize=(16, 8 if rows == 2 else 6), sharex=True, sharey=True)
            fig.suptitle(f'{race_name} {year} – Speed Map Vergleich', fontsize=22)

            colormap = mpl.cm.plasma

            # axes ist 2D bei 2x2, 1D bei 1x2 → flach machen für konsistentes Handling
            axes = axes.flatten() if isinstance(axes, np.ndarray) else [axes]

            for i, abbr in enumerate(drivers_abbr):
                fastest_lap = sess.laps.pick_driver(abbr).pick_fastest()
                telemetry = fastest_lap.telemetry

                x = telemetry['X']
                y = telemetry['Y']
                speed = telemetry['Speed']

                if x.empty or y.empty or speed.empty:
                    st.warning(f"Keine Telemetriedaten für {abbr} verfügbar.")
                    continue

                # Liniensegmente vorbereiten
                points = np.array([x, y]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)

                norm = plt.Normalize(speed.min(), speed.max())
                lc = LineCollection(segments, cmap=colormap, norm=norm, linewidth=4)
                lc.set_array(speed)

                ax = axes[i]
                ax.axis('off')
                ax.set_title(f"{drivers_str[i]} ({abbr})", fontsize=14)
                ax.plot(x, y, color='black', linestyle='-', linewidth=14, zorder=0)
                ax.add_collection(lc)

                # Farbskala
                cb_ax = fig.add_axes([
                    0.05 + (i % 2) * 0.45,
                    0.07 if rows == 1 else (0.05 if i < 2 else 0.01),
                    0.35, 0.015
                ])
                mpl.colorbar.ColorbarBase(cb_ax, cmap=colormap, norm=norm, orientation='horizontal')
                cb_ax.set_title("Speed [km/h]", fontsize=9)


            plt.tight_layout(rect=[0, 0.12, 1, 0.93])
            st.pyplot(fig)
