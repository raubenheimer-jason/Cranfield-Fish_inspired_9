import math
from constants.constants import *


def reg_bl_to_abs_bl_position(region, block):
    """Return absolute position (in BLOCKS) (basically ignoring regions, how big is the area in terms of a x a blocks)
    Returns: [x_abs_pos, y_abs_pos]
    """
    # ((number of regions accross/down) * (number of blocks in a region)) + (local number of blocks accross/down)
    x_abs_pos = (region[0] * REGION_SIZE) + block[0]
    y_abs_pos = (region[1] * REGION_SIZE) + block[1]

    return [x_abs_pos, y_abs_pos]


def abs_to_region_block_pos(abs_bl_pos):
    """converts absolute block position to region and block position
    ONLY xy direction...
    return [[reg_x, reg_y], [bl_x, bl_y]]
    return (region, block)
    """

    if abs_bl_pos == [None, None, None]:
        return [[-1, -1], [-1, -1]]

    if abs_bl_pos[0] < 0 or abs_bl_pos[1] < 0:
        return [[-1, -1], [-1, -1]]

    abs_x = abs_bl_pos[0]
    abs_y = abs_bl_pos[1]

    reg_x = abs_x // REGION_SIZE
    reg_y = abs_y // REGION_SIZE

    bl_x = abs_x - reg_x*REGION_SIZE
    bl_y = abs_y - reg_y*REGION_SIZE

    return [[reg_x, reg_y], [bl_x, bl_y]]


def pix_to_abs_block_position_xy(pix_pos):
    """returns [x_pos, y_pos] in BLOCKS, rounds off to the nearest block
    pix_pos is [x, y] in PIXELS  -> uav_pos_arr NO MARGIN
    """

    # need to factor in margins... MARGIN and REGION_INFO_SPACE

    # UAV pixel location must not consider margins... no margins in real life...
    # BUT display must consider margins...
    # this way the unit pixels can be converted to meters etc...

    local_pix_pos = pix_pos[:]

    # x direction
    bl_x = math.floor((local_pix_pos[0]) / BLOCK_SIZE)

    # y direction
    bl_y = math.floor((local_pix_pos[1]) / BLOCK_SIZE)

    return [bl_x, bl_y]


def pix_to_region_block_pos(pix_pos_xy):
    """ Converts the pix position [x, y] to the region and block position 
    Returns [[reg_x, reg_y], [bl_x, bl_y]]
    """

    abs_bl_pos = pix_to_abs_block_position_xy(pix_pos_xy)
    reg_bl_pos = abs_to_region_block_pos(abs_bl_pos)
    return reg_bl_pos  # [[reg_x, reg_y], [bl_x, bl_y]]


def pix_to_pix_display_position(pix_pos):
    """returns [x_pos, y_pos, z_pos] in PIXELS for display, factors in the margins
    pix_pos is [x, y, z] in PIXELS  -> uav_pos_arr
    """

    # need to factor in margins... MARGIN and REGION_INFO_SPACE

    # UAV pixel location must not consider margins... no margins in real life...
    # BUT display must consider margins...
    # this way the unit pixels can be converted to meters etc...

    local_pix_pos = pix_pos[:]

    # x direction
    # MARGIN and BLOCK_MARGIN
    # how many blocks assuming no BLOCK_MARGIN
    num_bl_x = math.floor(local_pix_pos[0] / BLOCK_SIZE)
    # add MARGIN and BLOCK_MARGIN*num_blocks
    disp_pixel_x = local_pix_pos[0] + MARGIN + num_bl_x*BLOCK_MARGIN

    # y direction
    num_bl_y = math.floor(local_pix_pos[1] / BLOCK_SIZE)
    num_reg_y = math.floor(num_bl_y / REGION_SIZE)

    # add MARGIN and BLOCK_MARGIN*num_blocks and REGION_INFO_SPACE*num_regions
    disp_pixel_y = local_pix_pos[1] + MARGIN + \
        (num_bl_y+1)*BLOCK_MARGIN + (num_reg_y+1)*REGION_INFO_SPACE

    if len(pix_pos) == 3:
        # z direction
        # assume no margins...
        disp_pixel_z = local_pix_pos[2]

        return [disp_pixel_x, disp_pixel_y, disp_pixel_z]

    # else just return x and y
    return [disp_pixel_x, disp_pixel_y]


def abs_block_to_pixel_xy(block_pos):
    """convert block position (absolute) to pixel position (excluding margins, raw pixel position)
    block_pos = [block_x, bloxk_y]
    Returns [pix_x, pix_y] in CENTER of block
    """

    pix_x = block_pos[0] * BLOCK_SIZE + BLOCK_SIZE/2
    pix_y = block_pos[1] * BLOCK_SIZE + BLOCK_SIZE/2

    pix_pos = [pix_x, pix_y]

    return pix_pos
