
from constants.sim_config import *

# good looking sim: Region: 4, Grid: 4, uav_swarm: 4, uav_per_swarm: 5, surv: 45

JUMP_Z_MOVE = True


MAX_NUM_UAV = UAV_NUMS[-1][0]*UAV_NUMS[-1][1]  # max num uav
TOTAL_REGION_BLOCKS = REGION_SIZE*REGION_SIZE
TOTAL_BLOCKS = (REGION_SIZE*REGION_SIZE)*(GRID_SIZE*GRID_SIZE)

LOG_PATH = "./logs"


# GRID detection settings...
# number of previous states that must be the same (for list)
NUM_SAME_STATES = 3

# create grid (array of regions)
GRID_SHAPE = (GRID_SIZE, GRID_SIZE)
# sor survivor array
ABS_GRID_SHAPE = (GRID_SIZE*REGION_SIZE, GRID_SIZE*REGION_SIZE)
ABS_GRID_SIZE = GRID_SIZE*REGION_SIZE


# GUI spacing
ROW_SPACE_BLOCK = 65  # space between rows (vertical)
COL_SPACE_BLOCK = 100  # space between columns (horizontal)
ROW_SPACE_REG = ROW_SPACE_BLOCK*REGION_SIZE  # space between rows (vertical)
# space between columns (horizontal)
COL_SPACE_REG = COL_SPACE_BLOCK*REGION_SIZE
MARGIN = 25
REGION_INFO_SPACE = 30  # top of each region for information


BLOCK_SIZE = 60  # 60
BLOCK_MARGIN = 1

ABS_PIX = ABS_GRID_SIZE*BLOCK_SIZE

# Fonts
GRID_FONT_SIZE = 16
SURV_FONT_SIZE = 14
PROFIT_FONT_SIZE = 10
UAV_FONT_SIZE = 10
REG_FONT_SIZE = 13
STATUS_FONT_SIZE = 14

UAV_START_FINISH_POS = [-10, -10, 0]


# GUI window
BLOCK_SPACE = BLOCK_SIZE+BLOCK_MARGIN
REGION_SPACE_WIDTH = BLOCK_SIZE*REGION_SIZE + BLOCK_MARGIN*(REGION_SIZE-1)
REGION_SPACE_HEIGHT = BLOCK_SIZE*REGION_SIZE + \
    BLOCK_MARGIN*(REGION_SIZE-1) + REGION_INFO_SPACE


DISPLAY_INFO_WIDTH = 400

UAV_HEIGHT_WIDTH = 15
UAV_HEIGHT_SPACE = 3
UAV_HEIGHTS_WIDTH = MAX_NUM_UAV * \
    (UAV_HEIGHT_WIDTH + UAV_HEIGHT_SPACE) + MARGIN

add_width = max(DISPLAY_INFO_WIDTH, UAV_HEIGHTS_WIDTH)

WIN_WIDTH = BLOCK_SPACE*REGION_SIZE*GRID_SIZE + MARGIN*2 + add_width
WIN_HEIGHT = (BLOCK_SPACE*REGION_SIZE+REGION_INFO_SPACE)*GRID_SIZE + MARGIN*2

FPS = 60
PLAY_FPS = 10

PLAY_BTN_SIZE = 30
PLAY_BTN_X = WIN_WIDTH - PLAY_BTN_SIZE - 5
PLAY_BTN_Y = WIN_HEIGHT - PLAY_BTN_SIZE - 5
PLAY_BTN_POS = [PLAY_BTN_X, PLAY_BTN_Y]

# colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
DEEP_SKY_BLUE = (0, 191, 255)
LIGHT_BLUE = (153, 255, 255)
LIGHT_BLUE_REG = (183, 225, 225)
ORANGE = (255, 128, 0)
LIGHT_ORANGE = (255, 213, 128)
LIGHT_RED = (255, 153, 153)
TEAL = (0, 128, 128)  # "assigned" colour
LIGHT_SEA_GREEN = (32, 178, 170)
GREY = (128, 128, 128)  # "explored" colour
DARK_GREY = (50, 50, 50)  # "deceased" colour
GAINSBORO = (220, 220, 220)
SILVER = (192, 192, 192)
MAGENTA = (255, 0, 255)


# unit for these is pixels (or meters... etc)
UAV_RESCUE_HEIGHT = 10  # if UAV z is < 10m then it is "rescuing"
# if UAV_RESCUE_HEIGHT <= (UAV z) < UAV_SAMPLER_HEIGHT then it is "sampler"
UAV_SAMPLER_HEIGHT = 20
UAV_FOLLOWER_HEIGHT = 30
# at this height the update_grid_arr wont set the block to assigned...
UAV_MOVE_HEIGHT = 40

UAV_DQN_HEIGHT = 25
