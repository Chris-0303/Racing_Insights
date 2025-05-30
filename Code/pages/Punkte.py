import streamlit as st
import matplotlib.pyplot as plt
import fastf1.plotting
import pandas as pd
from utils.helper_functions import load_races, load_data, data_cleaner

#load agreed on color scheme from package
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False,
                          color_scheme='fastf1')

#fastf1.Cache.enable_cache('./f1_cache')  # Lokaler Cache empfohlen!

st.title("Punkteverlauf in einer Saison")
st.subheader("Filtere Jahr um den Punkteverlauf der Fahrer zu sehen")

#ask user to choose year
year = st.selectbox("Wähle eine Saison zwischen 2018 und 2025", [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
                      index=None, placeholder="Saison")

if year: #only continue in code once year has been chosen by user
    #load race calendar for that year
    calendar = load_races(year)
    calendar_filtered = pd.DataFrame(calendar[["RoundNumber", "EventName"]])

    @st.cache_data(show_spinner=False)
    def load_all_race_results(year, calendar_filtered):
        combined_df = pd.DataFrame()

        for roundnr in calendar_filtered["RoundNumber"]:
            # Get RoundNumber and EventName
            r_nr = calendar_filtered.loc[calendar_filtered["RoundNumber"] == roundnr, "RoundNumber"].values[0]
            event_name = calendar_filtered.loc[calendar_filtered["RoundNumber"] == roundnr, "EventName"].values[0]

            # Load session (no telemetry, no weather)
            session = fastf1.get_session(year, roundnr, 'Race')
            session.load(telemetry=False, weather=False)

            # Select relevant columns
            results = session.results
            results_filter = pd.DataFrame(results[["DriverNumber", "Abbreviation", "FullName", "TeamName", "TeamColor", "CountryCode", "Points"]])
            results_filter["RoundNumber"] = r_nr
            results_filter["EventName"] = event_name

            # Append to combined dataframe
            combined_df = pd.concat([combined_df, results_filter], ignore_index=True)

        return combined_df

    with st.spinner("Daten werden geladen ..."):
        combined_df = load_all_race_results(year, calendar_filtered)

    #cumulative summe der Punkte für jedes Rennen, für die Visualisierung
    combined_df["CumulativePoints"] = combined_df.sort_values("RoundNumber") \
        .groupby("Abbreviation")["Points"] \
        .cumsum()
     
    # Final Points for each Driver
    final_points = combined_df.groupby("Abbreviation")["CumulativePoints"].max()
    sorted_drivers = final_points.sort_values(ascending=False).index.tolist()

    # Mapping von Abbreviation → CustomDriverName
    combined_df["CustomDriverName"] = (
        combined_df["DriverNumber"] + " - " +
        combined_df["FullName"] + " - " +
        combined_df["TeamName"]
    )
    name_map = combined_df.drop_duplicates("Abbreviation").set_index("Abbreviation")["CustomDriverName"].to_dict()

    # Labels in format "44 - Lewis Hamilton - Mercedes" (like in Rundenzeiten.py), sorted by Point
    driver_labels = [name_map[abbr] for abbr in final_points.sort_values(ascending=False).index]
    driver_map = {label: abbr for label, abbr in zip(driver_labels, final_points.sort_values(ascending=False).index)}

    # Multiselect
    highlight_labels = st.multiselect("Beliebige Anzahl an Fahrer zum Hervorheben auswählen:", options=driver_labels, default=[])
    highlight_drivers = [driver_map[label] for label in highlight_labels]

    # Plot-Setup
    fig, ax = plt.subplots(figsize=(12, 6))

    # Driver sorted by points
    for driver in sorted_drivers:
        group = combined_df[combined_df["Abbreviation"] == driver]
        color = "#" + group["TeamColor"].iloc[0]

        # Hihglight Driver when selected
        if not highlight_drivers or driver in highlight_drivers:
            ax.plot(group["RoundNumber"], group["CumulativePoints"], label=driver, color=color, linewidth=2.5)
        else:
            ax.plot(group["RoundNumber"], group["CumulativePoints"], label=driver, color=color, alpha=0.2, linewidth=1.0)

    ax.set_title(f"Total Punkte der Fahrer – Saison {year}")
    ax.set_xlabel("Runde")
    ax.set_ylabel("Total Punkte")
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), title="Fahrer (nach Punkten)")
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)

