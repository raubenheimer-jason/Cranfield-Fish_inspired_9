

from uav.uavFishCore import UavSelectBlock
from display3.display3 import draw_sim_window, mouse_over_play_btn, draw_play_btn
from grid.grid import gridArr
from grid.GridContainer import GridContainer
import pygame
from constants.constants import *
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


class DisplayContainer:

    def __init__(self,
                 quit_flag,
                 iter_count,
                 next,
                 start_time,
                 uav_pos_arr,
                 sim_type,  # "original" or "implicit"
                 uav_modes_arr,  # for original, if implicit this is None
                 uav_states_arr,  # for original, if implicit this is None
                 grid_arr_obj,   # for original, if implicit this is None
                 surv_arr,
                 prediction_flag=False):

        pygame.font.init()

        self.grid_log_arr = [["time_s",
                              "data_type",
                              "abs_block_pos_x",
                              "abs_block_pos_y",
                              "region_pos_x",
                              "region_pos_y",
                              "block_state"]]

        self.surv_log_arr = [["time_s",
                              "data_type",
                              "surv_id",
                              "abs_block_pos_x",
                              "abs_block_pos_y",
                              "surv_state"]]

        self.next = next
        self.quit_flag = quit_flag
        self.iter_count = iter_count
        self.uav_pos_arr = uav_pos_arr
        self.surv_arr = surv_arr
        self.start_time = start_time
        self.WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.prev_bl_explored = 0
        self.play = PLAY_INITIAL_VAL  # for play button

        self.prediction_flag = prediction_flag

        self.i = -1

        self.sim_type = sim_type
        if self.sim_type == "original":
            # if self.uav_modes_arr is NOT None
            self.uav_states_arr = uav_states_arr
            self.uav_modes_arr = uav_modes_arr  # for original. This is None if implicit
            self.grid_arr_obj = grid_arr_obj

        elif self.sim_type == "implicit" or self.sim_type == "implicit_prediction":
            self.uav_states_arr = [[] for _ in range(len(uav_pos_arr))]
            self.uav_modes_arr = [[] for _ in range(len(uav_pos_arr))]
            self.grid_arr_obj = gridArr()
            if self.prediction_flag:
                self.predict_arr = [[] for _ in self.uav_pos_arr]
            else:
                self.predict_arr = [[]]
            self.grid_container = GridContainer(self.uav_pos_arr,
                                                None,  # run_state
                                                self.i,  # i
                                                self.uav_modes_arr,
                                                self.predict_arr,  # for prediction
                                                self.grid_arr_obj,  # for prediction
                                                self.uav_states_arr,
                                                self.grid_log_arr,
                                                self.surv_log_arr,
                                                self.surv_arr,
                                                self.prediction_flag)

    def update_win(self, run, loop_time, num_surv):

        if self.sim_type == "implicit" or self.sim_type == "implicit_prediction":
            # always update grid arr first...
            self.grid_container.call_update_grid_arr(self.grid_arr_obj,
                                                     self.iter_count,
                                                     None,
                                                     prediction_flag=self.prediction_flag)
            predict_arr = self.grid_container.predict_arr

        elif self.sim_type == "original":
            predict_arr = None

        grid_arr = self.grid_arr_obj.get_grid_arr()
        # [blocks_explored, assigned_blocks, survivors_rescued]
        stats_arr = self.grid_arr_obj.get_stats_arr()

        blocks_explored = stats_arr[0]

        if not self.prev_bl_explored == blocks_explored:
            perc = round((blocks_explored/TOTAL_BLOCKS)*100)
            # print(
            #     f"blocks_explored: {blocks_explored}/{TOTAL_BLOCKS} ({perc}%)")
            self.prev_bl_explored = blocks_explored

        if blocks_explored >= TOTAL_BLOCKS:
            if not SHOW_SIMULATION:
                print("all blocks explored... exiting.")
                run[0] = False

        if SHOW_SIMULATION:

            times = draw_sim_window(self.WIN,
                                    loop_time,
                                    self.start_time,
                                    grid_arr,
                                    stats_arr,
                                    self.uav_pos_arr,
                                    self.surv_arr,
                                    self.uav_states_arr,
                                    self.uav_modes_arr,
                                    self.iter_count,
                                    num_surv,
                                    self.sim_type,
                                    predict_arr)

        if SHOW_SIMULATION and False:
            set_totals(tot_arr, times)
            num += 1
            calc_avgs(avg_arr, tot_arr, num)

            a0 = avg_arr[0]
            a1 = avg_arr[1]
            a2 = avg_arr[2]
            a3 = avg_arr[3]

            print(
                f"average times (ms): print_grid_state: {a0}     print_info: {a1}     print_surv_state: {a2}     print_uav_state: {a3}")

        # stores the (x,y) coordinates into the variable as a tuple
        mouse = pygame.mouse.get_pos()
        draw_play_btn(self.WIN, mouse, self.play)

        # This check must be before the SPACE event...
        if self.play == True:
            if self.next[0] == False:
                self.next[0] = True
        else:
            if self.next[0] == True:
                self.next[0] = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run[0] = False

            # checks if a mouse is clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_over_play_btn(mouse):
                    self.play = not self.play

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.next[0] = True

        pygame.display.update()

        if run[0] == False:
            print("Exiting display3.update_win.")
            pygame.display.quit()
