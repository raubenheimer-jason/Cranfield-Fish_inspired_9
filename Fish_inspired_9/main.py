# Paper reference: https://www.mdpi.com/2072-4292/13/1/27
# python guide reference: https://docs.python-guide.org/
#   code style (pep-8) : https://docs.python-guide.org/writing/style/#pep-8

# pygame: https://www.youtube.com/watch?v=jO6qQDNa2UY&ab_channel=TechWithTim

# 500 iterations sim: Simulations complete. Total time (s): 93762.6

"""

TODO: Prediction for which block other UAVs are going to... so two UAVs dont travel to the same block

TODO: Implement collision avoidance algorithm (from GDP?)

"""

from uav.UavImplicitContainer import UAV_All_Implicit
from uav.UavOriginalContainer import UAV_All_Original
from display3.DisplayContainer import DisplayContainer
from survivors.survivors import init_survivors
import time
from constants.constants import TIMEOUT_ITERATIONS, NUM_SIMULATIONS, SHOW_SIMULATION
from constants.sim_config import SURV_NUMS, UAV_NUMS, LOG_SIM, SIMULATIONS
from evaluation.logging_functions import add_to_log_dict, store_log_dict_file, add_meta_to_log_dict, logging_setup
from simLogging.LogContainer import LogContainer
import pygame
from grid.grid import gridArr
from copy import deepcopy
import pprint


def iterate(uavs_obj, uav_0_time_arr):
    """ Update all UAV objects... """
    uavs = uavs_obj.get_uavs()
    for i, uav in enumerate(uavs):
        if i == 0:
            start_time = time.time_ns()

        uav.iterate_uav()

        if i == 0:
            loop_time_ns = time.time_ns() - start_time
            uav_0_time_arr.append(loop_time_ns)


def mission_timeout(iter_count):
    """ returns true if mission is timed out, false otherwise """
    # if -1 then there is no timeout...
    if TIMEOUT_ITERATIONS == -1:
        return False

    if iter_count[0] >= TIMEOUT_ITERATIONS:
        return True

    return False


def run_loop(run,
             iter_count,
             next,
             uavs_obj,
             disp_obj,
             loop_time_arr,
             uav_0_time_arr,
             log_obj,
             num_surv):
    """ calls function that updates all UAVs, then updates the display.
    Will only loop if SPACE is pressed or play == True
    """
    loop_time_ns = None
    start_time = time.time_ns()

    while run[0] == True:
        s = time.time_ns()

        if next[0] == True or SHOW_SIMULATION == False:

            next[0] = False
            iterate(uavs_obj, uav_0_time_arr)

            iter_count[0] += 1

            # log_obj will be None if original algorithm
            if log_obj:
                log_obj.update_grid_arr()

            if mission_timeout(iter_count):
                run[0] = False

            # time.sleep(0.02)

            loop_time_ns = (time.time_ns()-s)
            loop_time_arr.append(loop_time_ns)

        if SHOW_SIMULATION:
            disp_obj.update_win(run, loop_time_ns, num_surv)

    sim_time_ms = round((time.time_ns() - start_time)/1000000)
    # print(f"sim_time_ms: {sim_time_ms}")


