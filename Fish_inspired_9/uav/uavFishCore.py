"""

Add "moving time" to UAVs

Have a "target location" and an "actual location"
uav_pos_arr = "actual location", "target location" is internal...


Store numpy array
https://stackoverflow.com/questions/28439701/how-to-save-and-load-numpy-array-data-properly

"""


import random
import math
from constants.constants import *
import time
from convert.convert import abs_to_region_block_pos, pix_to_abs_block_position_xy, abs_block_to_pixel_xy, reg_bl_to_abs_bl_position, pix_to_region_block_pos
from generalFunctions.generalFunctions import print_i


def closest_unoccupied_pos(swarm_reg, uav_pos_arr, sampler_pos=[0, 0]):
    """
    Returns [closest_abs_x_bl, closest_abs_y_bl]
    find the closest unoccupied block to the sampler in the same region
    sampler_pos default is [0, 0], which is the local region position
    """

    # loop over each block in the region
    # add any blocks to the dist array that don't already have a uav in that position

    dist_arr = []

    for y_bl in range(REGION_SIZE):
        for x_bl in range(REGION_SIZE):
            cur_abs_bl_pos = reg_bl_to_abs_bl_position(swarm_reg, [x_bl, y_bl])
            if cur_abs_bl_pos in uav_pos_arr:
                # already uav in this block, skip it...
                continue

            sam_local_pix_pos = abs_block_to_pixel_xy(sampler_pos)
            cur_bl_pix_pos = abs_block_to_pixel_xy([x_bl, y_bl])

            dist = math.dist(sam_local_pix_pos, cur_bl_pix_pos)
            dist_arr.append([dist, cur_abs_bl_pos[0], cur_abs_bl_pos[1]])

    # now return the closest (sort the dist array)
    if dist_arr:
        dist_arr.sort(key=lambda x: x[0])

        closest_abs_x_bl = dist_arr[0][1]
        closest_abs_y_bl = dist_arr[0][2]
        closest_abs_bl_pos = [closest_abs_x_bl, closest_abs_y_bl]
        return closest_abs_bl_pos

    print("Error in uav.closest_unoccupied_pos: no dist_arr")
    raise ValueError("No dist_arr, REGION_SIZE might be too small")


def init_uavs(num_swarms, num_uav_per_swarm):
    """
    Returns array of uav lists: [[x_pos, y_pos, z_pos, "state"], [x_pos, y_pos, z_pos, "state"], ...]

    need to cluster swarms like survivors
    followers need to be close to sampler...
    one sampler per region...
    if followers arent in closest block to sampler, then the block they're currently in appears assigned to all other uavs but the uav decides to move to a block that is closer to the sampler, resulting in a block that is not explored...
    """

    # create UAVs
    # create multiple "schools"/swarms

    if num_swarms > (GRID_SIZE**2):
        raise ValueError("NUM_UAV_SWARMS > (GRID_SIZE**2)")

    if MAX_NUM_UAV > TOTAL_BLOCKS:
        raise ValueError("MAX_NUM_UAV > TOTAL_BLOCKS")

    uav_arr = []
    uav_positions_arr = []  # [[x_abs_bl, y_abs_bl], ]
    swarm_reg = [0, 0]  # first swarm in [0, 0], increments row by row
    for swarm_num in range(num_swarms):
        if swarm_num > 0:
            if swarm_reg[0] >= (GRID_SIZE-1):
                swarm_reg[0] = 0
                if swarm_reg[1] >= (GRID_SIZE-1):
                    raise ValueError("Not enough regions for num swarms")
                else:
                    swarm_reg[1] += 1
            else:
                swarm_reg[0] += 1

        for uav_num in range(num_uav_per_swarm):
            if uav_num == 0:
                # first uav in each swarm must be a sampler
                state = "sampler"
            else:
                state = "follower"

            uav_abs_bl_pos = closest_unoccupied_pos(swarm_reg,
                                                    uav_positions_arr,
                                                    sampler_pos=[0, 0])
            uav_positions_arr.append(uav_abs_bl_pos)

            xy_pix_pos = abs_block_to_pixel_xy(uav_abs_bl_pos)

            uav = [xy_pix_pos[0], xy_pix_pos[1], UAV_MOVE_HEIGHT, state]

            uav_arr.append(uav)

    return uav_arr


