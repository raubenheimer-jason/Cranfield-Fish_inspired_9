
from generalFunctions.generalFunctions import print_i
from grid.grid import gridArr
from grid.GridContainer import GridContainer
from uav.uavImplicit import UAV_implicit_fish
from uav.uavFishCore import init_uavs
# from constants.sim_config import PREDICTION
from uav.uavFishCore import UavSelectBlock


class UAV_All_Implicit:

    def __init__(self,
                 num_swarms,
                 num_uav_per_swarm,
                 uav_pos_arr,
                 iter_count,
                 surv_arr,
                 surv_log_arr,
                 explored_block_log_arr,
                 prediction_flag=False):

        self.uavs = []  # main uav container objects
        uavs_init = init_uavs(num_swarms, num_uav_per_swarm)

        self.uav_pos_arr = uav_pos_arr

        for i, uav_init in enumerate(uavs_init):
            # Information: [x_pos, y_pos, z_pos, "state"]
            self.uav_pos_arr[i] = uav_init[0:3]
            uav_init_state = uav_init[3]

            uav = UavImplicitContainer(iter_count,
                                       i,
                                       uav_init_state,
                                       uav_pos_arr,
                                       surv_arr,
                                       surv_log_arr,
                                       explored_block_log_arr,
                                       prediction_flag)

            self.uavs.append(uav)

    def get_uavs(self):
        return self.uavs


class UavImplicitContainer(UAV_implicit_fish):
    """ 
    Holds all the UAV object for the implicit simulation...
    Holds the grid_arr object
    """

    def __init__(self,
                 iter_count,
                 i,
                 uav_init_state,
                 uav_pos_arr,
                 surv_arr,
                 surv_log_arr,
                 explored_block_log_arr,
                 prediction_flag):

        self.iter_count = iter_count
        self.uav_pos_arr = uav_pos_arr
        self.run_state = [1]  # list so its pass by ref
        # local storage for states of UAVs --> ONLY stores "sampler" or "follower"
        self.all_modes_arr = [[] for _ in self.uav_pos_arr]
        self.grid_arr_obj = gridArr()

        self.prediction_flag = prediction_flag

        if self.prediction_flag:
            # prediction array...
            self.predict_arr = [[] for _ in self.uav_pos_arr]
        else:
            self.predict_arr = [[]]

        self.grid_container = GridContainer(self.uav_pos_arr,
                                            self.run_state,
                                            i,
                                            self.all_modes_arr,
                                            self.predict_arr,  # for the prediction fish
                                            self.grid_arr_obj,  # for prediction
                                            None,  # uav_states_arr for display
                                            None,  # grid_log_arr for display
                                            None,  # surv_log_arr for display
                                            None,  # surv_arr for display
                                            prediction_flag=self.prediction_flag)

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
                         uav_init_state,
                         i,
                         self.iter_count,
                         self.grid_arr_obj,
                         self.uav_pos_arr,
                         surv_arr,
                         self.all_modes_arr,
                         surv_log_arr,
                         explored_block_log_arr,
                         self.predict_arr)

    def iterate_uav(self):
        """ called each iteration """

        self.grid_container.call_update_grid_arr(self.grid_arr_obj,
                                                 self.iter_count,
                                                 None,
                                                 self.prediction_flag)

        if self.run_state[0] == 1:  # dispersion state
            # TODO add dispersion algorithm
            self.run_state[0] = 2

        if self.run_state[0] == 2:  # wait for state height
            # set target z to state height
            self.set_target_mode_height()
            self.move()
            if self.all_uav_states_known():
                self.run_state[0] = 3
                return  # return so the update_grid_arr loop can run before the fish loop algorithm

        if self.run_state[0] == 3:  # run fish loop algorithm
            # run fish algorithm iteration...
            self.implicit_fish_alg_loop()
