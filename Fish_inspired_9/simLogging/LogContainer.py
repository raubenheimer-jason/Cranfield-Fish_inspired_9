
# from constants.sim_config import PREDICTION
from uav.uavFishCore import UavSelectBlock
from grid.GridContainer import GridContainer
from grid.grid import gridArr
from constants.constants import TOTAL_BLOCKS


class LogContainer:

    def __init__(self,
                 uav_pos_arr,
                 surv_arr,
                 explored_block_log_arr,
                 iter_num,
                 prediction_flag=False):

        self.uav_pos_arr = uav_pos_arr
        self.surv_arr = surv_arr
        self.uav_states_arr = [[] for _ in range(len(uav_pos_arr))]
        self.uav_modes_arr = [[] for _ in range(len(uav_pos_arr))]

        self.iter_num = iter_num

        self.i = -2

        # for implicit, need to have its own grid arr obj
        self.grid_arr_obj = gridArr()
        if prediction_flag:
            # prediction array...
            self.predict_arr = [[] for _ in self.uav_pos_arr]
            # self.pred_fish = UavSelectBlock(self.i,
            #                                 self.uav_modes_arr,
            #                                 self.uav_pos_arr,
            #                                 self.grid_arr_obj)
        else:
            self.predict_arr = [[]]
        self.grid_container = GridContainer(self.uav_pos_arr,
                                            None,  # run_state
                                            self.i,  # i
                                            self.uav_modes_arr,
                                            self.predict_arr,  # for prediction
                                            self.grid_arr_obj,  # for prediction
                                            self.uav_states_arr,
                                            None,  # grid_log_arr
                                            None,  # surv_log_arr
                                            self.surv_arr)

        self.explored_block_log_arr = explored_block_log_arr

    def update_grid_arr(self):

        self.grid_container.call_update_grid_arr(self.grid_arr_obj,
                                                 self.iter_num,
                                                 self.explored_block_log_arr)

        stats_arr = self.grid_arr_obj.get_stats_arr()

        blocks_explored = stats_arr[0]
        # print(f"blocks_explored: {blocks_explored} / {TOTAL_BLOCKS}")

    def get_num_bl_explored(self):
        self.update_grid_arr()
        stats_arr = self.grid_arr_obj.get_stats_arr()
        blocks_explored = stats_arr[0]
        return blocks_explored
