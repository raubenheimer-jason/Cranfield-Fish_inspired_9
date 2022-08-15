"""
Main objective is to maximise the number of rescued survivors and minimise the mean rescue time.

Number (use percentage) of rescued survivors:
-> just loop over the survivor log and see how many are rescued vs undiscovered/deceased

Mean rescue time:
-> record the time that each survivor is rescued (iteration number, not actual time)

Running time performance:
->

"""


import pickle
from constants.constants import TIMEOUT_ITERATIONS, TOTAL_BLOCKS, NUM_SIMULATIONS, LOG_PATH
from constants.sim_config import SURV_NUMS, UAV_NUMS, REGION_SIZE, GRID_SIZE, SURV_LIFESPAN_RANGE
import os
from datetime import datetime
import pprint


def logging_setup():
    """
    Initial setup for logging

    Returns sim_log_path to be used after simulations for storing data file
    """
    now = datetime.now()  # current date and time
    time_formatted = now.strftime("%Y-%m-%d__%H-%M-%S")
    sim_log_path = f"{LOG_PATH}/{time_formatted}/"
    print(f"sim_log_path: {sim_log_path}")
    make_dir(sim_log_path)
    make_dir(f"{sim_log_path}plts/")  # dir for plots

    return sim_log_path


def make_dir(path):
    """ Open "path" for writing, creating any parent directories as needed.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)


def add_meta_to_log_dict(log_dict):

    log_dict["meta"].update({"surv_arr": list(SURV_NUMS)})
    log_dict["meta"].update({"surv_lifespan": SURV_LIFESPAN_RANGE})
    log_dict["meta"].update({"uav_num_arr": [x[0]*x[1] for x in UAV_NUMS]})
    log_dict["meta"].update({"uav_nums_tup": UAV_NUMS})
    log_dict["meta"].update({"total_blocks": TOTAL_BLOCKS})
    log_dict["meta"].update({"grid_size": REGION_SIZE})
    log_dict["meta"].update({"region_size": GRID_SIZE})
    log_dict["meta"].update({"timeout_iterations": TIMEOUT_ITERATIONS})
    log_dict["meta"].update({"num_simulations": NUM_SIMULATIONS})


def add_to_log_dict(log_dict,
                    log_f_name,
                    sim_num,
                    surv_log_arr,
                    exp_bl,
                    loop_time_arr,
                    num_surv,
                    num_uav):

    log_dict["simulations"][log_f_name][sim_num].update(
        {"survivors": surv_log_arr})

    log_dict["simulations"][log_f_name][sim_num].update(
        {"explored_blocks": exp_bl})

    log_dict["simulations"][log_f_name][sim_num].update(
        {"loop_time": loop_time_arr})

    log_dict["simulations"][log_f_name][sim_num].update(
        {"num_surv": num_surv})

    log_dict["simulations"][log_f_name][sim_num].update(
        {"num_uav": num_uav})


def store_log_dict_file(log_dict, file_name):

    with open(file_name, 'wb') as f:
        pickle.dump(log_dict, f)
