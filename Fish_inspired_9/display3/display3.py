import time
import pygame
from constants.constants import *
import os
from convert.convert import pix_to_pix_display_position, abs_to_region_block_pos, abs_block_to_pixel_xy

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
pygame.font.init()


REG_UNASSIGNED_COL = LIGHT_BLUE_REG
REG_ASSIGNED_COL = TEAL
REG_EXPLORED_COL = GREY

BL_UNASSIGNED_COL = LIGHT_BLUE
BL_ASSIGNED_COL = TEAL
BL_EXPLORED_COL = GREY

UAV_SAMPLER_COL = BLUE
UAV_FOLLOWER_COL = DEEP_SKY_BLUE
UAV_MOVE_COL = GAINSBORO
UAV_RESCUE_COL = LIGHT_RED
UAV_UNKNOWN_COL = SILVER

UAV_DQN_COL = DEEP_SKY_BLUE


SURV_RESC_COL = LIGHT_ORANGE
SURV_UNDISC_COL = ORANGE
SURV_DEC_COL = DARK_GREY

UAV_FONT = pygame.font.SysFont('comicsans', UAV_FONT_SIZE)
GRID_FONT = pygame.font.SysFont('comicsans', GRID_FONT_SIZE)
SURV_FONT = pygame.font.SysFont('comicsans', SURV_FONT_SIZE)
PROFIT_FONT = pygame.font.SysFont('comicsans', PROFIT_FONT_SIZE)
REG_FONT = pygame.font.SysFont('comicsans', REG_FONT_SIZE)
STATUS_FONT = pygame.font.SysFont('comicsans', STATUS_FONT_SIZE)


pygame.display.set_caption(
    f"Grid state ({GRID_SIZE}x{GRID_SIZE} regions, {REGION_SIZE}x{REGION_SIZE} blocks/region)")


def draw_sim_window(WIN,
                    loop_time,
                    start_time,
                    grid_arr,
                    stats_arr,
                    uav_pos_arr,
                    surv_arr,
                    uav_states_arr,
                    last_known_modes_arr,
                    iter_count,
                    num_surv,
                    sim_type,
                    predict_arr):
    """"""

    times = []

    WIN.fill(BLACK)
    s = time.time()
    print_grid_state(WIN, grid_arr)  # +- 5ms (<10)
    t1 = (time.time()-s)*1000
    times.append(t1)
    s = time.time()
    print_info(WIN,
               loop_time,
               start_time,
               stats_arr,
               #    uav_states_arr,
               last_known_modes_arr,
               iter_count,
               num_surv)  # +- 1ms
    t2 = (time.time()-s)*1000
    times.append(t2)
    s = time.time()
    print_surv_state(WIN, surv_arr)  # +- 40ms (sometimes 100+)
    t3 = (time.time()-s)*1000
    times.append(t3)
    s = time.time()

    if sim_type == "implicit_prediction":
        print_predictions(WIN, uav_pos_arr, predict_arr)

    print_uav_state(WIN,
                    uav_pos_arr,
                    uav_states_arr,
                    last_known_modes_arr)  # +- 10ms

    t4 = (time.time()-s)*1000
    times.append(t4)

    return times


def calc_avgs(avg_arr, tot_arr, num):

    for i, tot in enumerate(tot_arr):
        avg_arr[i] = round(tot/num)


def set_totals(tot_arr, times):

    for i, t in enumerate(times):
        tot_arr[i] += t


def draw_manager_window(WIN,
                        fps,
                        start_time,
                        grid_arr,
                        stats_arr,
                        uav_states_arr,
                        uav_states_lock,
                        last_known_modes_arr,
                        last_known_modes_lock):
    """"""

    with uav_states_lock:
        uav_states_arr_copy = uav_states_arr

    WIN.fill(BLACK)
    print_grid_state(WIN, grid_arr)  # +- 5ms (<10)
    print_info(WIN,
               fps,
               start_time,
               stats_arr,
               uav_states_arr_copy)  # +- 1ms


def mouse_over_play_btn(mouse):
    """returns true if the mouse is over play button"""
    if PLAY_BTN_POS[0] <= mouse[0] <= (PLAY_BTN_POS[0]+PLAY_BTN_SIZE) and PLAY_BTN_POS[1] <= mouse[1] <= (PLAY_BTN_POS[1]+PLAY_BTN_SIZE):
        return True

    return False


