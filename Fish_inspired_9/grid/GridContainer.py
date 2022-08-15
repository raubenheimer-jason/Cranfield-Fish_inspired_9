import math
from constants.constants import TOTAL_BLOCKS
# from constants.sim_config import PREDICTION
from convert.convert import abs_block_to_pixel_xy, pix_to_region_block_pos, pix_to_abs_block_position_xy
from generalFunctions.generalFunctions import print_i
from grid.grid import update_grid_arr
from uav.uavFishCore import UavSelectBlock
from prediction.prediction import change_target


class GridContainer:
    """ GridContainer is ONLY used for implicit algorithm... 
        Therefore prediction can happen from here...
    """

    def __init__(self,
                 uav_pos_arr,
                 run_state,
                 i,
                 uav_modes_arr,
                 predict_arr,  # for prediction
                 grid_arr_obj,  # for prediction
                 uav_states_arr,
                 grid_log_arr,
                 surv_log_arr,
                 surv_arr,
                 prediction_flag=False):

        self.uav_pos_arr = uav_pos_arr
        self.run_state = run_state  # list so its pass by reference
        self.i = i
        self.uav_modes_arr = uav_modes_arr
        self.uav_states_arr = uav_states_arr
        self.prev_pos_uav_arr = [[] for _ in self.uav_pos_arr]
        self.all_prev_states_arr = [[] for _ in self.uav_pos_arr]
        # list to remember pos of survivors so 1 survivor = only 1 profit
        self.rescue_pos_arr = []

        if self.run_state == None:
            self.update_block_state_flag = [True]
        else:
            self.update_block_state_flag = [False]

        self.grid_log_arr = grid_log_arr  # for display
        self.surv_log_arr = surv_log_arr  # for display
        self.surv_arr = surv_arr  # for display3

        # array to keep track of the explored blocks so we dont set them a second time
        self.exp_blocks_arr = []

        self.predict_arr = predict_arr
        if prediction_flag:
            self.pred_fish = UavSelectBlock(self.i,
                                            uav_modes_arr,
                                            uav_pos_arr,
                                            grid_arr_obj)

    def call_update_grid_arr(self, grid_arr_obj, iter_num, explored_block_log_arr, prediction_flag=False):

        update_grid_arr(self.run_state,
                        self.grid_log_arr,  # display3
                        self.surv_log_arr,  # display3
                        explored_block_log_arr,  # only for implicit, None otherwise
                        self.surv_arr,  # display3
                        self.i,
                        self.uav_pos_arr,
                        self.uav_states_arr,  # display3
                        self.uav_modes_arr,
                        grid_arr_obj,
                        self.prev_pos_uav_arr,
                        self.all_prev_states_arr,
                        self.rescue_pos_arr,
                        self.update_block_state_flag,
                        iter_num,
                        self.exp_blocks_arr)

        if prediction_flag:
            self.update_pred_arr()

    def update_pred_arr(self):

        for i, (uav_pos, prev_pos, uav_mode) in enumerate(zip(self.uav_pos_arr, self.prev_pos_uav_arr, self.uav_modes_arr)):

            pred_abs_bl = []

            # get current region
            region = pix_to_region_block_pos(uav_pos[0:2])[0]

            if uav_mode == "sampler":
                cur_abs_bl = pix_to_abs_block_position_xy(uav_pos[0:2])
                if not self.pred_fish.grid_arr_obj.any_unassigned_block_in_region(region):
                    region = self.pred_fish.select_nearest_region(cur_abs_bl)
                    if region == []:
                        # no unassigned regions...
                        pass
                        # print("no unassigned regions...")
                    # pred_abs_bl = self.pred_fish.select_nearest_block(cur_abs_bl,
                    #                                                   region)
                # else:
                    # cur_abs_bl_pos = pix_to_abs_block_position_xy(uav_pos[0:2])
                if not region == []:
                    pred_abs_bl = self.pred_fish.select_nearest_block(cur_abs_bl,
                                                                      region)
                else:
                    # no unassigned regions...
                    pass

            elif uav_mode == "follower":
                num = 0
                while num < TOTAL_BLOCKS:
                    num += 1
                    if self.pred_fish.grid_arr_obj.any_unassigned_block_in_region(region):
                        pred_abs_bl = self.pred_fish.select_nearest_block_towards_sampler()
                        # look = False
                        break

                    else:
                        region = self.pred_fish.select_nearest_highly_profitable_region(
                            region)
                        # if not region == False:
                        if region == False:
                            if self.pred_fish.no_unassigned_block_or_mission_timeout():
                                # mission done, return home
                                pred_abs_bl = [-1, -1]
                            else:
                                # will change to sampler...
                                pred_abs_bl = []
                                pass
                            # look = False
                            break
                        else:
                            # repeat loop again
                            pass
                            # if self.pred_fish.grid_arr_obj.any_unassigned_block_in_region(region):
                            #     pred_abs_bl = self.pred_fish.select_nearest_block_towards_sampler()

            # convert abs bl to pix
            if pred_abs_bl:
                pred_pix = abs_block_to_pixel_xy(pred_abs_bl)
            else:
                pred_pix = pred_abs_bl

            # self.predict_arr[i] = pred_pix

            # check if uav is moving away from predicted position
            # prev distance
            if prev_pos and pred_pix and uav_pos:
                # print(prev_pos, pred_pix, uav_pos)
                prev_dist = math.dist(prev_pos[0:2], pred_pix[0:2])
                # current distance
                curr_dist = math.dist(uav_pos[0:2], pred_pix[0:2])
                if prev_dist < curr_dist:
                    # uav is not moving closer... prediction is wrong.
                    self.predict_arr[i] = []
                else:
                    self.predict_arr[i] = pred_pix
            else:
                self.predict_arr[i] = []

        # print("before", self.predict_arr)

        # now check if any targets need to change...
        for i, target in enumerate(self.predict_arr):
            if change_target(i, target, self.predict_arr, self.uav_pos_arr) == True:

                # print("change target")

                # TODO surely a faster way than a loop..
                # get list of blocks that are already targets...
                exc_blocks = []
                for bl in self.predict_arr:
                    if not bl == []:
                        exc_blocks.append(pix_to_abs_block_position_xy(bl))

                new_abs_bl = self.select_new_block_prediction(
                    self.uav_modes_arr[i],
                    self.uav_pos_arr[i],
                    exc_blocks)

                # print(new_abs_bl)

                # only update if we have a prediction
                if new_abs_bl:
                    self.predict_arr[i] = abs_block_to_pixel_xy(new_abs_bl)
                else:
                    self.predict_arr[i] = []

        # print("after", self.predict_arr)

    def select_new_block_prediction(self, mode, uav_pos, exc_bls):

        region = pix_to_region_block_pos(uav_pos[0:2])[0]

        if mode == "sampler":
            num = 0
            while num < TOTAL_BLOCKS:
                num += 1
                if self.pred_fish.grid_arr_obj.any_unassigned_block_in_region(region):
                    cur_abs_bl_pos = pix_to_abs_block_position_xy(uav_pos[0:2])
                    bl_abs_bl_pos = self.pred_fish.select_nearest_block(cur_abs_bl_pos,
                                                                        region,
                                                                        exc_bls)
                    if not bl_abs_bl_pos == False:
                        return bl_abs_bl_pos
                    else:
                        # raise ValueError("why is this false??")
                        return []
                else:
                    # also selects a new block in the region...
                    bl_abs_bl_pos = self.select_new_region_prediction(mode,
                                                                      uav_pos,
                                                                      exc_bls)  # TODO
                    return bl_abs_bl_pos

        elif mode == "follower":
            look = True
            while look == True:
                if self.pred_fish.grid_arr_obj.any_unassigned_block_in_region(region):
                    # select nearest block towards sampler
                    bl_abs_bl_pos = self.pred_fish.select_nearest_block_towards_sampler()
                    if bl_abs_bl_pos == False:
                        # there aren't any samplers... just become a sampler...
                        pass
                    else:
                        return bl_abs_bl_pos
                    # break out of loop...
                    look = False
                else:
                    # if there are no unassigned blocks left in the region, start from 1 to select a new region
                    region = self.pred_fish.select_nearest_highly_profitable_region(
                        region)
                    if region == False:
                        # no samplers? -> become a sampler...
                        pass
                        # either way, look gets set to false...
                        # break out of loop...
                        look = False
                    else:
                        # repeat loop again... "any_unassigned_block_in_region"
                        pass
        else:
            raise ValueError("Invalid mode")

    def select_new_region_prediction(self, mode, uav_pos, exc_bls):
        """ ONLY FOR SAMPLER - original target region has become not unassigned, this method selects a new region
        Returns True if OK, False if no unassigned blocks in grid or mission timed out -> mission over
        """

        assert mode == "sampler"

        if self.pred_fish.grid_arr_obj.any_unassigned_region():
            # select nearest region
            cur_abs_bl_pos = pix_to_abs_block_position_xy(uav_pos[0:2])
            region = self.pred_fish.select_nearest_region(cur_abs_bl_pos)
            bl_abs_bl_pos = self.pred_fish.select_nearest_block(cur_abs_bl_pos,
                                                                region,
                                                                exc_bls)
            if not bl_abs_bl_pos == False:
                return bl_abs_bl_pos

            else:
                raise ValueError("why is this false??")

        else:
            # change mode to follower...
            return []