class UavSelectBlock:

    def __init__(self, i, all_modes_arr, uav_pos_arr, grid_arr_obj):
        """ 
        Contains the methods to select a new block. 
        UavFishCore inherits from this class. 
        Seperate class so the prediction can use the same methods.
        """

        self.i = i
        self.all_modes_arr = all_modes_arr
        self.uav_pos_arr = uav_pos_arr
        self.grid_arr_obj = grid_arr_obj
        self.return_to_home = False

    def no_unassigned_block_or_mission_timeout(self):
        """
        Check if there are any unassigned blocks in the whole grid
        Check if mission has timed out
        """

        any_unassigned_block_in_grid = self.grid_arr_obj.any_unassigned_block_in_grid()

        if not any_unassigned_block_in_grid or self.mission_timeout():
            self.return_to_home = True
            return True

        return False

    def mission_timeout(self):
        """
        Returns True if mission has timed out
        """
        # TODO
        return False

    def select_nearest_block_towards_sampler(self, exc_bls=[]):
        """
        selects the nearest unassigned block in the region where there is a sampler

        update UAV position

        update region (and in tern block state)

        returns [abs_bl_x, abs_bl_y]
        returns False if there are no blocks close to sampler (no samplers or no unassigned blocks...)

        """

        # select the nearest unassigned block in this region (input argument)
        # maybe use absolute location?

        # checks if there is a sampler in the region
        # calculate distance to all blocks in the region (using abs locations)
        # make a list of all the block distances
        # sort list from low to high
        # loop over sorted list and the first block that has the state=unassigned is the nearest block

        # get uav abs position
        uav_pix_pos = self.uav_pos_arr[self.i][0:2]  # [x, y]

        sam_dist_arr = []

        # first find closest sampler
        for i, uav_state in enumerate(self.all_modes_arr):
            if uav_state == "sampler":
                sam_abs_pix_pos = self.uav_pos_arr[i][0:2]  # [x, y]
                sam_abs_bl_pos = pix_to_abs_block_position_xy(sam_abs_pix_pos)
                dist = math.dist(uav_pix_pos, sam_abs_pix_pos)
                reg_bl_pos = abs_to_region_block_pos(sam_abs_bl_pos)
                sam_reg = reg_bl_pos[0]
                sam_dist_arr.append([dist, sam_reg, sam_abs_bl_pos])

        # sort arr from low to high
        sam_dist_arr.sort(key=lambda x: x[0])

        for sam in sam_dist_arr:
            # select closest sampler
            sam_reg = sam[1]
            sam_abs_bl = sam[2]

            # use existing "select nearest block" method...
            bl_abs_bl_pos = self.select_nearest_block(sam_abs_bl,
                                                      sam_reg,
                                                      exc_bls)

            if not bl_abs_bl_pos == False:
                # this means we got a block, if it is false, look at next sampler
                return bl_abs_bl_pos  # returns [abs_bl_x, abs_bl_y]

        return False

    def get_abs_block_position(self):
        """returns [x_pos, y_pos] in BLOCKS, rounds off to the nearest block"""

        pix_pos = self.uav_pos_arr[self.i][:]

        # x direction
        bl_x = math.floor((pix_pos[0]) / (BLOCK_SIZE + BLOCK_MARGIN))

        # y direction
        bl_y = math.floor((pix_pos[1]) / (BLOCK_SIZE + BLOCK_MARGIN))

        return [bl_x, bl_y]

    def get_reg_bl_pos(self):
        """ returns: [[reg_x, reg_y], [block_x, block_y]] """
        return abs_to_region_block_pos(self.get_abs_block_position())

    def get_region_position(self):
        """ returns: [reg_x, reg_y] """
        return self.get_reg_bl_pos()[0]

    def select_nearest_highly_profitable_region(self, my_reg_pos):
        """
        # ? How is "highly profitable" defined ??

        find nearest region that:
        1. has a sampler...
        2. has unassigned blocks
        3. use cost function of profit and distance

        # TODO add function to work out best region based on distance AND profit...

        """

        # generate array of regions and sort by their profits

        PROFIT_WEIGHT = 0.3
        DISTANCE_WEIGHT = 0.7

        grid_arr = self.grid_arr_obj.get_grid_arr()

        sam_regions = []
        for i, mode in enumerate(self.all_modes_arr):
            if not i == self.i:
                if mode == "sampler":
                    # get the region and add it to the list...
                    sam_pix_pos = self.uav_pos_arr[i][0:2]  # just x, y
                    sam_reg = pix_to_region_block_pos(sam_pix_pos)[0]
                    sam_regions.append(sam_reg)

        # my_reg_pos = self.get_region_position()

        # print(f"sam_regions: {sam_regions}")

        dist_arr = []

        for row in grid_arr:
            for region in row:
                reg_pos = region.get_region_position()
                # exclude the region we are currently in
                if my_reg_pos == reg_pos:
                    continue

                # if region does not contain a sampler, look at next region...
                if not reg_pos in sam_regions:
                    continue

                # if region has no unassigned blocks, no point in continuing
                if not region.has_unassigned_block():
                    continue

                reg_profit = region.get_profit()

                # calculate distance
                dist = math.dist(my_reg_pos, reg_pos)
                # list stores distance as well as region position
                # For information: [[dist, [reg_x, reg_y]], []]

                # the bigger the profit the better -> thenlarger the reg_profit, the larger reg_profit/PROFIT_WEIGHT will be
                # the shorter the distance the better -> the smaller dist, the larger DISTANCE_WEIGHT/dist will be
                if dist == 0:
                    # shouldn't happen because we exclude the region we're currently in...
                    dist = 1

                eval_metric = reg_profit/PROFIT_WEIGHT + DISTANCE_WEIGHT/dist

                dist_arr.append([eval_metric, reg_pos])

        if not dist_arr:
            # false because there may be no regions with samplers
            # or no regions with samplers with unassigned blocks
            return False

        # sort array from low to high
        # https://stackoverflow.com/questions/4174941/how-to-sort-a-list-of-lists-by-a-specific-index-of-the-inner-list

        dist_arr.sort(key=lambda x: x[0], reverse=True)

        # closest region is the first element
        # return just the region, not the distance as well
        # For information: [[eval_metric, [reg_x, reg_y]], []]
        return dist_arr[0][1]

    def select_nearest_region(self, uav_abs_bl_pos):
        """
        select nearest unassigned region
        uav position gets updated in the next method (select_nearest_block)
        return the nearest unassigned region (location in the _grid_arr)

        searches by looking at the adjacent blocks (including diagonals)
        need to check if we are "out of range"
        # "max levels out" to search is GRID_SIZE-1   (if the uav is in the corner)

        """

        # uav_abs_bl_pos = self.get_abs_block_position()

        # uav_pos = self.get_region_position()
        # uav_x = uav_pos[0]
        # uav_y = uav_pos[1]

        uav_region = abs_to_region_block_pos(uav_abs_bl_pos)[0]
        uav_x = uav_region[0]
        uav_y = uav_region[1]

        # loop over _grid_arr (in the correct order of closest to furthest)
        # and store position of first element that is "unassigned"

        # create a list of possible search positions:
        search_pos_arr = []  # [level, region_x, region_y]
        unique_pos_arr = []  # this is to exclude duplicates
        for level in range(1, GRID_SIZE):
            # level = 1 is the first level out,
            # +-1 to current position

            start_x = uav_x - level
            start_y = uav_y - level

            end_x = uav_x + level
            end_y = uav_y + level

            for search_x in range(start_x, end_x+1):
                for search_y in range(start_y, end_y+1):

                    # now check if locations are valid
                    # first make sure they're >= 0
                    if search_x < 0 or search_y < 0:
                        continue

                    # then make sure they dont go out of range in the + direction
                    MAX_GRID_ARR_INDEX = GRID_SIZE-1
                    if search_x > MAX_GRID_ARR_INDEX or search_y > MAX_GRID_ARR_INDEX:
                        continue

                    # include level so next loop does level 1 first and so on
                    new_pos = [search_x, search_y]

                    if new_pos in unique_pos_arr:
                        continue

                    new_search_pos_arr = [level, new_pos[0], new_pos[1]]
                    search_pos_arr.append(new_search_pos_arr)
                    unique_pos_arr.append(new_pos)

        # sort search_pos_arr by level, lowest level first
        search_pos_arr.sort(key=lambda x: x[0])

        prev_level = search_pos_arr[0][0]

        # search each position in search_pos_arr until there is an unassigned region
        reg_bl_arr = []
        for search_pos in search_pos_arr:

            level = search_pos[0]
            search_x = search_pos[1]
            search_y = search_pos[2]

            # added this so it doesnt search every level if there is already an unassigned region
            # need to make sure we go through each region in the level though to find the closest block...
            if prev_level < level and len(reg_bl_arr) > 0:
                break

            prev_level = level

            reg_state = self.grid_arr_obj.get_grid_arr()[
                search_y][search_x].get_state()

            # faster to get block arr at same time even though we might not use it?
            bl_arr = self.grid_arr_obj.get_grid_arr()[
                search_y][search_x].get_block_arr()

            if not reg_state == "unassigned":
                continue

            # if we made it this far, region is unassigned...

            min_dist = ABS_GRID_SIZE*2
            for row in bl_arr:
                for block in row:
                    # loop over each block and find the distance from current position
                    # x,y block position (not pixels)
                    block_abs_bl_pos = block.get_abs_position()[0:2]
                    dist = math.dist(uav_abs_bl_pos, block_abs_bl_pos)
                    if min_dist > dist:
                        min_dist = dist

            # store distance to closest block, and region x and y block positions
            reg_info = [min_dist, search_x, search_y]
            reg_bl_arr.append(reg_info)

        # find region with closest block
        # sort array from low to high
        # https://stackoverflow.com/questions/4174941/how-to-sort-a-list-of-lists-by-a-specific-index-of-the-inner-list

        if reg_bl_arr:
            reg_bl_arr.sort(key=lambda x: x[0])

            # go to the region that is the closest
            return [reg_bl_arr[0][1], reg_bl_arr[0][2]]

        else:
            # no unassigned regions
            return []
            # raise ValueError("No regions to return")
            # print("Error in uav.UAV_fish.select_nearest_region")
            # return False

    def select_nearest_block(self, target_abs_bl_pos, target_region, exc_bls=[]):
        """
        Returns [abs_bl_x, abs_bl_y]

        target_abs_bl_pos -> [x, y] find the closest block to this target position. Either UAV current position (for sampler algorithm), or the sampler position (for follower algorithm)

        target_region     -> [x, y] region to look in

        select nearest unassigned block

        """

        # select the nearest unassigned block in this region (input argument)
        # maybe use absolute location?

        # calculate distance to all blocks in the region (using abs locations)
        # make a list of all the block distances
        # sort list from low to high
        # loop over sorted list and the first block that has the state=unassigned is the nearest block

        # get block array for region
        block_arr = self.grid_arr_obj.get_grid_arr(
        )[target_region[1]][target_region[0]].get_block_arr()

        dist_arr = []

        for row in block_arr:
            for block in row:

                # first see if block is unassigned
                if not block.get_state() == "unassigned":
                    continue

                # print(block.get_abs_position())

                if block.get_abs_position()[0:2] in exc_bls:
                    # block is in exclude_blocks list... skip
                    continue

                # use pix pos rather than abs block pos so diagonal blocks are penalised...
                # diag means uav has to change z to move height

                # get block abs position
                block_abs_bl_pos = block.get_abs_position()[0:2]  # just [x, y]
                block_px_pos = abs_block_to_pixel_xy(block_abs_bl_pos)

                target_px_pos = abs_block_to_pixel_xy(target_abs_bl_pos)

                dist = math.dist(target_px_pos, block_px_pos)

                # list stores distance as well as local position (to find block again, this is the return value)
                # For information: [[dist, [local_x, local_y]], []]
                dist_arr.append([dist,
                                 block_abs_bl_pos[0],
                                 block_abs_bl_pos[1]])

        # sort array from low to high
        # https://stackoverflow.com/questions/4174941/how-to-sort-a-list-of-lists-by-a-specific-index-of-the-inner-list

        # print_i(4, self.i, f"dist_arr: {dist_arr}")

        if dist_arr:

            dist_arr.sort(key=lambda x: x[0])

            # loop over new sorted array and return first block that is "unassigned"
            for bl in dist_arr:
                # get local block location [[dist, abs_x, abs_y], []]
                abs_bl_x = bl[1]
                abs_bl_y = bl[2]

                reg_bl_pos = abs_to_region_block_pos([abs_bl_x, abs_bl_y])
                bl_pos = reg_bl_pos[1]
                # get state of block at this location
                bl_state = block_arr[bl_pos[1]][bl_pos[0]].get_state()
                # check if state is "unassigned"
                if bl_state == "unassigned":
                    return [abs_bl_x, abs_bl_y]

        return False


