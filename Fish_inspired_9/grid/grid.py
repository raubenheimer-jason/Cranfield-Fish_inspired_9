from constants.constants import *
import numpy as np
from blockPosition.blockPosition import BlockPosition
from block.block import Block
from region.region import Region
from convert.convert import abs_to_region_block_pos, pix_to_abs_block_position_xy, abs_block_to_pixel_xy, reg_bl_to_abs_bl_position
import time
from generalFunctions.generalFunctions import is_valid_region, uav_height_equal


def uav_xy_equal(uav_xy_pos, test_xy_pos, precision=1):
    """checks the uav xy position against the test xy position (can add a tolerance etc here...)
    uav_pos, test_pos --> [x, y]
    """

    if len(uav_xy_pos) > 2 or len(test_xy_pos) > 2:
        print("Error in grid.uav_xy_equal - more than x,y input")

    # range to limit to only x,y if x,y,z is input by mistake...
    for i in range(2):
        if not round(uav_xy_pos[i], precision) == round(test_xy_pos[i], precision):
            return False

    return True


def uav_moved(uav_pos, test_pos):
    """ check if the height or the xy position is not equal"""

    if not uav_height_equal(uav_pos[2], test_pos[2]):
        return True

    if not uav_xy_equal(uav_pos[0:2], test_pos[0:2]):
        return True

    return False


def uav_on_grid(uav_pos):
    """ checks if uav is on the grid 
    Used to check state, if uav is off the grid it can only be in "move" state
    """

    uav_abs_bl_pos = pix_to_abs_block_position_xy(uav_pos[0:2])

    if uav_abs_bl_pos[0] >= 0 and uav_abs_bl_pos[1] >= 0:
        return True

    return False


def uav_state_from_height(uav_pos):

    uav_height = uav_pos[2]

    if uav_on_grid(uav_pos):

        if uav_height_equal(uav_height, UAV_RESCUE_HEIGHT):
            return "rescue"

        if uav_height_equal(uav_height, UAV_SAMPLER_HEIGHT):
            return "sampler"

        if uav_height_equal(uav_height, UAV_FOLLOWER_HEIGHT):
            return "follower"

    if uav_height_equal(uav_height, UAV_MOVE_HEIGHT):
        return "move"

    return "unknown"


def set_states_arr(uav_i,
                   last_known_modes_arr,   # UAV_fish
                   uav_states_arr,      # Display3
                   state):

    # used for display...
    if uav_states_arr:
        uav_states_arr[uav_i] = state

    # used for UAVs
    # last_known_states_lock will be None if update_grid_arr is called by Display3
    if last_known_modes_arr:
        if state == "sampler" or state == "follower":
            last_known_modes_arr[uav_i] = state


def highest_state_count(id, uav_i, prev_state_arr):
    """ prev_state_arr --> [[state_now, uav_height],[]] 

    """

    # return the state that has the highest count in the prev_state_arr
    count_dict = {
        "rescue": prev_state_arr.count("rescue"),
        "sampler": prev_state_arr.count("sampler"),
        "follower": prev_state_arr.count("follower"),
        "move": prev_state_arr.count("move"),
        "unknown": prev_state_arr.count("unknown"),
    }

    ordered_dict = {k: v for k, v in sorted(
        count_dict.items(), key=lambda item: item[1], reverse=True)}

    max_cnt = 0
    first_key_val = next(iter(ordered_dict.items()))
    first_key = first_key_val[0]
    first_val = first_key_val[1]

    for key_val in ordered_dict.items():

        # rescue state only requires one...
        if key_val[0] == "rescue" and int(key_val[1]) > 0:
            return "rescue"

        if key_val[1] == first_val:
            max_cnt += 1

    if max_cnt > 1:
        return prev_state_arr[-1]  # most recent state

    return first_key


def uav_state_prediction(id, uav_i, prev_state_arr, uav_pos):
    """if uav has been at the same height for X time, then check the state (i.e. it isnt transitioning)
    last_known_state = [state, time]

    only check for new state if uav height is different from previous time the state was checked 
    """

    # TODO eventually we need to improve the state predictor in the grid_arr algorithm so we dont just jump z...

    if JUMP_Z_MOVE == True:

        return uav_state_from_height(uav_pos)

    else:

        # if prev_state_arr:
        #     prev_pos = prev_state_arr[-1][1:4]  # last element [x,y,z]
        # else:
        #     prev_pos = None

        # if prev_pos == None or uav_moved(uav_pos, prev_pos):

        # if id == -1:
        #     print(f"height not equal... prev_state_arr: {prev_state_arr}")
        # state_now = uav_state_from_height(id, uav_i, uav_height)
        # uav_height = uav_pos[2]
        # state_now = uav_state_from_height(uav_height)
        state_now = uav_state_from_height(uav_pos)
        # add new state to list for this iteration (only if height has changed...)
        # prev_state_arr.append(state_now)
        prev_state_arr.append([state_now] + uav_pos)  # ["follower", x, y, z]

        # check if state arr for UAV is too long
        if len(prev_state_arr) > NUM_SAME_STATES:
            prev_state_arr.pop(0)  # remove element at index 0 (FIFO)

        # print(f"prev_state_arr: {prev_state_arr}")

        only_states_list = [item[0] for item in prev_state_arr]
        # print(f"only_states_list: {only_states_list}")
        return_state = highest_state_count(id, uav_i, only_states_list)
        # return_state = highest_state_count(id, uav_i, state_now, only_states_list)
        # return_state = highest_state_count(id, uav_i, state_now, prev_state_arr)

        return return_state


