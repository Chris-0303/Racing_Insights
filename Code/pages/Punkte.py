import streamlit as st
import matplotlib.pyplot as plt
import fastf1.plotting
import pandas as pd
from utils.helper_functions import load_races, load_data, data_cleaner

#load agreed on color scheme from package
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False,
                          color_scheme='fastf1')

#fastf1.Cache.enable_cache('./f1_cache')  # Lokaler Cache empfohlen!

st.title("Punkteverlauf über die Season")
st.subheader("Filtere Jahr um den Punkteverlauf der Spieler zu sehen")

#ask user to choose year
year = st.selectbox("Wähle eine Saison", [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
                      index=None, placeholder="Saison")

if year: #only continue in code once year has been chosen by user
    #load race calendar for that year
    with st.spinner("Daten werden geladen ..."):
        calendar = load_races(year)
        calendar_filtered = pd.DataFrame(calendar[["RoundNumber", "EventName"]])

    #new df to save data from each round inot one df
    combined_df = pd.DataFrame()
    for roundnr in calendar_filtered["RoundNumber"]:
                         
        #get RoundNUmber and EvnetName
        r_nr = calendar_filtered.loc[calendar_filtered["RoundNumber"] == roundnr, "RoundNumber"].values[0]
        event_name = calendar_filtered.loc[calendar_filtered["RoundNumber"] == roundnr, "EventName"].values[0]
        
        #infos Text "Daten werden geladen"
        with st.spinner("Daten werden geladen ..."):
            print(f"Lade Runde:{roundnr} - {event_name}")
        
            #load each round for choosen year 
            session = fastf1.get_session(year, roundnr, 'Race')
            session.load(telemetry=False, weather=False)
                    
            #save Results in a DataFrame (only keep needed cols)
            results = session.results
            results_filter = pd.DataFrame(results[["DriverNumber", "Abbreviation", "TeamColor", "CountryCode", "Points"]])

            
            #create new col to have RoundNUmber and EvnetName in DF as well
            results_filter["RoundNumber"] = r_nr
            results_filter["EventName"] = event_name

            # append combined_df with the rounds
            combined_df = pd.concat([combined_df, results_filter], ignore_index=True)


    #cumulative summe der Punkte für jeden Spiele, für die Visualisierung
    combined_df["CumulativePoints"] = combined_df.sort_values("RoundNumber") \
        .groupby("Abbreviation")["Points"] \
        .cumsum()
    

    # Plot-Setup
    fig, ax = plt.subplots(figsize=(12, 6))


    for driver, group in combined_df.groupby("Abbreviation"):
    color = "#" + group["TeamColor"].iloc[0]
    ax.plot(group["RoundNumber"], group["CumulativePoints"], label=driver, color=color)

    ax.set_title(f"Total Punkte der Fahrer – Saison {year}")
    ax.set_xlabel("Runde")
    ax.set_ylabel("Total Punkte")
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.grid(True, linestyle='--', alpha=0.5)    
    st.pyplot(fig)
