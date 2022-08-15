
# * https://stackoverflow.com/questions/24943991/change-grid-interval-and-specify-tick-labels-in-matplotlib


from evaluation.get_log_functions import *
import matplotlib.pyplot as plt
from statistics import mean
import pickle
import pprint


SAVE_FIGS = False
SHOW_PLOTS = True

SIM_TYPES = ("original", "implicit")

# key in dict, function that gets metric, log dict key name, show plot bool, plot title
LOG_ARR_METRICS = [["perc_rescued_survivors",
                    get_perc_rescued_survivors,
                    "survivors",  # this is the key that holds the data that the function will use
                    True,
                    "Percentage of Rescued Survivors"],
                   ["iter_to_rescue_survivor",
                    get_iter_to_rescue_survivor,
                    "survivors",
                    True,
                    "Mean Iterations to Rescue"],
                   ["loop_time_us",
                    get_loop_time_us,
                    "loop_time",
                    True,
                    "Iteration Time"],
                   ["total_sim_time_ms",
                    get_total_sim_time_ms,
                    "loop_time",
                    True,
                    "Total Simulation Time"],
                   ["perc_blocks_explored",
                    get_perc_blocks_explored,
                    "explored_blocks",
                    True,
                    "Percentage of Explored Blocks"],
                   ["iters_bet_explored",
                    get_iters_bet_explored,
                    "explored_blocks",
                    True,
                    "Iterations Between Explored Blocks"]]

PLOT_Y_UNITS = ["Percentage",
                "Iterations",
                "us",
                "ms",
                "Percentage",
                "Iterations"]

LOG_DICT_FILE_NAME = "log_dict.pkl"


def get_explored_blocks_arr(explored_block_log_arr, num_uav):
    """ return array of blocks that were explored and the iteration number when they were set to explored state """

    # [iteration_number, uav_num, abs_bl_pos_x, abs_bl_pos_y, state]
    ex_bl_arr = [bl[0:4]
                 for bl in explored_block_log_arr if bl[4] == "explored"]

    uav_ex_arr = [[] for _ in range(num_uav)]

    for p in ex_bl_arr:
        uav_num = p[1]
        uav_ex_arr[uav_num].append(p[0])

    # returns an array of arrays, each inner array is a list of iterations for the uav where the block was set to explored
    return uav_ex_arr


def get_plot_data(data_dict, surv_arr, uav_arr, total_blocks, timeout_iterations):
    """
    # structure of plot_dict
    plot_dict["axis_lims"] = {"LOG_ARR_METRICS": {"max_y": 0, "min_y": 0}}
    plot_dict["plot_arrays"][num_surv]["LOG_ARR_METRICS"] = {"implicit": ["y_vals for each x val (uav num) for this num_surv"],
                                                             "original": ["y_vals for each x val (uav num) for this num_surv"]}
    """

    plot_dict = {"plot_arrays": {},
                 "axis_lims": {}}

    for metric in LOG_ARR_METRICS:
        # axis limits are kept the same for different numbers of survivors to make comparisons easier
        plot_dict["axis_lims"][metric[0]] = {}

    for num_surv in surv_arr:
        plot_dict["plot_arrays"][num_surv] = {}
        for metric in LOG_ARR_METRICS:
            types_dict = {}
            for sim in SIM_TYPES:
                types_dict[sim] = [None for _ in uav_arr]
            plot_dict["plot_arrays"][num_surv][metric[0]] = types_dict

    # max and min for axes, one for each metric
    max_mins = [[float('-inf'), float('inf')]
                for _ in range(len(LOG_ARR_METRICS))]

    # data_dict is only "simulations"
    for sim_config in data_dict:
        config_info = sim_config.split('-')
        # [sim_type, num_surv, num_swarm, num_uav_per_swarm]
        sim_type = config_info[0]
        num_surv = int(config_info[1])
        num_uav = int(config_info[2]) * int(config_info[3])
        config_info.append(total_blocks)
        config_info.append(timeout_iterations)

        # each element is a different metric
        all_im_data = [[] for _ in LOG_ARR_METRICS]

        # loop over each sim in this config and calc mean etc.
        # append values from each sim to array, then will calc mean of each array
        for sim_num in data_dict[sim_config]:
            for i, metric in enumerate(LOG_ARR_METRICS):
                input_data = data_dict[sim_config][sim_num][metric[2]]
                # dont all need num_uav and num_surv...
                m = metric[1](input_data, config_info)
                all_im_data[i].append(m)

        for i, metric in enumerate(LOG_ARR_METRICS):
            mean_calc = mean(all_im_data[i])
            ind = uav_arr.index(num_uav)
            plot_dict["plot_arrays"][num_surv][metric[0]
                                               ][sim_type][ind] = mean_calc
            max_calc = max(all_im_data[i])
            min_calc = min(all_im_data[i])
            # [0] is max, [1] is min
            if max_mins[i][0] < max_calc:
                max_mins[i][0] = max_calc
                plot_dict["axis_lims"][metric[0]]["max_y"] = max_calc

            if max_mins[i][1] > min_calc:
                max_mins[i][1] = min_calc
                plot_dict["axis_lims"][metric[0]]["min_y"] = min_calc

    return plot_dict


