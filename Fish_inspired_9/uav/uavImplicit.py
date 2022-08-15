"""

Add "moving time" to UAVs

Have a "target location" and an "actual location"
uav_pos_arr = "actual location", "target location" is internal...


Store numpy array
https://stackoverflow.com/questions/28439701/how-to-save-and-load-numpy-array-data-properly

"""


from constants.constants import *
from convert.convert import abs_to_region_block_pos, pix_to_abs_block_position_xy, pix_to_region_block_pos
from generalFunctions.generalFunctions import is_valid_region, uav_height_equal, print_i
from uav.uavFishCore import UavFishCore
from prediction.prediction import change_target


class UAV_implicit_fish(UavFishCore):
    """

    This class only performs the fish algorithm (not the task of updating the grid)

    state: follower or sampler

    """

    def __init__(self,
                 uav_fish_log_arr,
                 uav_fish_ex_bl_arr,
                 uav_init_mode,  # sampler, follower
                 i,
                 iter_count,
                 grid_arr_obj,
                 uav_pos_arr,
                 surv_arr,
                 all_modes_arr,
                 surv_log_arr,
                 explored_block_log_arr,
                 predict_arr,
                 prediction_flag=False):  # for the prediction targets
        """
        position:    BlockPosition object
        state:       follower or sampler
        desired_pos: Position where the uav will move to on each iteration update
        memory:      used in controlling the memorability of a sampler by its followers given the profitability of its region (memory is a percentage, 100 = 100%)
        forgetting_rate: controls the memory size of followers.
        """

        # initial sampler alg pos set to 2 if mode is sampler and 1 if mode is follower
        sampler_alg_pos_start = {"sampler": 2, "follower": 1}
        # initial follower alg pos set to 2 if mode is sampler and 4 if mode is follower
        follower_alg_pos_start = {"sampler": 2, "follower": 4}

        super().__init__(uav_fish_log_arr,
                         uav_fish_ex_bl_arr,
                         uav_init_mode,  # sampler, follower
                         i,
                         iter_count,
                         grid_arr_obj,
                         uav_pos_arr,
                         surv_arr,
                         all_modes_arr,
                         surv_log_arr,
                         explored_block_log_arr,
                         sampler_alg_pos_start,
                         follower_alg_pos_start,
                         self.set_mode_implicit)

        # array to keep track of the previous regions for the "target_region_still_unassigned" method
        start_reg = pix_to_region_block_pos(uav_pos_arr[self.i][0:2])[0]
        self.region_history = [start_reg]  # initialise with current region...
        # array to keep track of the previous blocks for the "target_block_still_unassigned" method
        self.abs_block_history = []

        self.predict_arr = predict_arr
        self.prediction_flag = prediction_flag

    def implicit_fish_alg_loop(self):

        self.fish_alg_loop(self.sampler_algorithm_start,
                           self.follower_algorithm_start,
                           self.target_changed,
                           None)  # after_loop_method

    def set_mode_implicit(self, mode):
        """ sets the uav mode (sampler or follower) for the implicit uav
        Also sets the sampler/follower_alg_pos for next start
        Also sets the target z position to UAV_MOVE_HEIGHT
        """
        self.mode = mode
        if self.mode == "sampler":
            # if new mode is sampler, set follower_alg_pos for next start
            self.follower_alg_pos = 2  # for next time it's a follower
        elif self.mode == "follower":
            # if new mode is follower, set sampler_alg_pos for next start
            self.sampler_alg_pos = 1  # set to 1 for next time uav is sampler
        else:
            raise ValueError(f"Invalid self.mode: {self.mode}")

        # set height to move when mode changes...
        self.target_px_pos[2] = UAV_MOVE_HEIGHT

    def uav_in_same_block(self):
        """ returns a list of the the number(s) [i_1, i_2, ...] of the uav(s) in the same block...
        """

        cur_pix_pos_xy = self.uav_pos_arr[self.i][0:2]
        cur_abs_bl = pix_to_abs_block_position_xy(cur_pix_pos_xy)
        uav_nums = []

        for i, uav_pos in enumerate(self.uav_pos_arr):
            # dont include itself
            if i == self.i:
                continue

            # check if uav not at move height
            if uav_height_equal(uav_pos[2], UAV_MOVE_HEIGHT):
                continue

            uav_abs_bl = pix_to_abs_block_position_xy(uav_pos[0:2])
            if cur_abs_bl == uav_abs_bl:
                uav_nums.append(i)

        return uav_nums

    def higher_priority_uav_in_same_block(self):
        """ returns True if there is another uav in the same block with a higher priority
            (uav_i < self.i)

            Lower the number the higher the priority
        """

        uavs_in_block = self.uav_in_same_block()

        if len(uavs_in_block) > 0:
            for uav_num in uavs_in_block:
                if uav_num > self.i:
                    self.select_new_block()
                    return True

        return False

    def sampler_in_same_region(self):
        """ returns a list of the the number(s) [i_1, i_2, ...]
         of the samplers(s) in the same region...
        """

        cur_pix_pos_xy = self.uav_pos_arr[self.i][0:2]
        cur_region = pix_to_region_block_pos(cur_pix_pos_xy)[0]
        uav_nums = []

        for i, uav_pos in enumerate(self.uav_pos_arr):
            # dont include itself
            if i == self.i:
                continue

            # check if uav not at move height
            if uav_height_equal(uav_pos[2], UAV_MOVE_HEIGHT):
                continue

            # check that uav is a sampler
            mode = self.all_modes_arr[i]
            if not mode == "sampler":
                continue

            uav_region = pix_to_region_block_pos(uav_pos[0:2])[0]
            if cur_region == uav_region:
                uav_nums.append(i)

        return uav_nums

    def higher_priority_sampler_in_same_region(self):
        """ returns True if there is another sampler in the same region with a higher priority
            (uav_i < self.i)
        """

        samplers_in_region = self.sampler_in_same_region()
        if len(samplers_in_region) > 0:
            for sam_num in samplers_in_region:
                if sam_num > self.i:
                    self.select_new_region()
                    return True

        return False

    def target_changed(self):
        """ checks (and changes if necessary) the target position

        First checks if target position needs updating
            -> block/region still unassigned,
            -> if over target block, change target z

        """

        # check if the target needs to change due to the prediction...
        """
        if there is another uav that has the same target block
            if it is closer
                change target...
        """

        if self.prediction_flag:
            # target change because of prediction...
            if change_target(self.i, self.target_px_pos[0:2], self.predict_arr, self.uav_pos_arr) == True:

                # TODO surely a faster way than a loop..
                # get list of blocks that are already targets...
                exc_blocks = []
                for bl in self.predict_arr:
                    if not bl == []:
                        exc_blocks.append(pix_to_abs_block_position_xy(bl))

                self.select_new_block(exc_blocks)
                # self.predict_arr[self.i] = self.target_px_pos[0:2] #?.....
                return True

        # check if target block is still unassigned
        if not self.target_block_still_unassigned():
            # if it isnt, select a new block....
            self.select_new_block()
            return True

        if self.mode == "sampler":
            if not self.target_region_still_unassigned():
                self.select_new_region()
                return True

        # first check if UAV is over target block
        # need to only do this once per block... only the first time the uav is over the target block
        if self.first_time_uav_over_target_block():
            # * check if any other uav is in the block
            # if other uav in the block has a lower number (i), then give priority to that uav...
            if self.higher_priority_uav_in_same_block():
                return True

            # only for samplers
            if self.mode == "sampler":
                if self.higher_priority_sampler_in_same_region():
                    return True

            tar_abs_bl_pos = pix_to_abs_block_position_xy(
                self.target_px_pos[0:2])
            tar_reg_pos = abs_to_region_block_pos(tar_abs_bl_pos)[0]
            # add target region to the region history

            if not tar_reg_pos in self.region_history:
                self.region_history.append(tar_reg_pos)

            # add this block to the abs_block_history
            if not tar_abs_bl_pos in self.abs_block_history:
                self.abs_block_history.append(tar_abs_bl_pos)

            if self.uav_pos_arr[self.i][2] == UAV_MOVE_HEIGHT:
                self.update_target_position(
                    z_abs_pix_pos=self.get_mode_height())
                return True

        return False

    def target_block_still_unassigned(self):
        """ see if the target block is still unassigned
        Returns True if target block is still unassigned, False otherwise

        Takes into account if we assigned the block...
        """
        tar_pos_xy = self.target_px_pos[0:2]
        tar_abs_bl = pix_to_abs_block_position_xy(tar_pos_xy)
        tar_reg_bl = abs_to_region_block_pos(tar_abs_bl)

        # check if the uav is already in the block, then it is fine
        if tar_abs_bl in self.abs_block_history:
            return True

        tar_bl_state = self.grid_arr_obj.get_block_state(
            tar_reg_bl[0], tar_reg_bl[1])

        if not tar_bl_state == "unassigned":
            return False

        return True

    def target_region_still_unassigned(self):
        """ see if the (new) target region is still unassigned
        Only for new regions though, if the sampler is already in its region of course it will be assigned...
        Returns True if target region is still unassigned or we are already in the region, False otherwise
        """

        tar_pos_xy = self.target_px_pos[0:2]
        tar_abs_bl = pix_to_abs_block_position_xy(tar_pos_xy)
        tar_reg_bl = abs_to_region_block_pos(tar_abs_bl)

        # check if the uav is already in the region, then it is fine
        if tar_reg_bl[0] in self.region_history:
            return True

        grid_arr = self.grid_arr_obj.get_grid_arr()

        reg_state = grid_arr[tar_reg_bl[0][1], tar_reg_bl[0][0]].get_state()

        if not reg_state == "unassigned":
            return False

        return True

    def other_uav_in_block(self):
        """ check if there are any other UAVs in the same block
        Returns True if there is at least one other UAV in the same block
        """

        cur_pix_pos = self.uav_pos_arr[self.i][0:2]
        cur_abs_bl_pos = pix_to_abs_block_position_xy(cur_pix_pos)

        for i, uav_pos in enumerate(self.uav_pos_arr):
            if not i == self.i:
                check_abs_bl = pix_to_abs_block_position_xy(uav_pos[0:2])
                if check_abs_bl == cur_abs_bl_pos:
                    return True

        # if there are no other UAVs in the same block
        return False

    def select_new_region(self):
        """ ONLY FOR SAMPLER - original target region has become not unassigned, this method selects a new region
        Returns True if OK, False if no unassigned blocks in grid or mission timed out -> mission over
        """

        # TODO assert rather...

        if self.mode == "sampler":

            if self.grid_arr_obj.any_unassigned_region():
                # select nearest region
                uav_abs_bl_pos = self.get_abs_block_position()
                region = self.select_nearest_region(uav_abs_bl_pos)
                # set profitability = 0 -> should already be zero
                cur_abs_bl_pos = self.get_abs_block_position()  # TODO is this a repeat??
                bl_abs_bl_pos = self.select_nearest_block(cur_abs_bl_pos,
                                                          region)
                if not bl_abs_bl_pos == False:
                    # set UAV target position
                    self.update_target_position(x_abs_bl_pos=bl_abs_bl_pos[0],
                                                y_abs_bl_pos=bl_abs_bl_pos[1])

                    # set to 3 so it searches the block...
                    self.sampler_alg_pos = 3

                else:
                    raise ValueError("why is this false??")

            else:
                self.set_mode("follower")
                # need to set the follower_alg_pos to
                # set follower_alg_pos to 4 so it looks for survivor in the already assigned block
                self.follower_alg_pos = 4
        else:
            print("Error in uav.UAV_fish.select_new_region")

    def select_new_block(self, exc_bls=[]):
        """ original target block has become not unassigned, this method selects a new block"""

        region = self.get_region_position()  # default region pos

        if not is_valid_region(region):
            # happens when second uav enters area and first one takes assigned block, when searching for a new unassigned block, the current position is still off the grid so the region is off the grid...
            # region = [0, 0]  # ? set region to [0, 0] ??
            raise ValueError(f"Invalid region, region={region}")

        if self.mode == "sampler":

            num = 0
            while num < TOTAL_BLOCKS:
                num += 1
                if self.grid_arr_obj.any_unassigned_block_in_region(region):
                    cur_abs_bl_pos = self.get_abs_block_position()
                    bl_abs_bl_pos = self.select_nearest_block(cur_abs_bl_pos,
                                                              region,
                                                              exc_bls)
                    if not bl_abs_bl_pos == False:
                        # set UAV target position
                        self.update_target_position(x_abs_bl_pos=bl_abs_bl_pos[0],
                                                    y_abs_bl_pos=bl_abs_bl_pos[1])
                        # set to 3 so it searches the block...
                        self.sampler_alg_pos = 3
                        break
                    else:
                        # select new region ...
                        self.select_new_region()
                        break
                        # raise ValueError("why is this false??")

                else:
                    # also selects a new block in the region...
                    self.select_new_region()
                    break

        elif self.mode == "follower":
            look = True

            while look == True:
                if self.grid_arr_obj.any_unassigned_block_in_region(region):
                    # select nearest block towards sampler
                    # ? what if there aren't any samplers???
                    bl_abs_bl_pos = self.select_nearest_block_towards_sampler(
                        exc_bls)

                    # ? what if no blocks are unassigned ??? <<-- what if this changes while the algorithm is running...
                    if bl_abs_bl_pos == False:
                        # there aren't any samplers...
                        # block_region == False, therefore no unassigned blocks close to sampler
                        # just become a sampler...
                        self.set_mode("sampler")
                    else:
                        # set UAV target position
                        self.update_target_position(x_abs_bl_pos=bl_abs_bl_pos[0],
                                                    y_abs_bl_pos=bl_abs_bl_pos[1])
                        # set to 4 so it looks for survivor in new block
                        self.follower_alg_pos = 4

                    # break out of loop...
                    look = False

                else:
                    # if there are no unassigned blocks left in the region, start from 1 to select a new region
                    region = self.select_nearest_highly_profitable_region(
                        region)
                    if region == False:
                        # no samplers? -> become a sampler...
                        if self.no_unassigned_block_or_mission_timeout():
                            # mission done, return home
                            self.update_target_position(x_abs_bl_pos=-1,
                                                        y_abs_bl_pos=-1,
                                                        z_abs_pix_pos=UAV_MOVE_HEIGHT)
                        else:
                            self.set_mode("sampler")

                        # either way, look gets set to false...
                        # break out of loop...
                        look = False
                    else:
                        # memory = 100%
                        self.set_memory_100()
                        # generate forgetting rate
                        self.generate_forgetting_rate()
                        # repeat loop again... "any_unassigned_block_in_region"

        else:
            raise ValueError("Invalid mode")

    def all_uav_states_known(self):
        """ checks if all other uav states are known
        Returns True if all other uav states are known...
        """

        # for mode in self.last_known_modes_arr:
        for mode in self.all_modes_arr:
            if not (mode == "sampler" or mode == "follower"):
                return False

        return True

    def sampler_algorithm_start(self):
        """
        ignore travel time??
        """

        region = self.get_region_position()  # default region pos

        if not is_valid_region(region):
            raise ValueError(f"Invalid region: {region}")

        if self.sampler_alg_pos == 1:
            if self.grid_arr_obj.any_unassigned_region():
                # select nearest region
                uav_abs_bl_pos = self.get_abs_block_position()
                region = self.select_nearest_region(uav_abs_bl_pos)
                # set profitability = 0 -> should already be zero
                self.sampler_alg_pos = 2
            else:
                self.sampler_alg_pos = 5

        if self.sampler_alg_pos == 2:
            if self.grid_arr_obj.any_unassigned_block_in_region(region):
                cur_abs_bl_pos = self.get_abs_block_position()
                bl_abs_bl_pos = self.select_nearest_block(cur_abs_bl_pos,
                                                          region)
                if not bl_abs_bl_pos == False:
                    # set UAV target position
                    self.update_target_position(x_abs_bl_pos=bl_abs_bl_pos[0],
                                                y_abs_bl_pos=bl_abs_bl_pos[1])
                else:
                    raise ValueError("why is this false??")

                self.sampler_alg_pos = 3
                return  # return so uav can move to new position...
            else:
                self.sampler_alg_pos = 1
                # normal to not move for this iteration when the region is explored
                # * next iteration... (end = True for when its in a loop)

        if self.sampler_alg_pos == 3:
            any_survivors_if_so_then_rescue = self.any_survivors_if_so_then_rescue()
            if any_survivors_if_so_then_rescue == None:
                # still in delay...
                pass
            else:
                if any_survivors_if_so_then_rescue == True:
                    # survivors are rescued if there are any in the block...
                    # * increase profitability --> happens in other thread
                    pass
                elif any_survivors_if_so_then_rescue == False:
                    # no survivors found...
                    pass

                # regardless, if NOT still in delay, the next pos is 4
                self.sampler_alg_pos = 4

        if self.sampler_alg_pos == 4:
            if self.grid_arr_obj.region_explored(region):
                self.sampler_alg_pos = 5
            else:
                self.sampler_alg_pos = 2
                # * next iteration...

        if self.sampler_alg_pos == 5:
            if self.no_unassigned_block_or_mission_timeout():
                # mission done, return home
                self.update_target_position(x_abs_bl_pos=-1,
                                            y_abs_bl_pos=-1,
                                            z_abs_pix_pos=UAV_MOVE_HEIGHT)

                # * next iteration...
            else:
                # change mode to follower
                self.set_mode("follower")
                # * next iteration

        # set assigned after running algorithm
        self.set_current_block_state("assigned")

        return

    def follower_algorithm_start(self):

        region = self.get_region_position()  # default region pos

        if not is_valid_region(region):
            raise ValueError(f"Invalid region: {region}")

        if self.follower_alg_pos == 1:
            # select highly profitable region
            region = self.select_nearest_highly_profitable_region(region)
            if region == False:
                # might be because there are no samplers? or because there are no unassigned blocks...
                if self.no_unassigned_block_or_mission_timeout():
                    # mission done, return home
                    self.update_target_position(x_abs_bl_pos=-1,
                                                y_abs_bl_pos=-1,
                                                z_abs_pix_pos=UAV_MOVE_HEIGHT)

                else:
                    # become a sampler...
                    self.set_mode("sampler")

                # either way, return
                return

            self.follower_alg_pos = 2

        if self.follower_alg_pos == 2:
            # memory = 100%
            self.set_memory_100()
            # generate forgetting rate
            self.generate_forgetting_rate()
            self.follower_alg_pos = 3

        if self.follower_alg_pos == 3:
            if self.grid_arr_obj.any_unassigned_block_in_region(region):
                # select nearest block towards sampler
                bl_abs_bl_pos = self.select_nearest_block_towards_sampler()

                if not bl_abs_bl_pos == False:
                    # set UAV target position
                    self.update_target_position(x_abs_bl_pos=bl_abs_bl_pos[0],
                                                y_abs_bl_pos=bl_abs_bl_pos[1])
                    self.follower_alg_pos = 4
                    return  # return so uav can move to new position...

                else:
                    # there aren't any samplers...
                    # block_region == False, therefore no unassigned blocks close to sampler
                    # just become a sampler...
                    self.set_mode("sampler")
            else:
                self.follower_alg_pos = 1
                # * next iteration...

        if self.follower_alg_pos == 4:

            any_survivors_if_so_then_rescue = self.any_survivors_if_so_then_rescue()
            if any_survivors_if_so_then_rescue == None:
                # still in delay...
                pass
            else:
                if any_survivors_if_so_then_rescue == True:
                    # survivors are rescued if there are any in the block...
                    # *increase profitability -> happens in other thread
                    # decrease forgetting rate
                    self.decrease_forgetting_rate()
                    self.follower_alg_pos = 6
                elif any_survivors_if_so_then_rescue == False:
                    # no survivors found...
                    # decrease memory
                    self.decrease_memory()
                    # increase forgetting rate
                    self.increase_forgetting_rate()
                    self.follower_alg_pos = 5

                # regardless, if not still in delay, the next pos is 4
                self.follower_alg_pos = 5

        if self.follower_alg_pos == 5:
            if self.memory > 0:
                self.follower_alg_pos = 6
            else:
                self.follower_alg_pos = 7

        if self.follower_alg_pos == 6:
            if self.grid_arr_obj.region_explored(region):
                self.follower_alg_pos = 8
            else:
                self.follower_alg_pos = 3
                # * next iteration...

        if self.follower_alg_pos == 7:
            if self.grid_arr_obj.any_unassigned_region():
                self.set_mode("sampler")
            else:
                self.follower_alg_pos = 8

        if self.follower_alg_pos == 8:
            if self.no_unassigned_block_or_mission_timeout():
                # mission done, return home
                self.update_target_position(x_abs_bl_pos=-1,
                                            y_abs_bl_pos=-1,
                                            z_abs_pix_pos=UAV_MOVE_HEIGHT)
            else:
                self.follower_alg_pos = 3
                # * next iteration...

        # set assigned after running algorithm
        self.set_current_block_state("assigned")

        return
