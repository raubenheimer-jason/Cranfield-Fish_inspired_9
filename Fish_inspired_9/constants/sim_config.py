
from constants.sim_config_functions import check_sim_config

SIM_CONFIG = {"short_sim": False,
              "long_sim": True,
              "mega_sim": False}

check_sim_config(SIM_CONFIG)

# PREDICTION = True

if SIM_CONFIG["short_sim"] == True:

    SIMULATIONS = {"original": False,
                   "implicit": False,
                   "implicit_prediction": False}

    SHOW_SIMULATION = True

    PLAY_INITIAL_VAL = False

    # simulations per configuration
    NUM_SIMULATIONS = 1

    # (NUM_SWARMS, NUM_UAV_PER_SWARM)
    # UAV_NUMS = ((1, 1),
    #             (2, 2),)
    # UAV_NUMS = ((1, 2), (2, 3),)
    UAV_NUMS = ((2, 4),)
    # UAV_NUMS = ((2, 4), )

    REGION_SIZE = 3  # smaller 'grid' within the larger area (a x a area)
    GRID_SIZE = 4  # each block in the grid represents a region (b x b area)

    # SURV_NUMS = (10, 20)
    SURV_NUMS = (20, )

    TIMEOUT_ITERATIONS = 1000

    SURV_LIFESPAN_RANGE = (1, TIMEOUT_ITERATIONS)  # (min, max) iterations

    LOG_SIM = False


elif SIM_CONFIG["long_sim"] == True:

    SIMULATIONS = {"original": True,
                   "implicit": True,
                   "implicit_prediction": False}

    SHOW_SIMULATION = False

    PLAY_INITIAL_VAL = True

    # simulations per configuration
    NUM_SIMULATIONS = 15

    # (NUM_SWARMS, NUM_UAV_PER_SWARM)
    UAV_NUMS = ((1, 4),     # 4
                (2, 4),     # 8
                (4, 4),     # 16
                (4, 8),     # 32
                (8, 8))     # 64

    REGION_SIZE = 4  # smaller 'grid' within the larger area (a x a area)
    GRID_SIZE = 5  # each block in the grid represents a region (b x b area)

    SURV_NUMS = (4, 32, 128)

    TIMEOUT_ITERATIONS = 550

    SURV_LIFESPAN_RANGE = (100, TIMEOUT_ITERATIONS)  # (min, max) iterations

    LOG_SIM = True

elif SIM_CONFIG["mega_sim"] == True:

    SIMULATIONS = {"original": False,
                   "implicit": False,
                   "implicit_prediction": False}

    SHOW_SIMULATION = False

    PLAY_INITIAL_VAL = True

    # simulations per configuration
    NUM_SIMULATIONS = 15

    # (NUM_SWARMS, NUM_UAV_PER_SWARM)
    UAV_NUMS = ((1, 4),     # 4
                (2, 4),     # 8
                (4, 4),     # 16
                (4, 8),     # 32
                (8, 8))     # 64

    REGION_SIZE = 4  # smaller 'grid' within the larger area (a x a area)
    GRID_SIZE = 10  # each block in the grid represents a region (b x b area)

    SURV_NUMS = (4, 32, 128)

    TIMEOUT_ITERATIONS = 3000

    SURV_LIFESPAN_RANGE = (100, TIMEOUT_ITERATIONS)  # (min, max) iterations

    LOG_SIM = True
