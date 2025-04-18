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
        weekend = sess.event
        sess.load()

        driver_row = st.selectbox(
            "Wähle einen Fahrer",
            sess.results.itertuples(index=False),
            format_func=lambda row: row.FullName
        )

        if driver_row:
            driver = driver_row.Abbreviation
            lap = sess.laps.pick_drivers(driver).pick_fastest()

            # Get telemetry data
            colormap = mpl.cm.plasma
            x = lap.telemetry['X']              # values for x-axis
            y = lap.telemetry['Y']              # values for y-axis
            color = lap.telemetry['Speed']      # value to base color gradient on


            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            # We create a plot with title and adjust some setting to make it look good.
            fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
            fig.suptitle(f'{weekend.name} {year} - {driver} - Speed', size=24, y=0.97)

            # Adjust margins and turn of axis
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
            ax.axis('off')


            # After this, we plot the data itself.
            # Create background track line
            ax.plot(lap.telemetry['X'], lap.telemetry['Y'],
                    color='black', linestyle='-', linewidth=16, zorder=0)

            # Create a continuous norm to map from data points to colors
            norm = plt.Normalize(color.min(), color.max())
            lc = LineCollection(segments, cmap=colormap, norm=norm,
                                linestyle='-', linewidth=5)

            # Set the values used for colormapping
            lc.set_array(color)

            # Merge all line segments together
            line = ax.add_collection(lc)


            # Finally, we create a color bar as a legend.
            cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
            normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
            legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap,
                                            orientation="horizontal")

            # Show the plot
            st.pyplot(fig)