def draw_play_btn(WIN, mouse, play):

    # if mouse is hovered on a button it
    # changes to lighter shade
    button = pygame.Rect(
        PLAY_BTN_POS[0], PLAY_BTN_POS[1], PLAY_BTN_SIZE, PLAY_BTN_SIZE)

    if mouse_over_play_btn(mouse):
        pygame.draw.rect(WIN, ORANGE, button)

    else:
        pygame.draw.rect(WIN, LIGHT_ORANGE, button)

    # draw play text
    str = "state = "
    if play:
        str += "PLAY"
    else:
        str += "PAUSE"
    txt = GRID_FONT.render(str, 1, WHITE)
    x_pos = PLAY_BTN_POS[0] - 125
    y_pos = WIN_HEIGHT-txt.get_size()[1]
    pos = (x_pos, y_pos)
    WIN.blit(txt, pos)


def get_num_samplers_followers(last_known_modes_arr):
    """
    returns [samplers, followers]
    returns the number of sampler and follower UAVs

    """
    sampler_cnt = 0
    follower_cnt = 0

    # for uav_state in uav_states_arr:
    for uav_mode in last_known_modes_arr:
        if uav_mode == "sampler":
            sampler_cnt += 1
        elif uav_mode == "follower":
            follower_cnt += 1

    return [sampler_cnt, follower_cnt]


def print_info(WIN, loop_time_ns, start_time, stats_arr, last_known_modes_arr, iter_count, num_surv):
    """
    print the key and variable parameters on the right

    stats_arr: [blocks_explored, survivors_rescued]
    """

    key_arr = [[REG_UNASSIGNED_COL, "region (unassigned)"],
               [REG_ASSIGNED_COL, "region (assigned)"],
               [REG_EXPLORED_COL, "region (explored)"],
               [BL_UNASSIGNED_COL, "block (unassigned)"],
               [BL_ASSIGNED_COL, "block (assigned)"],
               [BL_EXPLORED_COL, "block (explored)"],
               [UAV_SAMPLER_COL, "UAV (sampler)"],
               [UAV_FOLLOWER_COL, "UAV (follower)"],
               [SURV_RESC_COL, "Survivor (rescued)"],
               [SURV_UNDISC_COL, "Survivor (undiscovered)"]]

    x_pos = GRID_SIZE*BLOCK_SPACE*REGION_SIZE + MARGIN*2
    y_pos = MARGIN
    height = None

    key_widths = list()

    txt_str = "Key:"
    txt = GRID_FONT.render(txt_str, 1, WHITE)
    WIN.blit(txt, (x_pos, y_pos))
    height = txt.get_size()[1]
    y_pos += height + 5

    for key in key_arr:
        txt = STATUS_FONT.render(key[1], 1, WHITE)
        height = txt.get_size()[1]
        WIN.blit(txt, (x_pos+height+5, y_pos))

        b = pygame.Rect(x_pos, y_pos, height, height)
        pygame.draw.rect(WIN, key[0], b)
        y_pos += height + 5

        key_width = txt.get_size()[0] + x_pos+height+5
        key_widths.append(key_width)

    # reset y pos
    y_pos = MARGIN
    # set x pos to next to "key"
    x_pos = max(key_widths) + MARGIN

    # print current simulation stats
    txt_str = "Current simulation stats:"
    txt = GRID_FONT.render(txt_str, 1, WHITE)
    WIN.blit(txt, (x_pos, y_pos))
    y_pos += height + 5
    # survivors rescued: 3/60
    resc_cnt = stats_arr[2]
    txt_str = f"Survivors found: {resc_cnt}/{num_surv}"
    txt = STATUS_FONT.render(txt_str, 1, WHITE)
    WIN.blit(txt, (x_pos, y_pos))
    y_pos += height + 5
    # Blocks explored: 45%
    perc_explored = round((stats_arr[0]/TOTAL_BLOCKS)*100, 1)
    txt_str = f"Blocks explored: {perc_explored}%"
    txt = STATUS_FONT.render(txt_str, 1, WHITE)
    WIN.blit(txt, (x_pos, y_pos))
    y_pos += height + 5
    # Samplers / followers
    samp_foll = get_num_samplers_followers(last_known_modes_arr)
    # Num Samplers: 12
    txt_str = f"Num Samplers: {samp_foll[0]}"
    txt = STATUS_FONT.render(txt_str, 1, WHITE)
    WIN.blit(txt, (x_pos, y_pos))
    y_pos += height + 5
    # Num Followers: 23
    txt_str = f"Num Followers: {samp_foll[1]}"
    txt = STATUS_FONT.render(txt_str, 1, WHITE)
    WIN.blit(txt, (x_pos, y_pos))
    y_pos += height + 5
    # Display FPS:
    if not loop_time_ns == None:
        loop_time_ms = round(loop_time_ns/1000000)
    else:
        loop_time_ms = "n/a"
    txt_str = f"Loop time (ms): {loop_time_ms}"
    txt = STATUS_FONT.render(txt_str, 1, WHITE)
    WIN.blit(txt, (x_pos, y_pos))
    y_pos += height + 5
    # Iteration count:
    txt_str = f"Iteration count: {iter_count[0]}"
    txt = STATUS_FONT.render(txt_str, 1, WHITE)
    WIN.blit(txt, (x_pos, y_pos))
    y_pos += height + 5
    # Elapsed time:
    txt_str = f"Elapsed time (s): {round(time.time()-start_time,1)}"
    txt = STATUS_FONT.render(txt_str, 1, WHITE)
    WIN.blit(txt, (x_pos, y_pos))
    y_pos += height + 5