class UavFishCore(UavSelectBlock):
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
                 all_modes_arr,  # original this is set, implicit this is deduced from grid_arr
                 surv_log_arr,
                 explored_block_log_arr,
                 sampler_alg_pos_start,
                 follower_alg_pos_start,
                 set_mode_method):  # set_mode is different for implicit and original
        """
        position:    BlockPosition object
        state:       follower or sampler
        desired_pos: Position where the uav will move to on each iteration update
        memory:      used in controlling the memorability of a sampler by its followers given the profitability of its region (memory is a percentage, 100 = 100%)
        forgetting_rate: controls the memory size of followers.
        """

        super().__init__(i, all_modes_arr, uav_pos_arr, grid_arr_obj)

        self.uav_fish_log_arr = uav_fish_log_arr
        self.uav_fish_ex_bl_arr = uav_fish_ex_bl_arr
        self.state = "search"  # search, rescue
        self.target_px_pos = uav_pos_arr[i][0:3]
        self.speed_xy = BLOCK_SIZE/5  # "pixels" / iteration
        self.speed_z = 1  # "meters" / iteration
        # self.i = i
        self.iter_count = iter_count
        # self.uav_pos_arr = uav_pos_arr
        self.surv_arr = surv_arr
        self.rescue_state = None
        self.rescue_index = None
        self.search_state = 1
        self.delay_iterations_count = 0
        self.delay_iterations_set = 0
        self.surv_log_arr = surv_log_arr
        self.over_target_block_history = []
        # keep track of all assigned blocks so we dont keep setting the same block to assigned at the end of the algorithm
        self.ass_blocks = []
        # self.return_to_home = False  # used in child classes

        self.mode = uav_init_mode  # sampler, follower
        self.state = "search"  # search, rescue
        self.memory = 100
        self.forgetting_rate = None
        self.generate_forgetting_rate()  # this sets the forgetting rate...

        # if the mode was set to sampler after the intial mode of being a follower, the algorithm must start at 1 to make sure that the uav selects an unassigned region. The reason the default is 2 i
        self.sampler_alg_pos = sampler_alg_pos_start[self.mode]
        self.follower_alg_pos = follower_alg_pos_start[self.mode]

        self.target_px_pos = uav_pos_arr[i][0:3]
        self.speed_xy = BLOCK_SIZE/5  # "pixels" / iteration
        self.speed_z = 1  # "meters" / iteration
        self.i = i
        # self.grid_arr_obj = grid_arr_obj
        self.uav_pos_arr = uav_pos_arr
        # self.all_modes_arr = all_modes_arr
        self.rescue_state = None
        self.rescue_index = None
        self.search_state = 1
        self.delay_iterations_count = 0
        self.delay_iterations_set = 0
        # self.return_to_home = False
        self.set_mode = set_mode_method
        # used in first_time_uav_over_target_block
        self.over_target_block_history = []
        # keep track of all assigned blocks so we dont keep setting the same block to assigned at the end of the algorithm
        self.ass_blocks = []
        self.explored_block_log_arr = explored_block_log_arr

    def set_block_state(self, state, region, local_pos):
        """Updates the block state in the self.grid_arr"""
        self.grid_arr_obj.update_block_state(state, region, local_pos)

        bl_abs_pos = reg_bl_to_abs_bl_position(region, local_pos)
        # [iteration_number, uav_num,  abs_bl_pos_x,  abs_bl_pos_y, state]
        self.explored_block_log_arr.append([self.iter_count[0],
                                            self.i,
                                            bl_abs_pos[0],
                                            bl_abs_pos[1],
                                            state])

    # def no_unassigned_block_or_mission_timeout(self):
    #     """
    #     Check if there are any unassigned blocks in the whole grid
    #     Check if mission has timed out
    #     """

    #     any_unassigned_block_in_grid = self.grid_arr_obj.any_unassigned_block_in_grid()

    #     if not any_unassigned_block_in_grid or self.mission_timeout():
    #         self.return_to_home = True
    #         return True

    #     return False

    def get_mode_height(self):
        """ returns the desired height for the current uav mode (sampler, follower) """
        if self.mode == "sampler":
            return UAV_SAMPLER_HEIGHT
        elif self.mode == "follower":
            return UAV_FOLLOWER_HEIGHT

        print("Error in uav.UAV_fish.get_mode_height")
        return 0

    def get_uav_state(self):
        return self.state

    def set_target_mode_height(self):
        """ set the target height to the current mode (sampler or follower height) 
        Used in "UavImplicitContainer.iterate_uav"
        """

        if self.mode == "follower":
            height = UAV_FOLLOWER_HEIGHT
        elif self.mode == "sampler":
            height = UAV_SAMPLER_HEIGHT
        else:
            print("Error in uav.UAV_fish.set_target_mode_height")

        self.update_target_position(z_abs_pix_pos=height)

    def set_state(self, state):
        """ sets the uav state (search or rescue) """
        self.state = state

    def set_memory_100(self):
        """ Reset memory to 100% (value of 100) """
        self.memory = 100

    def generate_forgetting_rate(self):
        """ Randomly generate forgetting rate between 10-20% (values of 10-20) """
        self.forgetting_rate = random.randint(10, 20)
        # self.forgetting_rate = random.randint(1, 5)

    def decrease_forgetting_rate(self):
        """Decrease the forgetting rate
        # ? By how much ??
        """
        # self.forgetting_rate -= 5
        f_rate = self.forgetting_rate - 1
        if f_rate < 1:
            self.forgetting_rate = 1
        else:
            self.forgetting_rate = f_rate

    def increase_forgetting_rate(self):
        """Increase the forgetting rate
        # ? By how much ??
        """
        self.forgetting_rate += 1

    def decrease_memory(self):
        """Decrease the memory
        # ? By how much ?? --> the forgetting rate??
        """
        self.memory -= self.forgetting_rate

    def fish_alg_loop(self, sampler_algorithm_start, follower_algorithm_start, target_changed, after_loop_method):
        """
        """

        if self.at_target_position(target_changed):
            if self.state == "search":
                if self.return_to_home == False:
                    if self.mode == "sampler":
                        sampler_algorithm_start()
                    elif self.mode == "follower":
                        follower_algorithm_start()
                    else:
                        print("Error in uav.UAV_fish.fish_alg_loop: mode")
            elif self.state == "rescue":
                self.rescue_survivor()
            else:
                print("Error in uav.UAV_fish.fish_alg_loop: state")
        else:
            self.move()

        if after_loop_method:
            after_loop_method()

    # def mission_timeout(self):
    #     """
    #     Returns True if mission has timed out
    #     """
    #     # TODO
    #     return False

    def delay_iterations(self, num_iter):
        """use the event_obj to wait (delay) number of iterations
        Returns True for still in delay mode, False if delay is over
        """

        if self.delay_iterations_set > 0:
            self.delay_iterations_count += 1
            if self.delay_iterations_count >= self.delay_iterations_set:
                self.delay_iterations_set = 0
                self.delay_iterations_count = 0
                return False  # false for delay over
        else:
            # new delay starting...
            self.delay_iterations_set = num_iter
            self.delay_iterations_count = 1  # this is iteration 1

        return True  # true for still in "delay"

    def at_target_position_z(self):
        """Return True if target_px_pos[2] == uav_pos_arr[i][2]  (only z direction)"""

        if self.target_px_pos[2] == self.uav_pos_arr[self.i][2]:
            return True

        return False

    def at_target_position_xy(self):
        """Return True if target_px_pos[0:1] == uav_pos_arr[i][0:2]  (only x, y directions)"""

        if self.target_px_pos[0:2] == self.uav_pos_arr[self.i][0:2]:
            return True

        return False

    def set_current_block_state(self, state):
        """sets the current block state"""

        pix_pos_xy = self.uav_pos_arr[self.i][0:2]
        abs_bl_pos = pix_to_abs_block_position_xy(pix_pos_xy)

        if state == "assigned":
            if abs_bl_pos in self.ass_blocks:
                # already set to assigned, return
                return

            self.ass_blocks.append(abs_bl_pos)

        reg_bl_pos = abs_to_region_block_pos(abs_bl_pos)

        self.set_block_state(state, reg_bl_pos[0], reg_bl_pos[1])

    def first_time_uav_over_target_block(self):
        """ checks if the uav is over the target block (only once will return FALSE if it has returned True for the block already)
        Returns True if uav is somewhere over the target block
        """

        tar_abs_bl_pos = pix_to_abs_block_position_xy(self.target_px_pos)

        uav_px_pos_xy = self.uav_pos_arr[self.i][0:2]
        uav_abs_bl_pos = pix_to_abs_block_position_xy(uav_px_pos_xy)

        if uav_abs_bl_pos == tar_abs_bl_pos:
            if tar_abs_bl_pos in self.over_target_block_history:
                # not the first time the UAV is over this target block
                return False

            # add target block pos to array so this method returns FALSE next iteration for the same block
            self.over_target_block_history.append(tar_abs_bl_pos)
            return True

        return False

    def at_target_position(self, target_changed=None):
        """
        returns True if uav_pos_arr[self.i] == target_px_pos[self.i]
         (for x, y, and z)
        """

        # target_changed might = None if this is dqn
        if target_changed:
            # # only check if target has changed if fish is implicit, original doesn't need that check
            if target_changed():
                # obviously not at target position because it changed and we haven't moved yet
                return False

        if self.at_target_position_xy() and self.at_target_position_z():
            return True

        return False

    def move_z(self):
        """move one step closer to target_px_pos

        unit? -> pixels... +1 pixel per time
        speed:
        """

        # TODO eventually we need to improve the state predictor in the grid_arr algorithm so we dont just jump z...

        if JUMP_Z_MOVE == True:
            # update only z position
            self.uav_pos_arr[self.i][2] = self.target_px_pos[2]

        else:
            iterations_passed = 1
            max_poss_dist_moved = self.speed_z * iterations_passed
            # current z position in pixels
            current_z_pos = self.uav_pos_arr[self.i][2]
            total_dist_to_move = self.target_px_pos[2] - current_z_pos
            # check if we would go past our target
            if abs(max_poss_dist_moved) > abs(total_dist_to_move):
                updated_z_pos = self.target_px_pos[2]

            else:
                # else just move closer... which direction?
                if current_z_pos < self.target_px_pos[2]:
                    # need to add
                    updated_z_pos = current_z_pos + max_poss_dist_moved
                else:
                    # need to subtract
                    updated_z_pos = current_z_pos - max_poss_dist_moved

            # update only z position
            self.uav_pos_arr[self.i][2] = updated_z_pos

    def is_bl_adjacent(self, current_bl, check_bl):
        """check if the block is adjacent EXCLUDING diag... ?"""

        cur_x = current_bl[0]
        cur_y = current_bl[1]

        adj_blocks_arr = []

        adj_blocks_arr.append([cur_x, cur_y])  # include current position...
        adj_blocks_arr.append([cur_x, cur_y + 1])
        adj_blocks_arr.append([cur_x + 1, cur_y])
        adj_blocks_arr.append([cur_x, cur_y - 1])
        adj_blocks_arr.append([cur_x - 1, cur_y])

        if check_bl in adj_blocks_arr:
            return True

        return False

    def pause_rand_iterations(self):
        """ pause the movement for a random number of iterations...
        Returns True for still in delay mode, False if delay is over
        """

        max_iters = 10
        min_iters = 1

        num_iter = random.randint(min_iters, max_iters)

        still_in_delay = self.delay_iterations(num_iter)

        return still_in_delay

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

    def run_dispersion(self):
        """ If there is another uav in the block, pause for a random time, then slect a new block
        Returns True for still in delay mode, False if delay is over
        """

        if self.other_uav_in_block():
            if self.pause_rand_iterations():
                return True

        return False

    def move_xy(self):
        """move one step closer to target_px_pos

        unit? -> pixels... +1 pixel per time
        speed:
        """

        iterations_passed = 1
        max_poss_dist_moved = self.speed_xy * iterations_passed

        # current position in pixels
        current_pos = self.uav_pos_arr[self.i][0:3]

        cur_bl = pix_to_abs_block_position_xy(current_pos[0:2])
        tar_bl = pix_to_abs_block_position_xy(self.target_px_pos[0:2])
        move_adjacent_block = self.is_bl_adjacent(cur_bl, tar_bl)

        if not move_adjacent_block:
            if not current_pos[2] == UAV_MOVE_HEIGHT:
                if not self.target_px_pos[2] == UAV_MOVE_HEIGHT:
                    self.update_target_position(z_abs_pix_pos=UAV_MOVE_HEIGHT)

                # return, only move xy if we are at move height and we're not moving to adjacent block
                return

        updated_pos = current_pos  # default if nothing changes

        # loop for x and y direction (NOT z)
        for d in range(2):
            total_dist_to_move = self.target_px_pos[d] - current_pos[d]
            # check if we would go past our target
            if abs(max_poss_dist_moved) > abs(total_dist_to_move):
                updated_pos[d] = self.target_px_pos[d]
            else:
                # else just move closer... which direction?
                if current_pos[d] < self.target_px_pos[d]:
                    # need to add
                    updated_pos[d] = current_pos[d] + max_poss_dist_moved
                else:
                    # need to subtract
                    updated_pos[d] = current_pos[d] - max_poss_dist_moved

        # assign updated pos to uav_pos_arr
        for a in range(2):
            self.uav_pos_arr[self.i][a] = updated_pos[a]

    def move(self):
        """ move one step closer to target position """

        # first make sure we are at target z...
        if not self.at_target_position_z():
            self.move_z()
            return

        if not self.at_target_position_xy():
            self.move_xy()

        # ["time_ms", "type", "uav_num", "pos_x", "pos_y", "pos_z", "state"]
        self.uav_fish_log_arr.append([time.time(),
                                      "uav",  # type
                                      self.i,
                                      self.uav_pos_arr[self.i][0],
                                      self.uav_pos_arr[self.i][1],
                                      self.uav_pos_arr[self.i][2],
                                      self.state])

    def update_target_position(self, x_abs_bl_pos=None, y_abs_bl_pos=None, z_abs_pix_pos=None):
        """updates the local "target" position (target_px_pos)
        Sets pixel to center of block (actual block, not display block) EXCEPT for z
        """

        # print(
        #     f"update target position: {x_abs_bl_pos}, {y_abs_bl_pos}, {z_abs_pix_pos}")

        if not x_abs_bl_pos == None:
            self.target_px_pos[0] = x_abs_bl_pos * BLOCK_SIZE + BLOCK_SIZE/2

        if not y_abs_bl_pos == None:
            self.target_px_pos[1] = y_abs_bl_pos * BLOCK_SIZE + BLOCK_SIZE/2

        if not z_abs_pix_pos == None:
            self.target_px_pos[2] = z_abs_pix_pos  # no "BLOCK_SIZE" for z

    def set_state(self, state):
        """ sets the uav state (search or rescue) """
        self.state = state

    def survivor_alive(self, surv_info):
        """ checks if the survivor lifespan is greater than the number of iterations passed
            -> if so, survivor is alive

            surv_info -> [x_abs_bl, y_abs_bl, state, lifespan]
        """

        lifespan = surv_info[3]
        if lifespan > self.iter_count[0]:
            return True

        return False

    def rescue_survivor(self):

        if self.rescue_state == 1:
            self.update_target_position(z_abs_pix_pos=UAV_RESCUE_HEIGHT)
            self.rescue_state = 2
            return  # so we can move to the new position...

        if self.rescue_state == 2:
            # [x_abs_bl, y_abs_bl, state, lifespan]
            surv_info = self.surv_arr[self.rescue_index][:]
            if self.survivor_alive(surv_info):
                # set survivor state to "rescued"
                surv_state = "rescued"
            else:
                # set survivor state to "deceased"
                surv_state = "deceased"

            self.surv_arr[self.rescue_index][2] = surv_state

            # surv info: [x, y, surv_state, lifespan]
            # "iteration_number", "survivor_number", "pos_x", "pos_y", "state", "lifespan"
            self.surv_log_arr.append([self.iter_count[0],
                                      self.rescue_index,
                                      surv_info[0],
                                      surv_info[1],
                                      surv_state,
                                      surv_info[3]])

            self.rescue_state = 3
            return

        if self.rescue_state == 3:
            # wait a bit so grid_arr checks the height
            if self.delay_iterations(20) == False:
                # delay mode is over, move to next "rescue_state"
                self.rescue_state = 4
            return  # rescue still in progress

        if self.rescue_state == 4:
            # go back to original height (sampler or follower)
            self.update_target_position(z_abs_pix_pos=self.get_mode_height())
            self.rescue_state = 5
            return  # so we can move to the new position...

        if self.rescue_state == 5:
            # change z...
            if self.at_target_position_z():
                self.rescue_state = None  # finished rescuing...
                self.rescue_index = None
                self.set_state("search")
                return  # rescue complete
            else:
                return  # rescue still in progress

    def any_survivors_if_so_then_rescue(self):
        """
        Search the current block for survivors
        return  None if still in delay (searching),
                True if there are survivors,
                False if no survivors
        """

        surv_found = None  # None means still searching...

        # this is used to know if the uav is searching or not
        if self.search_state == 0:
            self.search_state = 1

        if self.search_state == 1:
            # delay when searching....
            if self.delay_iterations(10) == False:
                # delay mode is over, move to next "search_state"
                self.search_state = 2

        # before condition for logging...
        uav_abs_bl_pos = self.get_abs_block_position()

        if self.search_state == 2:
            # search as normal...
            self.search_state = 0  # for next time
            surv_found = False

            for index, surv in enumerate(self.surv_arr):
                if surv[0:2] == uav_abs_bl_pos and surv[2] == "undiscovered":
                    # we know there is a surv at this position and the state is "undiscovered"
                    # rescue survivor
                    self.rescue_state = 1
                    self.rescue_index = index
                    self.set_state("rescue")
                    surv_found = True
                    break

        # info: ["time_s", "block_abs_x", "block_abs_y", "survivor_in_block"]
        self.uav_fish_ex_bl_arr.append([self.iter_count,
                                        uav_abs_bl_pos[0],
                                        uav_abs_bl_pos[1],
                                        surv_found])  # only if surv_found == False did we actually look

        return surv_found