def store_grid_log(grid_log_arr, grid_arr_obj):
    """
    ["time_s", "type", "abs_block_pos_x", "abs_block_pos_y", "region_pos_x", "region_pos_y", "block_state"]
    """

    grid_arr = grid_arr_obj.get_grid_arr()

    for row in grid_arr:
        for region in row:
            bl_arr = region.get_block_arr()
            for row in bl_arr:
                for block in row:
                    bl_state = block.get_state()
                    bl_abs_pos = block.get_abs_position()
                    bl_reg_pos = block.get_region_position()
                    app_arr = [time.time(),
                               "grid",
                               bl_abs_pos[0],
                               bl_abs_pos[1],
                               bl_reg_pos[0],
                               bl_reg_pos[1],
                               bl_state]
                    grid_log_arr.append(app_arr)


def store_surv_log(surv_log_arr, surv_arr):

    for i, surv in enumerate(surv_arr):
        # info: surv -> [x_pos, y_pos, state]
        # [["time_s", "type", "surv_id", "abs_block_pos_x", "abs_block_pos_y", "surv_state"]]
        app_arr = [time.time(), "survivor", i, surv[0], surv[1], surv[2]]
        surv_log_arr.append(app_arr)


def get_assigned_blocks(grid_arr_obj):

    assigned_blocks = list()

    for grid_row in grid_arr_obj.get_grid_arr():
        for region in grid_row:
            reg_arr = region.get_block_arr()
            for reg_row in reg_arr:
                for bl in reg_row:
                    if bl.get_state() == "assigned":
                        assigned_blocks.append(bl.get_abs_position()[0:2])

    return assigned_blocks


def log_block_state(explored_block_log_arr,
                    state,
                    reg_bl,
                    uav_num,
                    iter_num):

    bl_abs_pos = reg_bl_to_abs_bl_position(reg_bl[0], reg_bl[1])

    # [iteration_number, uav_num,  abs_bl_pos_x,  abs_bl_pos_y, state]
    explored_block_log_arr.append([iter_num[0],
                                   uav_num,
                                   bl_abs_pos[0],
                                   bl_abs_pos[1],
                                   state])


