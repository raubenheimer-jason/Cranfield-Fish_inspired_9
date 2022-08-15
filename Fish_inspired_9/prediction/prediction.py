
import math
from generalFunctions.generalFunctions import print_i


def change_target(self_i, self_target_xy, predict_arr, uav_pos_arr):

    for i, target in enumerate(predict_arr):

        if i == self_i:
            # dont do our own one...
            continue

        if not self_target_xy or not target:
            continue

        if self_target_xy == target:
            # check if the uav that has the same target is closer than us...
            my_dist = math.dist(uav_pos_arr[self_i][0:2],
                                target)
            other_uav_dist = math.dist(uav_pos_arr[i][0:2],
                                       target)

            # need to factor in distance and time...
            # calculate number of steps until uav reaches block...
            # this is based on distance, travel speed, and whether the uav is searching or not

            if my_dist <= other_uav_dist and self_i < i:
                # we have priority
                continue

            return True
