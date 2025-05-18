import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch
import matplotlib.ticker as ticker
import seaborn as sns
import fastf1.plotting
from utils.helper_functions import load_races, load_data, data_cleaner

class HandlerCircle(HandlerPatch):
    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize, trans):
        radius = min(width, height) / 2
        center = [xdescent + width / 2, ydescent + height / 2]
        circle = mpatches.Circle(center, radius)  # 👈 use mpatches.Circle here
        self.update_prop(circle, orig_handle, legend)
        circle.set_transform(trans)
        return [circle]

#load agreed on color scheme from package
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False,
                          color_scheme='fastf1')

st.title("Strategieanalyse nach Fahrer")
st.subheader("Wähle eine Saison, ein Rennen und 2 bis 4 Fahrer und vergleiche deren Rundenzeiten im Rennverlauf")

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

        #ask if pit laps should be excluded or not (default is no)
        hide_pit_laps = st.selectbox("Boxenstop-Rundenzeiten ausblenden?", options=["Ja", "Nein"], index=1)

        if drivers_str: #only continue in code once driver(s) have been chosen by user
            #print warning and stop code execution if not 2 or 4 drivers are selected
            if len(drivers_str) not in (2, 4):
                st.warning(f"Achtung: Wähle 2 oder 4 Fahrer zum Vergleich")
                st.stop()

            #find abbreviations of selected drivers in driver_info
            drivers_abbr = driver_info.loc[driver_info['CustomDriverName'].isin(drivers_str), 'Abbreviation'].tolist()

            #calc number of rows need in viz based on drivers_amount
            rows = 1 if len(drivers_str) == 2 else 2

            #compound color mapping and add gray just in case (missing tyre values seen in 2018 data)
            compound_palette = fastf1.plotting.get_compound_mapping(session=dat)
            compound_palette['NODATA'] = '#808080'

            #create 2x2 subplot layout
            fig, axes = plt.subplots(rows, 2, figsize=(16, 8*rows), sharey=True)
            axes = axes.flatten()

            #loop to plot each driver
            for i, driver in enumerate(drivers_abbr):
                ax = axes[i]
                driver_laps = laps[laps['Driver'] == driver].copy()

                #Finde Boxenstopp-Runden für mögliche Ausblendung
                pit_laps = driver_laps[
                    driver_laps['PitInTime'].notna() | driver_laps['PitOutTime'].notna()
                    ]['LapNumber'].drop_duplicates()

                #Diese exkludieren je nach Inputbox
                if hide_pit_laps == "Ja":
                    driver_laps.loc[driver_laps['LapNumber'].isin(pit_laps), 'LapTimeSeconds'] = np.nan

                sns.scatterplot(data=driver_laps, x="LapNumber", y="LapTimeSeconds", hue="Compound",
                                palette=compound_palette, ax=ax, s=100, linewidth=0, legend=False)

                #Rain Laps Squares
                raining_laps = driver_laps[driver_laps['Raining'] == True]['LapNumber']
                for lap in raining_laps:
                    ax.axvspan(lap - 0.5, lap + 0.5, ymin=0.98, ymax=1.0, color='deepskyblue', alpha=0.7)

                #Safety Car Laps Squares
                sc_laps = driver_laps[driver_laps['TrackStatus'].isin(['4', '6'])]['LapNumber']
                for lap in sc_laps:
                    ax.axvspan(lap - 0.5, lap + 0.5, ymin=0.96, ymax=0.98, color='darkorange', alpha=0.7)

                #Pit Stop Laps highlighted
                pit_laps = driver_laps[driver_laps['PitInTime'].notna()]['LapNumber']
                for lap in pit_laps:
                    ax.axvspan(lap - 0.5, lap + 1.5, color='lightgrey', alpha=0.2, zorder=0)

                #Get Strings vor Viz
                d_name = driver_info.loc[driver_info['Abbreviation'] == driver, 'FullName'].values[0]
                d_team = driver_info.loc[driver_info['Abbreviation'] == driver, 'TeamName'].values[0]
                d_pos = driver_info.loc[driver_info['Abbreviation'] == driver, 'ClassifiedPosition'].values[0]

                #titles and more
                ax.set_title(f"{d_name}, {d_team} (Rang: {d_pos})", fontsize=18)
                ax.set_xlabel("Runde", fontsize=16)

                #y labels are complicated because streamlit doesnt work well with original time formats
                def format_laptime(x, pos):
                    mins = int(x // 60)
                    secs = int(x % 60)
                    return f"{mins}:{secs:02d}"
                ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_laptime))

                if i % 2 == 0:
                    ax.set_ylabel("Rundenzeit (Min.)", fontsize=16)

                ax.set_xlim(left=0)
                ax.tick_params(axis='both', labelsize=14)
                ax.invert_yaxis()
                ax.grid(alpha=0.3)

            #Identify all compounds actually used in the laps data
            used_compounds = laps['Compound'].dropna().unique()

            handles = [
                mpatches.Patch(color=compound_palette[compound], label=compound)
                for compound in used_compounds if compound in compound_palette
            ]

            compound_legend = fig.legend(
                handles, [h.get_label() for h in handles],
                title="Reifentyp", loc='lower center', bbox_to_anchor=(0.3, -0.01),
                ncol=len(handles), frameon=False,
                fontsize='large', title_fontsize='x-large',
                handletextpad=0.8, columnspacing=1.5, handlelength=1.5,
                handler_map={mpatches.Patch: HandlerCircle()}
            )

            #Custom Legend 2 - Context Information
            rain_patch = mpatches.Patch(color='deepskyblue', label='REGEN')
            sc_patch = mpatches.Patch(color='darkorange', label='SAFETY CAR / VSC')
            pit_patch = mpatches.Patch(color='lightgrey', alpha=0.5, label='BOXENSTOPP')

            context_legend = fig.legend(handles=[rain_patch, sc_patch, pit_patch],
                                        title="Kontextinformationen", loc='lower center', bbox_to_anchor=(0.73, -0.01), ncol=3, frameon=False,
                                        fontsize='large', title_fontsize='x-large', columnspacing=1.5)

            fig.add_artist(compound_legend)
            fig.add_artist(context_legend)

            #Title
            fig.suptitle(f"{year} {race_name} – Vergleich der Rundenzeiten nach Fahrer", fontsize=24)

            #Adjusted Layout for Title and Legends
            plt.tight_layout(rect=[0, 0.045, 1, 0.98])
            st.pyplot(fig)