def print_grid_state(WIN, grid_arr):
    """
    Visualise the status of grid (regions and blocks)

    draws UAVs as blue circles

    rx = region x position (within the grid)
    ry = region y position (within the grid)

    bx = block x position (within the region)
    by = block y position (within the region)

    """

    for ry, reg_row in enumerate(grid_arr):  # first row, y = 0
        for rx, region in enumerate(reg_row):  # iter cols, therefore "y" ??

            rx_pos = rx*(REGION_SPACE_WIDTH+BLOCK_MARGIN) + MARGIN
            ry_pos = ry*(REGION_SPACE_HEIGHT+BLOCK_MARGIN) + MARGIN

            reg_state = region.get_state()
            if reg_state == "unassigned":
                r_colour = REG_UNASSIGNED_COL
            elif reg_state == "assigned":
                r_colour = REG_ASSIGNED_COL
            else:
                r_colour = REG_EXPLORED_COL  # "explored"

            r = pygame.Rect(rx_pos, ry_pos, REGION_SPACE_WIDTH,
                            REGION_SPACE_HEIGHT)
            pygame.draw.rect(WIN, r_colour, r)

            # print region space info
            # 1. blocks explored
            bl_exp = region.get_num_explored_blocks()
            # 2. blocks assigned
            bl_ass = region.get_num_assigned_blocks()
            # 3. profit
            profit = region.get_profit()

            r_str = f"exp: {bl_exp}, ass: {bl_ass}, profit: {profit}"

            reg_txt = REG_FONT.render(r_str, 1, WHITE)
            if reg_txt.get_size()[1] < REGION_INFO_SPACE:
                WIN.blit(reg_txt, (rx_pos, ry_pos))

            # print blocks
            block_arr = region.get_block_arr()
            for by, block_row in enumerate(block_arr):
                for bx, block in enumerate(block_row):

                    x_pos = rx*BLOCK_SPACE*REGION_SIZE + bx*BLOCK_SPACE + MARGIN
                    y_pos = ry*BLOCK_SPACE*REGION_SIZE + by * \
                        BLOCK_SPACE + MARGIN + REGION_INFO_SPACE*(ry+1)

                    block_state = block.get_state()
                    if block_state == "unassigned":
                        b_colour = BL_UNASSIGNED_COL
                    elif block_state == "assigned":
                        b_colour = BL_ASSIGNED_COL
                    else:
                        b_colour = BL_EXPLORED_COL  # "explored"

                    b = pygame.Rect(x_pos, y_pos, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(WIN, b_colour, b)


def print_uav_heights(WIN, uav_hs_arr):
    """ print uav heights 

    uav_hs_arr -> [[uav_z, uav_state],[]]

    loop over each uav and print "bar graph" for height...
    """

    # this first start_x_pos is the beginning of the "print_info"
    start_x_pos = GRID_SIZE*BLOCK_SPACE*REGION_SIZE + MARGIN*2

    for i, uav_hs in enumerate(uav_hs_arr):
        h = uav_hs[0]
        state = uav_hs[1]

        if state == "follower":
            u_str_1 = f"{i}"
            u_str_2 = f"F"
            u_str_3 = f"{round(h)}"
            u_col = UAV_FOLLOWER_COL
        elif state == "sampler":
            u_str_1 = f"{i}"
            u_str_2 = f"S"
            u_str_3 = f"{round(h)}"
            u_col = UAV_SAMPLER_COL
        elif state == "move":
            u_str_1 = f"{i}"
            u_str_2 = f"Mo"
            u_str_3 = f"{round(h)}"
            u_col = UAV_MOVE_COL
        elif state == "unknown":
            u_str_1 = f"{i}"
            u_str_2 = f"Un"
            u_str_3 = f"{round(h)}"
            u_col = UAV_UNKNOWN_COL
        elif state == "rescue":
            u_str_1 = f"{i}"
            u_str_2 = f"Re"
            u_str_3 = f"{round(h)}"
            u_col = UAV_RESCUE_COL
        else:
            print(
                "Error in display3.print_uav_state, unknown uav state.")

        uav_txt_1 = UAV_FONT.render(u_str_1, 1, WHITE)
        uav_txt_2 = UAV_FONT.render(u_str_2, 1, WHITE)
        uav_txt_3 = UAV_FONT.render(u_str_3, 1, WHITE)
        txt_size_1 = uav_txt_1.get_size()
        txt_size_2 = uav_txt_2.get_size()
        txt_size_3 = uav_txt_3.get_size()

        height_pix = 10 * h

        x_pos = start_x_pos + i * (UAV_HEIGHT_WIDTH + UAV_HEIGHT_SPACE)
        all_txt_height = txt_size_1[1] + txt_size_2[1] + txt_size_3[1]
        # 30 for space from play button
        y_pos = WIN_HEIGHT - MARGIN - all_txt_height - 30
        y_pos -= height_pix

        h_bl = pygame.Rect(x_pos, y_pos, UAV_HEIGHT_WIDTH, height_pix)
        pygame.draw.rect(WIN, u_col, h_bl)
        if (max(txt_size_1[0], txt_size_2[0], txt_size_3[0])) < UAV_HEIGHT_WIDTH:
            y_pos += height_pix + 5 + UAV_HEIGHT_SPACE
            t_pos_1 = (x_pos, y_pos)
            t_pos_2 = (x_pos, y_pos + txt_size_1[1])
            t_pos_3 = (x_pos, y_pos + 2*txt_size_1[1])

            WIN.blit(uav_txt_1, t_pos_1)
            WIN.blit(uav_txt_2, t_pos_2)
            WIN.blit(uav_txt_3, t_pos_3)

        else:
            # just do number?
            pass


def print_predictions(WIN, uav_pos_arr, predict_arr):
    """ pred arr is in pix position (same as the UAV) """

    # print("disp: ", predict_arr)

    for uav_pos, pred in zip(uav_pos_arr, predict_arr):

        if not pred:
            continue

        # draw a line from UAV pos to the predict arr pos
        # pred_pix = abs_block_to_pixel_xy(pred)
        pred_pix = pix_to_pix_display_position(pred)
        uav_pix = pix_to_pix_display_position(uav_pos[0:2])

        pygame.draw.line(WIN, MAGENTA, uav_pix, pred_pix, 4)

# def print_predictions(WIN, uav_pos_arr, predict_arr):
#     """ pred arr is in pix position (same as the UAV) """

#     for uav_pos, pred in zip(uav_pos_arr, predict_arr):

#         if not pred:
#             continue

#         for p in pred:

#             # draw a line from UAV pos to the predict arr pos
#             # pred_pix = abs_block_to_pixel_xy(pred)
#             pred_pix = pix_to_pix_display_position(p)
#             uav_pix = pix_to_pix_display_position(uav_pos[0:2])

#             pygame.draw.line(WIN, MAGENTA, uav_pix, pred_pix, 4)


def print_uav_state(WIN, uav_pos_arr, uav_states_arr, last_known_modes_arr):
    """
    Visualise the status of grid (regions and blocks)

    draws UAVs as blue circles

    rx = region x position (within the grid)
    ry = region y position (within the grid)

    bx = block x position (within the region)
    by = block y position (within the region)

    """

    # print(f"uav_states_arr: {uav_states_arr}")
    # print(f"last_known_modes_arr: {last_known_modes_arr}")

    for mode in last_known_modes_arr:
        if not mode:
            return

    # if not last_known_modes_arr[-1]:
    #     return

    uav_hs_arr = []  # heights and states array [[uav_z, uav_state],[]]

    for i, uav_pix in enumerate(uav_pos_arr):

        uav_z = uav_pix[2]

        uav_disp_px = pix_to_pix_display_position(uav_pix)

        uav_state = uav_states_arr[i]
        uav_height_state_arr = [uav_z, uav_state]
        uav_hs_arr.append(uav_height_state_arr)

        uav_mode = last_known_modes_arr[i]

        # print(uav_mode)
        if uav_mode == "follower":
            u_col = UAV_FOLLOWER_COL
        elif uav_mode == "sampler":
            u_col = UAV_SAMPLER_COL
        elif uav_mode == None:
            u_col = UAV_UNKNOWN_COL
        else:
            raise ValueError(f"Invalid uav_mode: {uav_mode}")

        if uav_state == "follower":
            u_str_1 = f"{i}_F"
            u_str_2 = f"{round(uav_z)}"
        elif uav_state == "sampler":
            u_str_1 = f"{i}_S"
            u_str_2 = f"{round(uav_z)}"
        elif uav_state == "move":
            u_str_1 = f"{i}_Mo"
            u_str_2 = f"{round(uav_z)}"
        elif uav_state == "unknown":
            u_str_1 = f"{i}_Un"
            u_str_2 = f"{round(uav_z)}"
        elif uav_state == "rescue":
            u_str_1 = f"{i}_Re"
            u_str_2 = f"{round(uav_z)}"
        else:
            print(
                "Error in display3.print_uav_state, unknown uav state.")
            raise ValueError(f"Invalid uav_state: {uav_state}")

        c_size = BLOCK_SIZE/3
        c_pos = (uav_disp_px[0], uav_disp_px[1])
        pygame.draw.circle(WIN, u_col, c_pos, c_size)

        uav_txt_1 = UAV_FONT.render(u_str_1, 1, WHITE)
        uav_txt_2 = UAV_FONT.render(u_str_2, 1, WHITE)
        txt_size_1 = uav_txt_1.get_size()
        txt_size_2 = uav_txt_2.get_size()
        if (txt_size_1[1] + txt_size_2[1]) < BLOCK_SIZE/2:
            x_pos = uav_disp_px[0] - txt_size_1[0]/2
            y_pos = uav_disp_px[1] - txt_size_1[1]/2
            t_pos_1 = (x_pos, y_pos - txt_size_1[1]/2)
            t_pos_2 = (x_pos, y_pos + txt_size_1[1]/2)
            WIN.blit(uav_txt_1, t_pos_1)
            WIN.blit(uav_txt_2, t_pos_2)

    print_uav_heights(WIN, uav_hs_arr)


def print_surv_state(WIN, surv_arr):
    """
    Visualise the status of grid (regions and blocks)

    draws UAVs as blue circles

    rx = region x position (within the grid)
    ry = region y position (within the grid)

    bx = block x position (within the region)
    by = block y position (within the region)

    """

    for i, surv in enumerate(surv_arr):

        surv_x = surv[0]
        surv_y = surv[1]

        surv_pos = abs_to_region_block_pos([surv_x, surv_y])

        rx = surv_pos[0][0]
        ry = surv_pos[0][1]
        bx = surv_pos[1][0]
        by = surv_pos[1][1]

        # surv bottom half of block
        bl_x_pos = rx*BLOCK_SPACE*REGION_SIZE + bx*BLOCK_SPACE + MARGIN
        bl_y_pos = ry*BLOCK_SPACE*REGION_SIZE + by*BLOCK_SPACE + \
            MARGIN + BLOCK_SPACE/2 + REGION_INFO_SPACE*(ry+1)

        surv_state = surv[2]

        if surv_state == "undiscovered":
            u_str = f"{i}_Und"
            s_col = SURV_UNDISC_COL
        elif surv_state == "rescued":
            u_str = f"{i}_Res"
            s_col = SURV_RESC_COL
        elif surv_state == "deceased":
            u_str = f"{i}_Dec"
            s_col = SURV_DEC_COL
        else:
            raise ValueError("Invalid surv_state")

        sb = pygame.Rect(bl_x_pos, bl_y_pos, BLOCK_SIZE, BLOCK_SIZE/2)
        pygame.draw.rect(WIN, s_col, sb)

        surv_txt = SURV_FONT.render(u_str, 1, WHITE)
        if surv_txt.get_size()[1] < BLOCK_SIZE/2:
            WIN.blit(surv_txt, (bl_x_pos, bl_y_pos))
