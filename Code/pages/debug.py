import sys
import os

# Add the parent directory of 'utils' to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import fastf1.plotting
import matplotlib.patches as mpatches
from utils.helper_functions import load_races, load_data, data_cleaner

# Load data
year = 2023
race_nr = 5  # use actual race number

#session = load_data(year, race_nr)
#driver_info, laps = data_cleaner(session)

# Pick a sample driver
#drv = session.drivers[0]
#drv_laps = laps.pick_drivers(drv)

dat = load_data(year, race_nr)
driver_info, laps = data_cleaner(dat)

if year: #only continue in code once year has been chosen by user
    #load race calendar for that year
    calendar = load_races(year)

    #ask user to choose race from that year
    race_str = "Austalian Grand Prix - Melbourne - Rennen 1"


    #ask user to choose driver(s), number of drivers to compare and convert to their driver abbreviation
    drivers_str = []

    #ask user to choose y-axis
    y_axis_metric = "TimeBehindLeaderSeconds"


    #calculate laps where it was raining for any driver
    rain_laps = sorted(laps[laps["Raining"]]["LapNumber"].unique())

    #same for saftey car laps
    sc_laps = sorted(laps[laps["TrackStatus"].isin(["4", "6"])]["LapNumber"].unique())

    #Vizualize (inspired by example from fastf1 documentation)
    fig, ax = plt.subplots(figsize=(8, 6))

    if drivers_str:
        drivers_abbr = driver_info.loc[driver_info['CustomDriverName'].isin(drivers_str), 'Abbreviation'].tolist()

        for drv in dat.drivers:
            drv_laps = laps.pick_drivers(drv)
            abb = drv_laps['Driver'].iloc[0]

            if abb in drivers_abbr:
                # Highlight selected
                style = fastf1.plotting.get_driver_style(identifier=abb, style=['color', 'linestyle'], session=dat)
                alpha = 1.0
                lw = 2.0
            else:
                # Fade others
                style = {'color': 'lightgray', 'linestyle': '--'}
                alpha = 0.5
                lw = 1.0

            # Determine y-values
            if y_axis_metric == "TimeBehindLeaderSeconds":
                y_vals = drv_laps["TimeBehindLeaderSeconds"]
            else:
                y_vals = drv_laps["Position"]

            ax.plot(drv_laps['LapNumber'], y_vals, label=abb, **style, alpha=alpha, linewidth=lw)

    else:
        for drv in dat.drivers:
            drv_laps = laps.pick_drivers(drv).copy()

            abb = drv_laps['Driver'].iloc[0]
            style = fastf1.plotting.get_driver_style(identifier=abb, style=['color', 'linestyle'], session=dat)

            # Determine y-values
            if y_axis_metric == "TimeBehindLeaderSeconds":
                y_vals = drv_laps["TimeBehindLeaderSeconds"]
            else:
                y_vals = drv_laps["Position"]

            ax.plot(drv_laps['LapNumber'], y_vals, label=abb, **style)

    #add top overlay axis for rain/SC indicators
    ax_top = ax.inset_axes([0, 1.00, 1, 0.04], sharex=ax)
    ax_top.axis('off')

    # Plot rain and SC boxes
    for lap in rain_laps:
        ax_top.axvspan(lap - 0.5, lap + 0.5, ymin=0.5, ymax=1, color='deepskyblue', alpha=0.7)

    for lap in sc_laps:
        ax_top.axvspan(lap - 0.5, lap + 0.5, ymin=0, ymax=0.5, color='darkorange', alpha=0.7)

    #set ax properties and titles
    fig.suptitle(f"Positionsverlauf, {year} {race_str}", fontsize=16, fontweight='bold', y = 1.03)

    if y_axis_metric == "Position":
        ax.set_ylim([20.5, 0.5])
        ax.set_yticks([1, 5, 10, 15, 20])
        ax.set_ylabel('Position')
    else:
        ax.set_ylim(bottom=-5)
        ax.invert_yaxis()
        ax.set_ylabel('Zeit hinter Führendem (Sekunden)')

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
    plt.show()




