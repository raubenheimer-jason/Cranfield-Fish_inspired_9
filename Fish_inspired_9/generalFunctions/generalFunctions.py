
from constants.constants import *


def is_valid_region(region):
    """returns True if the region is valid (within range)"""

    if not type(region) is list:
        return False

    # if home:
    #     if not region == [-1, -1]:
    #         return False

    for reg in region:
        # reg is x or y value of region list

        # if reg < 0:
        #     return False

        if reg < -1:
            # -1 is valid because that is "home"
            return False

        if reg >= GRID_SIZE:
            # e.g. GRID_SIZE = 4, then region range is 0 to 3 (inclusive), therefore if reg == 4 then return False
            return False

    return True


def is_valid_abs_block(bl):
    """ check if the abs bl (bl) is on the grid """

    if not type(bl) is list:
        return False

    for a in bl:
        # a is x or y axis of bl list

        if a < 0:
            return False

        if a >= ABS_GRID_SIZE:
            return False

    return True


def print_i(expected_i, i, msg):
    """ only prints the message if i is in expected_i
    expected_i can be a single int or a list
    """

    # """ only prints the message if expected_i == i """

    if type(expected_i) is not list:
        expected_i = [expected_i]

    if i in expected_i:
        print(f"{i}\t{msg}")


def uav_height_equal(uav_height, test_height, precision=1):
    """checks the uav height against the test height (can add a tolerance etc here...)"""

    if round(uav_height, precision) == round(test_height, precision):  # TODO have some range
        return True

    return False
