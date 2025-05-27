import streamlit as st
import matplotlib.pyplot as plt
import fastf1.plotting
import matplotlib.patches as mpatches
from utils.helper_functions import load_races, load_data, data_cleaner

#load agreed on color scheme from package
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False,
                          color_scheme='fastf1')

st.title("TEST:Positionsverlauf im Rennen")
st.subheader("Filtere Jahr/Rennen um den Positionsverlauf zu sehen")

#ask user to choose year
year = st.selectbox("Wähle eine Saison zwischen 2018 und 2025", [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
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

        @st.cache_data(show_spinner=False)
        def get_race_data(year, race_nr):
            dat = load_data(year, race_nr)
            driver_info, laps = data_cleaner(dat)
            return dat, driver_info, laps

        with st.spinner("Daten werden geladen ..."):
            dat, driver_info, laps = get_race_data(year, race_nr)

        # y-axis selection
        y_axis_metric = st.selectbox("Wähle die Y-Achse für den Verlauf", options=["Position", "TimeBehindLeader"])

        #ask user to choose driver(s), number of drivers to compare and convert to their driver abbreviation
        driver_options = sorted(driver_info['CustomDriverName'].tolist())
        drivers_str = st.multiselect("Optional: Wähle 2 bis 4 Fahrer zum Vergleich:", options=driver_options, default=[])

        #calculate laps where it was raining for any driver
        rain_laps = sorted(laps[laps["Raining"]]["LapNumber"].unique())

        #same for saftey car laps
        sc_laps = sorted(laps[laps["TrackStatus"].isin(["4", "6"])]["LapNumber"].unique())

        #Vizualize (inspired by example from fastf1 documentation)
        fig, ax = plt.subplots(figsize=(8, 6))

        if drivers_str and len(drivers_str) not in (2, 3, 4):
            st.warning("Achtung: Wähle 2 bis 4 Fahrer zum Vergleich")
            st.stop()

        # abbreviations of selected drivers, if any
        drivers_abbr = []
        if drivers_str:
            drivers_abbr = driver_info.loc[driver_info['CustomDriverName'].isin(drivers_str), 'Abbreviation'].tolist()


        def get_y_values(drv_laps, y_axis_metric):
            if y_axis_metric == "TimeBehindLeader":
                return drv_laps['TimeBehindLeader'].dt.total_seconds()
            return drv_laps['Position']


        # always plot all drivers
        for drv in dat.drivers:
            drv_laps = laps.pick_drivers(drv)
            abb = drv_laps['Driver'].iloc[0]
            y_vals = get_y_values(drv_laps, y_axis_metric)

            style = fastf1.plotting.get_driver_style(identifier=abb, style=['color', 'linestyle'], session=dat)

            if abb in drivers_abbr:
                alpha = 1.0
                lw = 2.0
            else:
                alpha = 0.5
                lw = 1.0

            ax.plot(drv_laps['LapNumber'], y_vals, label=abb, **style, alpha=alpha, linewidth=lw)

        #add top overlay axis for rain/SC indicators
        ax_top = ax.inset_axes([0, 1.00, 1, 0.04], sharex=ax)
        ax_top.axis('off')

        # Plot rain and SC boxes
        for lap in rain_laps:
            ax_top.axvspan(lap - 0.5, lap + 0.5, ymin=0.5, ymax=1, color='deepskyblue', alpha=0.7)

        for lap in sc_laps:
            ax_top.axvspan(lap - 0.5, lap + 0.5, ymin=0, ymax=0.5, color='darkorange', alpha=0.7)

        #set ax properties and titles
        fig.suptitle(f"Positionsverlauf, {year} {race_name}", fontsize=16, fontweight='bold', y = 1.03)

        if y_axis_metric == "Position":
            ax.set_ylim([20.5, 0.5])
            ax.set_yticks([1, 5, 10, 15, 20])
            ax.set_ylabel('Position')
        else:
            ax.set_ylim(bottom=0)  # ascending from top to bottom (default)
            ax.set_ylabel('Zeit hinter Leader (s)')

        ax.set_xlabel('Runde')
        ax.legend(bbox_to_anchor=(1.0, 1.02))

        #add legend
        rain_patch = mpatches.Patch(color='deepskyblue', label='REGEN')
        sc_patch = mpatches.Patch(color='darkorange', label='SAFETY CAR / VSC')

        context_legend = fig.legend(
            handles=[rain_patch, sc_patch], loc='upper center', bbox_to_anchor=(0.5, 0.98),
            ncol=2, frameon=False, fontsize='medium', title_fontsize='large', columnspacing=1.5
        )
        fig.add_artist(context_legend)

        plt.tight_layout()
        st.pyplot(fig)

