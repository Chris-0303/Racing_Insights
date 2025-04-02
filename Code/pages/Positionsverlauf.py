import streamlit as st
import matplotlib.pyplot as plt
import fastf1.plotting
from utils.helper_functions import load_races, load_data, data_cleaner

#load agreed on color scheme from package
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False,
                          color_scheme='fastf1')

st.title("Positionsverlauf im Rennen")
st.subheader("Filtere Jahr/Rennen um den Positionsverlauf zu sehen")

#ask user to choose year
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

        with st.spinner("Daten werden geladen ..."):
            #load data of the chosen race
            dat = load_data(year, race_nr)

            #prepare data for visualization
            driver_info, laps = data_cleaner(dat)

        #Vizualize (inspired by example from fastf1 documentation)
        fig, ax = plt.subplots(figsize=(8, 6))

        for drv in dat.drivers:
            drv_laps = laps.pick_drivers(drv)

            abb = drv_laps['Driver'].iloc[0]
            style = fastf1.plotting.get_driver_style(identifier=abb, style=['color', 'linestyle'], session=dat)
            ax.plot(drv_laps['LapNumber'], drv_laps['Position'], label=abb, **style)

        #set ax properties
        ax.set_ylim([20.5, 0.5])
        ax.set_yticks([1, 5, 10, 15, 20])
        ax.set_xlabel('Lap')
        ax.set_ylabel('Position')

        #add legend
        ax.legend(bbox_to_anchor=(1.0, 1.02))
        plt.tight_layout()
        plt.show()

