
from statistics import mean


def get_perc_rescued_survivors(survivors_arr, config_info):

    num_surv = int(config_info[1])

    # surv_log_arr: iter_num (rescued), surv_num, x_bl_pos, y_bl_pos, surv_state, surv_lifespan
    # store array of iteration numbers when survivors were rescued
    rescued_surv = [surv[0] for surv in survivors_arr if surv[4] == "rescued"]

    num_rescued = len(rescued_surv)

    if num_surv > 0:
        perc_rescued_survivors = round((num_rescued/num_surv)*100)
    else:
        perc_rescued_survivors = 0  # if no survivors then there are no rescued survivors

    return perc_rescued_survivors


def get_iter_to_rescue_survivor(survivors_arr, config_info):

    # surv_log_arr: iter_num (rescued), surv_num, x_bl_pos, y_bl_pos, surv_state, surv_lifespan
    # store array of iteration numbers when survivors were rescued
    rescued_surv = [surv[0] for surv in survivors_arr if surv[4] == "rescued"]

    num_rescued = len(rescued_surv)
    if num_rescued == 0:
        rescued_surv = [0]

    iter_to_rescue_survivor = round(mean(rescued_surv))

    return iter_to_rescue_survivor


def get_loop_time_us(loop_time_arr, config_info):

    loop_time_us = round(mean(loop_time_arr)/1000)

    return loop_time_us


def get_total_sim_time_ms(loop_time_arr, config_info):

    total_sim_time_ms = round(sum(loop_time_arr)/1000000)

    return total_sim_time_ms


def get_perc_blocks_explored(exp_bl_log_arr, config_info):

    total_blocks = int(config_info[4])

    ex_bl_arr = [n for n in exp_bl_log_arr if n[4] == "explored"]
    num_exp_blocks_tot = len(ex_bl_arr)
    perc_blocks_explored = round((num_exp_blocks_tot/total_blocks)*100)

    return perc_blocks_explored


def get_iters_bet_explored(exp_bl_log_arr, config_info):
    """
    calculate mean iterations between explored blocks for each uav
    """

    num_uav = int(config_info[2]) * int(config_info[3])
    timeout_iterations = int(config_info[5])

    # [iteration_number, uav_num, abs_bl_pos_x, abs_bl_pos_y, state]
    ex_bl_arr = [b[0:2] for b in exp_bl_log_arr if b[4] == "explored"]

    uav_ex_arr = [[] for _ in range(num_uav)]

    for p in ex_bl_arr:
        uav_num = p[1]
        uav_ex_arr[uav_num].append(p[0])

    # uav_ex_arr ->
    # array of arrays, each inner array is a list of iterations for the uav where the block was set to explored

    iters_bet_exp_tot = 0

    for uav_num, ex_iters in enumerate(uav_ex_arr):
        if ex_iters:
            iters_between_explored = [ex_iters[i+1]-ex_iters[i]
                                      for i in range(len(ex_iters)-1)]

            if iters_between_explored:
                mean_iters_bet_exp = round(mean(iters_between_explored))
            else:
                # ? is this right?? what happens if the uav hasnt explored a single block...
                mean_iters_bet_exp = timeout_iterations

        iters_bet_exp_tot += mean_iters_bet_exp

    iters_bet_exp_avg = round(iters_bet_exp_tot/(uav_num+1))

    return iters_bet_exp_avg
