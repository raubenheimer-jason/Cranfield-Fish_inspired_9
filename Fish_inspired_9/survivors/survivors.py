import numpy as np
from constants.sim_config import *
from constants.constants import *
from random import randint


def init_survivors(num_surv):
    """
    Returns 2D array same shape as grid (absolute), holds state at each position. None if no survivor

    First generates a 2D array that has the same structure as the grid (abs positions)
    If survivors[y_pos][x_pos] == None, then no survivor at that location
    """
    surv_arr = np.empty(shape=ABS_GRID_SHAPE, dtype=object)

    # create Survivors
    # need to be at random unique locations
    # need to create "hot spots"
    num_hot_spots = num_surv // REGION_SIZE
    if num_hot_spots < 1:
        num_hot_spots = 1

    abs_max = GRID_SIZE*REGION_SIZE-1

    hot_spot_pos_arr = []

    for i in range(num_hot_spots):
        hot_spot_pos_arr.append([randint(0, abs_max), randint(0, abs_max)])

    surv_per_hot = num_surv//num_hot_spots
    pos_arr_index = 0
    for i in range(1, num_surv+1):

        # find closest block to current position that doesnt have a survivor in it

        pos = hot_spot_pos_arr[pos_arr_index-1]
        n_abs_pos = nearest_unoccupied_pos(pos, surv_arr)
        x_pos = n_abs_pos[0]
        y_pos = n_abs_pos[1]

        lifespan = randint(SURV_LIFESPAN_RANGE[0], SURV_LIFESPAN_RANGE[1])

        surv_arr[y_pos][x_pos] = ["undiscovered", lifespan]

        if i % surv_per_hot == 0:
            pos_arr_index += 1

    return get_sur_1d_arr(surv_arr)


def get_sur_1d_arr(sur_2d_arr):
    """returns 1D array only with survivor [x, y] positions
    x and y are abs block positions
    """
    surv_1d_arr = []
    for y, row in enumerate(sur_2d_arr):
        for x, surv_info in enumerate(row):
            if surv_info == None:
                # Only include if there is a survivor in that block
                continue
            surv_state = surv_info[0]
            lifespan = surv_info[1]
            # add x, y position, state, and lifespan
            surv_1d_arr.append([x, y, surv_state, lifespan])
    return surv_1d_arr


def nearest_unoccupied_pos(pos, surv_arr):
    """
    Find the closest block that doesnt have a survivor in it
     -> All absolute positions

    surv_arr = 2D np array same shame as (abs) grid...
    """

    #! DOESNT ACTUALLY DO NEAREST BLOCK..... NEED TO SEARCH ALL LEVEL 1 BEFORE GOING TO LEVEL 2 ...
    #! Add numbers to survivors and you'll see...
    #! also problem for other "nearest block" methods ????

    for level in range(1, GRID_SIZE*REGION_SIZE+1):
        # level = 1 is the first level out,
        # +-1 to current position

        for x in range(-level, level):
            for y in range(-level, level):
                search_x = pos[0]+x
                search_y = pos[1]+y

                # now check if locations are valid
                # first make sure they're >= 0
                if search_x < 0 or search_y < 0:
                    continue

                # then make sure they dont go out of range in the + direction
                MAX_ARR_INDEX = GRID_SIZE*REGION_SIZE-1
                if search_x > MAX_ARR_INDEX or search_y > MAX_ARR_INDEX:
                    continue

                # if we made it here the indexes are valid
                # see if survivor is in block
                if surv_arr[search_y][search_x] == None:
                    # if None at that position then no survivor there, return pos
                    return [search_x, search_y]

                else:
                    continue  # else try next pos

    return False  # No blocks available?
