"""

Original "fish-inspired" algorithm with direct communication (grid state shared)

"""

from constants.constants import *
from convert.convert import abs_to_region_block_pos
from generalFunctions.generalFunctions import is_valid_region, print_i, uav_height_equal
from uav.uavFishCore import UavFishCore


class UAV_original_fish(UavFishCore):
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
                 grid_arr_obj,  # common grid_arr_obj between all uavs
                 uav_pos_arr,
                 surv_arr,
                 all_modes_arr,
                 uav_states_arr,
                 surv_log_arr,
                 explored_block_log_arr):
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
        follower_alg_pos_start = {"sampler": 2, "follower": 3}

        super().__init__(uav_fish_log_arr,
                         uav_fish_ex_bl_arr,
                         uav_init_mode,  # sampler, follower
                         i,
                         iter_count,
                         grid_arr_obj,  # common grid_arr_obj between all uavs
                         uav_pos_arr,
                         surv_arr,
                         all_modes_arr,
                         surv_log_arr,
                         explored_block_log_arr,
                         sampler_alg_pos_start,
                         follower_alg_pos_start,
                         self.set_mode_original)

        self.uav_states_arr = uav_states_arr

    def original_fish_alg_loop(self):

        self.fish_alg_loop(self.sampler_algorithm_start,
                           self.follower_algorithm_start,
                           self.target_changed,
                           self.original_after_loop_method)

    def original_after_loop_method(self):
        # set the states array here for the display
        self.uav_states_arr[self.i] = self.get_state_from_height()

    def target_changed(self):
        """ checks (and changes if necessary) the target position (for original this is just the height...)

        First checks if target position needs updating
            -> if over target block, change target z

        """

        # first check if UAV is over target block
        # need to only do this once per block... only the first time the uav is over the target block
        if self.first_time_uav_over_target_block():
            if self.uav_pos_arr[self.i][2] == UAV_MOVE_HEIGHT:
                self.update_target_position(
                    z_abs_pix_pos=self.get_mode_height())
                return True

        return False

    def get_state_from_height(self):

        my_height = self.uav_pos_arr[self.i][2]

        if uav_height_equal(my_height, UAV_MOVE_HEIGHT):
            return "move"

        if uav_height_equal(my_height, UAV_SAMPLER_HEIGHT):
            return "sampler"

        if uav_height_equal(my_height, UAV_FOLLOWER_HEIGHT):
            return "follower"

        if uav_height_equal(my_height, UAV_RESCUE_HEIGHT):
            return "rescue"

        return "unknown"

    def set_mode_original(self, mode):
        """ sets the uav mode (sampler or follower) for the original uav (sets the state array as well...)
        Also sets the sampler/follower_alg_pos for next start
        Also sets the target z position to UAV_MOVE_HEIGHT
        """
        self.mode = mode
        self.all_modes_arr[self.i] = mode

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

                    # * ALSO for *original* -> set block as assigned in grid_arr...
                    reg_bl_pos = abs_to_region_block_pos(bl_abs_bl_pos)
                    self.set_block_state("assigned",
                                         reg_bl_pos[0],
                                         reg_bl_pos[1])

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
                    # * for *original* -> increase region profitability...
                    self.grid_arr_obj.increment_profitability(region)
                    pass
                elif any_survivors_if_so_then_rescue == False:
                    # no survivors found...
                    pass

                # * for *original* -> set block to explored
                reg_bl_pos = self.get_reg_bl_pos()
                self.set_block_state("explored",
                                     reg_bl_pos[0],
                                     reg_bl_pos[1])

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

                    # * ALSO for *original* -> set block as assigned in grid_arr...
                    reg_bl_pos = abs_to_region_block_pos(bl_abs_bl_pos)
                    self.set_block_state("assigned",
                                         reg_bl_pos[0],
                                         reg_bl_pos[1])

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
                    # * for *original* -> increase region profitability...
                    self.grid_arr_obj.increment_profitability(region)
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

                # * for *original* -> set block to explored
                reg_bl_pos = self.get_reg_bl_pos()
                self.set_block_state("explored",
                                     reg_bl_pos[0],
                                     reg_bl_pos[1])

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

        return
