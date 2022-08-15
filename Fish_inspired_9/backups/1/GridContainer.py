from generalFunctions.generalFunctions import print_i
from grid.grid import update_grid_arr
from constants.constants import ABS_PIX
from sympy.abc import x, y
from sympy import Eq, solve


class GridContainer:
    """ GridContainer is ONLY used for implicit algorithm... 
        Therefore prediction can happen from here...
    """

    def __init__(self,
                 uav_pos_arr,
                 run_state,
                 i,
                 last_known_modes_arr,
                 uav_states_arr,
                 grid_log_arr,
                 surv_log_arr,
                 surv_arr):

        self.uav_pos_arr = uav_pos_arr
        self.run_state = run_state  # list so its pass by reference
        self.i = i
        self.last_known_modes_arr = last_known_modes_arr
        self.uav_states_arr = uav_states_arr
        self.prev_pos_uav_arr = [[] for _ in self.uav_pos_arr]
        self.all_prev_states_arr = [[] for _ in self.uav_pos_arr]
        # list to remember pos of survivors so 1 survivor = only 1 profit
        self.rescue_pos_arr = []

        if self.run_state == None:
            self.update_block_state_flag = [True]
        else:
            self.update_block_state_flag = [False]

        self.grid_log_arr = grid_log_arr  # for display
        self.surv_log_arr = surv_log_arr  # for display
        self.surv_arr = surv_arr  # for display3

        # array to keep track of the explored blocks so we dont set them a second time
        self.exp_blocks_arr = []

        # prediction array...
        self.predict_arr = [[] for _ in self.uav_pos_arr]

    def call_update_grid_arr(self, grid_arr_obj, iter_num, explored_block_log_arr):

        update_grid_arr(self.run_state,
                        self.grid_log_arr,  # display3
                        self.surv_log_arr,  # display3
                        explored_block_log_arr,  # only for implicit, None otherwise
                        self.surv_arr,  # display3
                        self.i,
                        self.uav_pos_arr,
                        self.uav_states_arr,  # display3
                        self.last_known_modes_arr,
                        grid_arr_obj,
                        self.prev_pos_uav_arr,
                        self.all_prev_states_arr,
                        self.rescue_pos_arr,
                        self.update_block_state_flag,
                        iter_num,
                        self.exp_blocks_arr)

        self.update_pred_arr()

    def update_pred_arr(self):

        # if self.i == 0:
        for i, (prev_pos, curr_pos) in enumerate(zip(self.prev_pos_uav_arr, self.uav_pos_arr)):
            print_i(0, self.i, f"prev: {prev_pos}, curr: {curr_pos}")

            # if not prev_pos and curr_pos:
            #     continue

            # if prev_pos[0:2] == curr_pos[0:2]:
            #     continue

            # dy = curr_pos[1]-prev_pos[1]
            # dx = curr_pos[0]-prev_pos[0]
            # if dx == 0:
            #     m = None
            #     c = None  # what if UAV is on the y axis? unlikely...
            # else:
            #     m = dy/dx
            #     c = curr_pos[1] - m * curr_pos[0]

            # direction = self.get_direction(prev_pos, curr_pos)

            # line_end_point = self.get_line_endpoint(m,
            #                                         c,
            #                                         direction,
            #                                         prev_pos,
            #                                         curr_pos)

            line_end_point = self.get_line_endpoint(prev_pos,
                                                    curr_pos)

            # # will return none if the uav is not moving etc... therefore cant make prediction
            # if line_end_point == None:
            #     # continue
            #     line_end_point = []

            # now follow this line and select the next unassigned block
            # there will be flaws in this becasue the UAV tends to look for a block in the same region...

            # print(f"line_end_point: {line_end_point}")
            self.predict_arr[i] = line_end_point

    def get_direction(self, prev_pos, curr_pos):
        """ returns a tuple (horizontal, vertical) 

        if horizontal == 1, its moving right, else if horizontal == -1 its moving left
        if vertical == 1, its moving down, else if vertical == -1 its moving up

        if they == 0, it is not moving in that direction

        """

        hori_dir = 0
        vert_dir = 0

        if prev_pos[0] < curr_pos[0]:
            hori_dir = 1  # moving right
        elif prev_pos[0] > curr_pos[0]:
            hori_dir = -1  # moving left

        if prev_pos[1] < curr_pos[1]:
            vert_dir = 1  # moving down
        elif prev_pos[1] > curr_pos[1]:
            vert_dir = -1  # moving up

        return hori_dir, vert_dir

    # def get_line_endpoint(self, m, c, direction, prev_pos, curr_pos):
    def get_line_endpoint(self, prev_pos, curr_pos):
        """ gets the endpoint of the line (the block on the boundry) 

        The boundry lines (top, bottom, left, right) are just straight lines (y=mx+c),
        so we just need to find where the line intersects the boundry.
            (Should be two opposite boundries, then choose the one in the direction of travel)
        """

        """
        
        y=mx+c
        
        top line: horizontal, starting at 0,0 and ending at ABS_PIX,0
        bottom line: horizontal, starting at 0,ABS_PIX and ending at ABS_PIX,ABS_PIX

        left line: vertical, starting at 0,0 and ending at 0,ABS_PIX
        right line: vertical, starting at ABS_PIX,0 and ending at ABS_PIX,ABS_PIX


        returns [] if UAV is not moving etc

        """

        if not prev_pos and curr_pos:
            return []

        if prev_pos[0:2] == curr_pos[0:2]:
            return []

        dy = curr_pos[1]-prev_pos[1]
        dx = curr_pos[0]-prev_pos[0]
        if dx == 0:
            m = None
            c = None  # what if UAV is on the y axis? unlikely...
        else:
            m = dy/dx
            c = curr_pos[1] - m * curr_pos[0]

        direction = self.get_direction(prev_pos, curr_pos)

        hori_eq = None
        vert_eq = None

        if m == None or c == None:
            # UAV is moving vertically, m and c are None
            pred_eq = Eq(x, curr_pos[0])  # y = mc+c
        else:
            pred_eq = Eq(y, m*x + c)  # y = mc+c

        if direction[0] == 1:
            hori_eq = Eq(x, ABS_PIX)  # x = ABS_PIX, moving right
        elif direction[0] == -1:
            hori_eq = Eq(x, 0)  # x = 0, moving left
        else:
            pass  # not moving on this axis...

        if direction[1] == 1:
            vert_eq = Eq(y, 0*x + ABS_PIX)  # moving down
        elif direction[1] == -1:
            vert_eq = Eq(y, 0*x + 0)  # moving up
        else:
            pass  # not moving on this axis...

        hori_sol = None
        vert_sol = None

        if not hori_eq == None:
            hori_sol = solve([pred_eq,
                              hori_eq])

            # check for negatives
            if hori_sol[x] < 0 or hori_sol[y] < 0:
                hori_sol = None

            # check if value is in range?

        if not vert_eq == None:
            vert_sol = solve([pred_eq,
                              vert_eq])

            # check for negatives
            if vert_sol[x] < 0 or vert_sol[y] < 0:
                vert_sol = None
        # print(f"bot: {sol}")

        # if not hori_sol == None and not vert_sol == None:
        #     print(f"direction: {direction}")
        #     print(f"hori_sol: {hori_sol}")
        #     print(f"vert_sol: {vert_sol}")
        #     raise ValueError("Should not be two solutions.")

        end_point = []
        if not hori_sol == None:
            # print(f"hori_sol: {hori_sol}")
            # print(f"---> hori_sol: {hori_sol.keys()}")
            # end_point = [hori_sol[x], hori_sol[y]]
            end_point.append([hori_sol[x], hori_sol[y]])
        elif not vert_sol == None:
            # print(f"vert_sol: {vert_sol}")
            # end_point = [vert_sol[x], vert_sol[y]]
            end_point.append([vert_sol[x], vert_sol[y]])
        else:
            print(f"prev: {prev_pos},  curr: {curr_pos}")
            raise ValueError("There should be one solution. Got no solutions.")

        return end_point

    # def get_line_endpoint(self, m, c, direction, curr_pos):
    #     """ gets the endpoint of the line (the block on the boundry)

    #     The boundry lines (top, bottom, left, right) are just straight lines (y=mx+c),
    #     so we just need to find where the line intersects the boundry.
    #         (Should be two opposite boundries, then choose the one in the direction of travel)
    #     """

    #     """

    #     y=mx+c

    #     top line: horizontal, starting at 0,0 and ending at ABS_PIX,0
    #     bottom line: horizontal, starting at 0,ABS_PIX and ending at ABS_PIX,ABS_PIX

    #     left line: vertical, starting at 0,0 and ending at 0,ABS_PIX
    #     right line: vertical, starting at ABS_PIX,0 and ending at ABS_PIX,ABS_PIX

    #     """

    #     from sympy.abc import x, y
    #     from sympy import Eq, solve

    #     if m == None or c == None:
    #         # UAV is moving vertically, m and c are None
    #         pred_eq = Eq(x, curr_pos[0])  # y = mc+c
    #     else:
    #         pred_eq = Eq(y, m*x + c)  # y = mc+c

    #     vert_end_point = None
    #     hori_end_point = None

    #     if direction[0] == 1:
    #         # moving right
    #         right_eq = Eq(x, ABS_PIX)  # x = ABS_PIX
    #         sol = solve([pred_eq,
    #                     right_eq])
    #         print(f"right: {sol}")

    #     elif direction[0] == -1:
    #         # moving left
    #         left_eq = Eq(x, 0)  # x = 0
    #         sol = solve([pred_eq,
    #                     left_eq])
    #         print(f"left: {sol}")
    #     else:
    #         # not moving on this axis...
    #         pass

    #     if direction[1] == 1:
    #         # moving down
    #         bot_eq = Eq(y, 0*x + ABS_PIX)
    #         sol = solve([pred_eq,
    #                     bot_eq])
    #         print(f"bot: {sol}")

    #     elif direction[1] == -1:
    #         # moving up
    #         top_eq = Eq(y, 0*x + 0)
    #         sol = solve([pred_eq,
    #                     top_eq])
    #         print(f"top: {sol}")
    #     else:
    #         # not moving on this axis...
    #         pass
