import streamlit as st
import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from utils.helper_functions import load_races, load_data, data_cleaner
import fastf1
from fastf1 import plotting
import matplotlib.gridspec as gridspec
from scipy.interpolate import interp1d
from matplotlib.colors import LinearSegmentedColormap

plotting.setup_mpl()

# Define your custom diverging colormap (e.g., green for one driver, orange for the other)
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_diff", ["green", "white", "#633a34"]
)

# --- User selections ---
st.title("Visualisierung der Geschwindigkeit auf der schnellsten Runde")

# Jahr auswählen
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

        def format_laptime(timedelta_obj):
            total_seconds = timedelta_obj.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            milliseconds = int((total_seconds - int(total_seconds)) * 1000)
            return f"{minutes}:{seconds:02d}.{milliseconds:03d}"

        #ask user to choose driver(s), number of drivers to compare and convert to their driver abbreviation
        driver_options = sorted(driver_info['CustomDriverName'].tolist())
        drivers_str = st.multiselect("Wähle 2 Fahrer zum Vergleich:", options=driver_options, default=[])

        if drivers_str: #only continue in code once driver(s) have been chosen by user
        #print warning and stop code execution if not 2 or 4 drivers are selected
            if len(drivers_str) != 2:
                st.warning(f"Achtung: Wähle 2 Fahrer zum Vergleich")
                st.stop()

            #find abbreviations of selected drivers in driver_info
            drivers = driver_info.loc[driver_info['CustomDriverName'].isin(drivers_str), 'Abbreviation'].tolist()

            # Set up figure and grid layout
            fig = plt.figure(figsize=(10, 14.5))  # Tall layout to allow space for three rows
            gs = fig.add_gridspec(nrows=2, ncols=2, height_ratios=[1, 1.6])

            # Define axes for top two driver plots
            axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
            ax_bottom = fig.add_subplot(gs[1, :])  # Placeholder for third plot (full-width)

            # Collect all speeds for global color normalization
            all_speeds = []

            for driver in drivers:
                lap = dat.laps.pick_drivers(driver).pick_fastest()
                all_speeds.append(lap.telemetry['Speed'])

            # Normalize speeds globally for consistent coloring
            all_speeds_combined = np.concatenate(all_speeds)
            norm = plt.Normalize(all_speeds_combined.min(), all_speeds_combined.max())

            # Plotting top two driver laps
            for i, driver in enumerate(drivers):
                ax = axes[i]
                lap = dat.laps.pick_drivers(driver).pick_fastest()
                x = lap.telemetry['X']
                y = lap.telemetry['Y']
                color = lap.telemetry['Speed']

                points = np.array([x, y]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)

                lc = LineCollection(segments, cmap='plasma', norm=norm, linewidth=7)
                lc.set_array(color)

                ax.plot(x, y, color='black', linestyle='-', linewidth=12, zorder=0)
                ax.add_collection(lc)

                # Driver name for title
                d_name = driver_info.loc[driver_info['Abbreviation'] == driver, 'FullName'].values[0]
                d_team = driver_info.loc[driver_info['Abbreviation'] == driver, 'TeamName'].values[0]
                d_laptime = format_laptime(lap['LapTime'])
                ax.set_title(f'{d_name}, {d_team}\nRundenzeit: {d_laptime}', fontsize=14)
                ax.set_aspect('equal', adjustable='box')
                ax.axis('off')

            # Add a colorbar above the top plots
            cax = fig.add_axes([0.25, 0.915, 0.5, 0.015])  # [left, bottom, width, height]
            sm = mpl.cm.ScalarMappable(norm=norm, cmap='plasma')
            fig.colorbar(sm, cax=cax, orientation='horizontal', label='Geschwindigkeit (km/h)')

            # Add a figure-level title
            fig.suptitle(f'{year} {race_name}\nVergleich der schnellsten Runden zweier Fahrer im Rennen', fontsize=18, y=0.97)

            # Get fastest laps
            lap1 = dat.laps.pick_drivers(drivers[0]).pick_fastest()
            lap2 = dat.laps.pick_drivers(drivers[1]).pick_fastest()

            tel1 = lap1.telemetry
            tel2 = lap2.telemetry

            # Create a common reference: distance (we resample based on that)
            num_points = 500
            dist_common = np.linspace(0, min(tel1['Distance'].max(), tel2['Distance'].max()), num_points)

            # Interpolate positions and speed to common distance base
            def interpolate_telemetry(telemetry, dist_common):
                interp_x = interp1d(telemetry['Distance'], telemetry['X'], kind='linear', fill_value="extrapolate")
                interp_y = interp1d(telemetry['Distance'], telemetry['Y'], kind='linear', fill_value="extrapolate")
                interp_speed = interp1d(telemetry['Distance'], telemetry['Speed'], kind='linear', fill_value="extrapolate")
                return interp_x(dist_common), interp_y(dist_common), interp_speed(dist_common)

            x1, y1, speed1 = interpolate_telemetry(tel1, dist_common)
            x2, y2, speed2 = interpolate_telemetry(tel2, dist_common)

            # Average position between both drivers (to draw segments)
            x_avg = (x1 + x2) / 2
            y_avg = (y1 + y2) / 2

            # Speed difference (positive = driver 1 faster, negative = driver 2 faster)
            speed_diff = speed1 - speed2

            # Build segments for line collection
            points = np.array([x_avg, y_avg]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            # Custom colormap: red for driver 2 faster, blue for driver 1 faster
            cmap = mpl.cm.seismic  # Blue to red diverging
            diff_norm = mpl.colors.TwoSlopeNorm(vmin=-20, vcenter=0, vmax=20)  # adjust limits as needed

            lc = LineCollection(segments, cmap=custom_cmap, norm=diff_norm, linewidth=6)
            lc.set_array(speed_diff[:-1])  # one value per segment

            # Plot on ax_bottom
            ax_bottom.add_collection(lc)
            ax_bottom.plot(x_avg, y_avg, color='black', linewidth=12, zorder=0)
            ax_bottom.set_aspect('equal')
            ax_bottom.set_title("Vergleich auf der Runde: Wer war wo schneller? (in km/h)", fontsize=14)
            ax_bottom.axis('off')

            # Colorbar for difference
            cbax_diff = fig.add_axes([0.25, 0.1, 0.5, 0.015])
            cb = mpl.colorbar.ColorbarBase(cbax_diff, cmap=custom_cmap, norm=diff_norm, orientation='horizontal',
                                           label=f"{drivers[1]} schneller        ←        →        {drivers[0]} schneller")


            # Adjust layout to make space for title and colorbar
            plt.tight_layout(rect=[0, 0.12, 1, 0.93])

            # Show the plot
            st.pyplot(fig)