def plot_original_vs_implicit(log_dict):
    """
    """

    print("=========== meta ===========")
    for md in log_dict["meta"]:
        print(f"{md}: {log_dict['meta'][md]}")
    print("----------------------------")

    plot_dict = get_plot_data(data_dict=log_dict["simulations"],
                              surv_arr=log_dict["meta"]["surv_arr"],
                              uav_arr=log_dict["meta"]["uav_num_arr"],
                              total_blocks=log_dict["meta"]["total_blocks"],
                              timeout_iterations=log_dict["meta"]["timeout_iterations"])

    surv_arr = log_dict["meta"]["surv_arr"]
    uav_num_arr = log_dict["meta"]["uav_num_arr"]

    # get axis limits
    lims = [[] for _ in range(len(LOG_ARR_METRICS))]
    # x is the same for everything
    x_lim = [0, max(uav_num_arr) + min(uav_num_arr)]
    for i, k in enumerate(LOG_ARR_METRICS):
        max_y = plot_dict["axis_lims"][k[0]]["max_y"]
        min_y = plot_dict["axis_lims"][k[0]]["min_y"]
        ten_per = round(max_y*0.1)
        y_lim = [min_y - ten_per, max_y + ten_per]
        lims[i] = [x_lim, y_lim]

    # 2D array of figures, 1st level is different num of survivors,
    # 2nd is the two plots for each num of surv (mean_resc_iter, perc_resc)
    figs = []

    n_cols = len(surv_arr)

    for i, _ in enumerate(LOG_ARR_METRICS):
        # one fig for each metric
        figs.append(None)

        if LOG_ARR_METRICS[i][3] == False:
            continue

        f = plt.figure(i, figsize=(15, 5), tight_layout=True)

        ax_arr = []

        for c, _ in enumerate(surv_arr):
            # one subplot for each num of survivors
            # https://matplotlib.org/stable/api/figure_api.html#matplotlib.figure.Figure.add_subplot
            ax = f.add_subplot(1, n_cols, c+1)
            ax_arr.append(ax)

        figs[i] = ax_arr

    for a, metric in enumerate(LOG_ARR_METRICS):
        # each metric has its own figure

        if metric[3] == False:
            continue

        for c, num_surv in enumerate(surv_arr):
            # one subplot for each num of survivors
            # https://matplotlib.org/stable/api/figure_api.html#matplotlib.figure.Figure.add_subplot

            s_plt_dict = plot_dict["plot_arrays"][num_surv]

            figs[a][c].set_title(f"{num_surv} Survivors")

            for sim in SIM_TYPES:
                figs[a][c].plot(uav_num_arr,
                                s_plt_dict[metric[0]][sim],
                                marker='.',
                                label=sim.title())  # .title to capatalise first letter

    for k, f in enumerate(figs):

        if f == None:
            continue

        plt.figure(k)
        plt.suptitle(LOG_ARR_METRICS[k][4], fontsize=14)

        for i, num_surv in enumerate(surv_arr):
            f[i].legend()
            f[i].set_xlabel("Number of UAVs")
            if i == 0:
                f[i].set_ylabel(PLOT_Y_UNITS[k])
            f[i].set_xlim(lims[k][0])
            f[i].set_ylim(lims[k][1])
            f[i].set_xticks(uav_num_arr)
            f[i].grid()

        if SAVE_FIGS:
            fig_1_name = f"{sim_log_path}plts/{LOG_ARR_METRICS[k][0]}.png"
            plt.savefig(fig_1_name, bbox_inches='tight')

    if SHOW_PLOTS:
        plt.show()


def get_log_dict(sim_log_path):

    loaded_dict = {}

    with open(sim_log_path + LOG_DICT_FILE_NAME, 'rb') as f:
        loaded_dict = pickle.load(f)

    return loaded_dict


if __name__ == "__main__":

    sim_log_path = "./logs/2022-08-11__14-27-42/"

    log_dict = get_log_dict(sim_log_path)

    plot_original_vs_implicit(log_dict)