def update_grid_arr(run_state,  # used for uav
                    grid_log_arr,
                    surv_log_arr,  # used for Display3
                    explored_block_log_arr,  # only for implicit, None otherwise
                    surv_arr,  # used for Display3
                    id,
                    uav_pos_arr,
                    uav_states_arr,  # used for Display3
                    last_known_modes_arr,  # UAV_fish (only follower/sampler)
                    grid_arr_obj,
                    prev_pos_uav_arr,
                    all_prev_states_arr,
                    rescue_pos_arr,
                    update_block_state_flag,
                    iter_num,
                    exp_blocks_arr):  # array to keep track of explored blocks so we dont record a second time
    """
    Used by UAVs and display

    read uav_arr and update grid_arr_obj based on uav positions

    Grid state: unassigned     -> default, no UAV been there
    Grid state: assigned       -> UAV in that area
    Grid state: explored       -> was assigned but now there isn't a uav there
    Region profitability       -> Survivor rescued -> UAV below certain altitude and there for some time
    Teammate sampler/follower  -> Different altitudes (low = sampler, high = follower)


    """

    s = time.time()

    # once set to true we dont have to check for this again
    if update_block_state_flag[0] == False:
        rs_val = run_state[0]
        if rs_val == 3 or rs_val == 4:  # only fish algorithm or rescue states
            update_block_state_flag[0] = True

    for i, u in enumerate(uav_pos_arr):

        uav_pos = u[0:3]
        uav_height = uav_pos[2]
        uav_pos_bl = pix_to_abs_block_position_xy(uav_pos[0:2])

        # check if uav has changed position (region/block) since last checking
        # get current position of uav
        uav_reg_bl = abs_to_region_block_pos(uav_pos_bl)

        # 1. check if prev pos != current pos --> then set prev pos = explored
        # # only if UAV is not at MOVE height...
        # if not uav_height_equal(uav_height, UAV_MOVE_HEIGHT):
        if prev_pos_uav_arr[i]:
            # get previous position of uav
            prev_uav_pos_bl = pix_to_abs_block_position_xy(
                prev_pos_uav_arr[i][0:2])
            if not prev_uav_pos_bl == uav_pos_bl:
                # uav is in a different region/block
                # update the previous block to explored
                prev_uav_reg_bl = abs_to_region_block_pos(prev_uav_pos_bl)
                grid_arr_obj.update_block_state("explored",
                                                prev_uav_reg_bl[0],
                                                prev_uav_reg_bl[1])

                # -2 is for the LogContainer, this is only for implicit
                if id == -2:

                    # make sure we haven't already recorded the blocks
                    if not prev_uav_reg_bl in exp_blocks_arr:
                        # if explored_block_log_arr:
                        log_block_state(explored_block_log_arr,
                                        "explored",
                                        prev_uav_reg_bl,
                                        i,
                                        iter_num)
                        exp_blocks_arr.append(prev_uav_reg_bl)

        # 2. check if current height != move height --> then set current pos = assigned
        if id == i:
            # this is for our UAV...
            # block must only get set to assigned if we are at the center of it....
            # maybe still mustnt get assigned here becasue it might mess up the fish algorithm...
            pass

        else:
            # check that uav is not at "move" height
            if update_block_state_flag[0] == True:
                # if not uav_height == UAV_MOVE_HEIGHT:
                if not uav_height_equal(uav_height, UAV_MOVE_HEIGHT):
                    grid_arr_obj.update_block_state("assigned",
                                                    uav_reg_bl[0],
                                                    uav_reg_bl[1])

        state = uav_state_prediction(id,
                                     i,
                                     all_prev_states_arr[i],
                                     uav_pos)

        set_states_arr(i,
                       last_known_modes_arr,
                       uav_states_arr,
                       state)

        if state == "rescue":
            if not uav_pos_bl in rescue_pos_arr:
                grid_arr_obj.increment_profitability(uav_reg_bl[0])
                # one one survivor per block... remember this position
                rescue_pos_arr.append(uav_pos_bl)

        # only if UAV is not at MOVE height...
        if not uav_height_equal(uav_height, UAV_MOVE_HEIGHT):
            # and only if uav is at the center of the block...
            if uav_at_center_of_block(uav_pos):
                prev_pos_uav_arr[i] = uav_pos

    if not grid_log_arr == None:
        store_grid_log(grid_log_arr, grid_arr_obj)

    if not surv_log_arr == None:
        store_surv_log(surv_log_arr, surv_arr)

    # time.sleep(0.5)

    # if id == -2:
    #     print(f"loop time (ms): {(time.time()-s)*1000}")


def uav_at_center_of_block(uav_pos):
    """ returns True if the uav pix position is the center of the current block """

    uav_pix_xy = uav_pos[0:2]

    uav_abs_bl_pos = pix_to_abs_block_position_xy(uav_pix_xy)
    expected_pix_xy = abs_block_to_pixel_xy(uav_abs_bl_pos)

    if uav_xy_equal(uav_pix_xy, expected_pix_xy):
        return True

    return False


