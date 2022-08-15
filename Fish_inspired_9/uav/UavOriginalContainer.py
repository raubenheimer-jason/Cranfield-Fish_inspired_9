
from uav.uavFishCore import init_uavs
from uav.uavOriginal import UAV_original_fish


class UAV_All_Original:

    def __init__(self,
                 num_swarms,
                 num_uav_per_swarm,
                 uav_pos_arr,
                 uav_modes_arr,
                 uav_states_arr,
                 grid_arr_obj,
                 iter_count,
                 surv_arr,
                 surv_log_arr,
                 explored_block_log_arr):

        self.uavs = []  # main uav container objects
        uavs_init = init_uavs(num_swarms, num_uav_per_swarm)

        self.uav_pos_arr = uav_pos_arr
        # holds the grid for all uavs (shared)
        self.grid_arr_obj = grid_arr_obj
        # holds the modes for all uavs (shared)
        self.uav_modes_arr = uav_modes_arr
        self.uav_states_arr = uav_states_arr

        for i, uav_init in enumerate(uavs_init):
            # Information: [x_pos, y_pos, z_pos, "state"]
            self.uav_pos_arr[i] = uav_init[0:3]
            uav_init_mode = uav_init[3]
            self.uav_modes_arr.append(uav_init_mode)

            # sampler, follower, move, unknown, rescue
            self.uav_states_arr.append(uav_init_mode)

            uav = UavOriginalContainer(iter_count,
                                       i,
                                       uav_init_mode,
                                       self.uav_pos_arr,
                                       self.uav_modes_arr,
                                       self.uav_states_arr,
                                       self.grid_arr_obj,
                                       surv_arr,
                                       surv_log_arr,
                                       explored_block_log_arr)

            self.uavs.append(uav)

    def get_uavs(self):
        return self.uavs


class UavOriginalContainer(UAV_original_fish):
    """ 
    Holds the UAV object for the original simulation...
    """

    def __init__(self,
                 iter_count,
                 i,
                 uav_init_mode,
                 uav_pos_arr,
                 uav_modes_arr,
                 uav_states_arr,
                 grid_arr_obj,  # common grid_arr_obj between all uavs
                 surv_arr,
                 surv_log_arr,
                 explored_block_log_arr):

        self.run_state = [1]  # list so its pass by ref

        self.uav_fish_log_arr = [["time_s",
                                  "data_type",
                                  "uav_num",
                                  "pos_x",
                                  "pos_y",
                                  "pos_z",
                                  "state"]]

        self.uav_fish_ex_bl_arr = [["time_s",
                                    "block_abs_x",
                                    "block_abs_y",
                                    "survivor_in_block"]]

        super().__init__(self.uav_fish_log_arr,
                         self.uav_fish_ex_bl_arr,
                         uav_init_mode,
                         i,
                         iter_count,
                         grid_arr_obj,  # common grid_arr_obj between all uavs
                         uav_pos_arr,
                         surv_arr,
                         uav_modes_arr,
                         uav_states_arr,
                         surv_log_arr,
                         explored_block_log_arr)

    def iterate_uav(self):
        """ called each iteration """

        if self.run_state[0] == 1:  # dispersion state
            # TODO add dispersion algorithm
            self.run_state[0] = 2

        if self.run_state[0] == 2:  # run fish loop algorithm
            # run fish algorithm iteration...
            self.original_fish_alg_loop()