def main(sim_num,
         sim_type,
         log_dict,
         log_f_name,  # key for the log_dict
         all_sim_surv_arr,
         num_surv,
         num_swarms,
         num_uav_per_swarm):

    start_time = time.time()

    if LOG_SIM:
        log_dict["simulations"][log_f_name].update({sim_num: {}})

    total_uav_num = num_swarms*num_uav_per_swarm

    config_info = f"num_surv: {num_surv}, num_swarms: {num_swarms}, num_uav_per_swarm: {num_uav_per_swarm}"
    sim_info = f"({sim_num}/{NUM_SIMULATIONS})"
    print(f"{'='*10} starting {sim_type} simulation {sim_info} -- {config_info} {'='*10}")

    surv_arr = all_sim_surv_arr[sim_num-1]

    quit_flag = False
    iter_count = [0]  # arr so it's passed by value
    run = [True]
    surv_log_arr = [["iteration_number",
                     "survivor_number",
                     "pos_x",
                     "pos_y",
                     "state",
                     "lifespan"]]

    # for recording the time (iterations) between explored blocks (and number of explored blocks)
    explored_block_log_arr = [["iteration_number",
                               "uav_num",
                               "pos_x",  # abs block pos
                               "pos_y",  # abs block pos
                               "state"]]  # assigned, unassigned, explored
    next = [False]
    loop_time_arr = []
    uav_0_time_arr = []
    uav_pos_arr = [[] for _ in range(total_uav_num)]

    if sim_type == "implicit":
        uavs_obj = UAV_All_Implicit(num_swarms,
                                    num_uav_per_swarm,
                                    uav_pos_arr,
                                    iter_count,
                                    surv_arr,
                                    surv_log_arr,
                                    explored_block_log_arr)
        if SHOW_SIMULATION:
            disp_obj = DisplayContainer(quit_flag,
                                        iter_count,
                                        next,
                                        start_time,
                                        uav_pos_arr,
                                        sim_type,  # "original" or "implicit"
                                        None,  # for original, if implicit this is None
                                        None,  # for original, if implicit this is None
                                        None,   # for original, if implicit this is None
                                        surv_arr)

        log_obj = LogContainer(uav_pos_arr,
                               surv_arr,
                               explored_block_log_arr,
                               iter_count)

    elif sim_type == "implicit_prediction":
        uavs_obj = UAV_All_Implicit(num_swarms,
                                    num_uav_per_swarm,
                                    uav_pos_arr,
                                    iter_count,
                                    surv_arr,
                                    surv_log_arr,
                                    explored_block_log_arr,
                                    prediction_flag=True)
        if SHOW_SIMULATION:
            disp_obj = DisplayContainer(quit_flag,
                                        iter_count,
                                        next,
                                        start_time,
                                        uav_pos_arr,
                                        sim_type,  # "original" or "implicit"
                                        None,  # for original, if implicit this is None
                                        None,  # for original, if implicit this is None
                                        None,   # for original, if implicit this is None
                                        surv_arr,
                                        prediction_flag=True)

        log_obj = LogContainer(uav_pos_arr,
                               surv_arr,
                               explored_block_log_arr,
                               iter_count,
                               prediction_flag=True)

    elif sim_type == "original":

        uav_modes_arr = []
        uav_states_arr = []
        grid_arr_obj = gridArr()

        uavs_obj = UAV_All_Original(num_swarms,
                                    num_uav_per_swarm,
                                    uav_pos_arr,
                                    uav_modes_arr,
                                    uav_states_arr,
                                    grid_arr_obj,
                                    iter_count,
                                    surv_arr,
                                    surv_log_arr,
                                    explored_block_log_arr)

        if SHOW_SIMULATION:
            disp_obj = DisplayContainer(quit_flag,
                                        iter_count,
                                        next,
                                        start_time,
                                        uav_pos_arr,
                                        sim_type,  # "original" or "implicit"
                                        uav_modes_arr,  # for original, if implicit this is None
                                        uav_states_arr,  # for original, if implicit this is None
                                        grid_arr_obj,   # for original, if implicit this is None
                                        surv_arr)

        log_obj = None

    else:
        raise ValueError(f"Invalid sim_type: {sim_type}")

    if not SHOW_SIMULATION:
        disp_obj = None

    # this runs the simulation, loops until this sim is complete...
    run_loop(run,
             iter_count,
             next,
             uavs_obj,
             disp_obj,
             loop_time_arr,
             uav_0_time_arr,
             log_obj,
             num_surv)

    if LOG_SIM:
        add_to_log_dict(log_dict,
                        log_f_name,
                        sim_num,
                        surv_log_arr,
                        explored_block_log_arr,
                        loop_time_arr,
                        uav_0_time_arr,
                        num_surv,
                        total_uav_num)


def main_loop_starter(log_dict):
    """ run the simulations for the different configurations (num_surv, num_uav) """

    if LOG_SIM:
        add_meta_to_log_dict(log_dict)

    for num_surv in SURV_NUMS:
        for uav_nums in UAV_NUMS:
            num_swarms = uav_nums[0]
            num_uav_per_swarm = uav_nums[1]

            # generate an array of survivor arrays, one for each simulation
            # will be used by both original and implicit algorithms
            all_sim_surv_arr = []
            for _ in range(NUM_SIMULATIONS):
                # generate survivors (will be same for both simulations)
                # Info -> surv: [x_pos, y_pos, state]
                all_sim_surv_arr.append(init_survivors(num_surv))

            # create log file for each type of simulation
            for sim_type in SIMULATIONS:
                # dont create a log file if the simulation is False
                if SIMULATIONS[sim_type] == False:
                    continue

                # the - are used to split the filename when plotting
                log_f_name = f"{sim_type}-{num_surv}-{num_swarms}-{num_uav_per_swarm}"
                if LOG_SIM:
                    log_dict["simulations"].update({log_f_name: {}})

                all_sim_surv_arr_copy = deepcopy(all_sim_surv_arr)

                for sim_num in range(1, NUM_SIMULATIONS + 1):

                    main(sim_num,
                         sim_type,
                         log_dict,
                         log_f_name,  # key for the log_dict
                         all_sim_surv_arr_copy,
                         num_surv,
                         num_swarms,
                         num_uav_per_swarm)

    return


if __name__ == "__main__":
    start_time = time.time()

    log_dict = {"simulations": {}, "meta": {}}

    if LOG_SIM:
        sim_log_path = logging_setup()

    # MAIN SIMULATION CODE STARTER
    main_loop_starter(log_dict)

    total_time = round(time.time() - start_time, 1)
    print(f"Simulations complete. Total time (s): {total_time}")

    if LOG_SIM:
        log_dict_file_path = sim_log_path + "log_dict.pkl"
        store_log_dict_file(log_dict, log_dict_file_path)

    pygame.quit()