class gridArr:
    def __init__(self):
        """
        rx = region x position (within the grid)
        ry = region y position (within the grid)

        bx = block x position (within the region)
        by = block y position (within the region)
        """

        """ Grid array

        array of regions

        1. A survivor can be in one of the four states: discovered, undiscovered, deceased, or rescued. At the start of the mission, the statuses of all survivors are unknown.

        2. The mission area is logically structured as a grid of blocks with each block holding at most a single survivor.

        3. Regions and blocks can be in one of the following states: unassigned, assigned or explored.
        3.1  Assigned block: is a block that has been selected by a UAV but where the search for a survivor is yet to be completed.
        3.2  Assigned region: is a region with at least one assigned block.
        3.3  A block is said to be explored when a search for a survivor has been completed.
        3.4  When all blocks in a region have been explored, then the region is said to be explored as well.
        3.5  At the start of the mission, the statuses of the regions and blocks are set to unassigned and change as the mission progresses.
        """

        self.grid_arr = np.empty(shape=GRID_SHAPE, dtype=object)

        for ry in range(GRID_SIZE):
            for rx in range(GRID_SIZE):
                # this is a region, now create the blocks within the region
                region_shape = (REGION_SIZE, REGION_SIZE)
                region_arr = np.empty(shape=region_shape, dtype=object)

                for by in range(REGION_SIZE):
                    for bx in range(REGION_SIZE):
                        # create block objects here, assign to position in region array
                        position = BlockPosition(
                            local_position=[bx, by], region_position=[rx, ry])
                        region_arr[by][bx] = Block(position=position)

                self.grid_arr[ry][rx] = Region([rx, ry], region_arr)

        # Now we have an array of GRID_SIZE x GRID_SIZE of Region objects and each Region object contains an array of REGION_SIZE x REGION_SIZE block objects

        self.num_rescued_survivors_in_grid = 0
        self.num_explored_blocks_in_grid = 0
        self.num_assigned_blocks_in_grid = 0

    def get_stats_arr(self):
        """return stats_arr: [blocks_explored, num_assigned_blocks, survivors_rescued]"""
        return [self.num_explored_blocks_in_grid, self.num_assigned_blocks_in_grid, self.num_rescued_survivors_in_grid]

    def increment_num_explored_blocks_in_grid(self):
        """increment the number of explored blocks"""
        self.num_explored_blocks_in_grid += 1
        # print(
        #     f"num_explored_blocks_in_grid: {self.num_explored_blocks_in_grid}")

    def increment_num_assigned_blocks_in_grid(self):
        """increment the number of assigned blocks"""
        self.num_assigned_blocks_in_grid += 1

    def decrement_num_assigned_blocks_in_grid(self):
        """decrement the number of assigned blocks"""
        self.num_assigned_blocks_in_grid -= 1

    def get_grid_arr(self):
        """returns grid_arr"""
        return self.grid_arr

    def get_block_state(self, region, block):
        """"""
        bl_state = self.grid_arr[region[1]][region[0]].get_block_state(block)
        return bl_state

    def any_unassigned_region(self):
        """
        check if there are any regions that are unassigned

        Loops over grid_arr and checks the state of each region

        returns True if there is an unassigned region, False otherwise
        """
        # loop over _grid_arr and get state of each region
        for row in self.grid_arr:
            for region in row:
                if region.get_state() == "unassigned":
                    return True

        return False

    def any_unassigned_block_in_region(self, region):
        """check if there are any blocks in the region that are unassigned
        returns True or False
        """

        if not is_valid_region(region):
            print("Error in grid.GridArr.any_unassigned_block_in_region")
            # should raise exception here... because return False will work
            raise ValueError(f"Invalid region, region = {region}")

        if self.grid_arr[region[1]][region[0]].has_unassigned_block():
            return True
        else:
            return False

    def any_unassigned_block_in_grid(self):
        """check if there are any blocks in the WHOLE GRID that are unassigned
        returns True if there are unassigned blocks
        """

        num_explored_assigned = self.num_assigned_blocks_in_grid + \
            self.num_explored_blocks_in_grid
        if num_explored_assigned >= TOTAL_BLOCKS:
            return False
        else:
            return True

    def increment_profitability(self, region):
        """Increments the profit of the specified region
        Also increments the "num_rescued_survivors_in_grid"
        """

        if not is_valid_region(region):
            print("Error grid.gridArr.increment_profitability: region")
            raise ValueError(f"Invalid region, region = {region}")

        self.grid_arr[region[1]][region[0]].increment_profit()
        self.num_rescued_survivors_in_grid += 1

    def region_explored(self, region):
        """return True if region is explored (all blocks are explored)"""

        # get the region state
        reg_state = self.grid_arr[region[1]][region[0]].get_state()

        if reg_state == "explored":
            return True
        else:
            return False

    def update_block_state(self, state, region, block):
        """
        updates the state of the block that the uav is currently in

        - Assigned: is a block that has been selected by a UAV but where the search for a survivor is yet to be completed.
        - explored: when a search for a survivor has been completed.

        Need to update the state of the specific block
        """
        # TODO: add check to make sure state is valid

        # we know the UAV position, find the block that relates to that position

        # finds the Region object in the _grid_arr
        # then finds the Block object in the region object's block_arr
        # then uses the Block object's "set_state" method to change the state

        accepted_states = ["unassigned", "assigned", "explored"]

        if not state in accepted_states:
            return

        if region[0] < 0 or region[1] < 0:
            return

        if block[0] < 0 or block[1] < 0:
            return

        prev_bl_state = self.get_block_state(region, block)

        if prev_bl_state == "unassigned" and state == "assigned":
            self.increment_num_assigned_blocks_in_grid()
        elif prev_bl_state == "assigned" and state == "explored":
            self.increment_num_explored_blocks_in_grid()
            self.decrement_num_assigned_blocks_in_grid()
        else:
            return

        self.grid_arr[region[1]][region[0]].update_block_state(state, block)
