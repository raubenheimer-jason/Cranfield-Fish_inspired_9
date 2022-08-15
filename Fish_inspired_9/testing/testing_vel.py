import math

# # # expected dir_deg = 124.765
# # # expected speed = 2.236
# # curr_pos = [2, 1, 0]  # x,y,z
# # prev_pos = [0, 0, 0]  # x,y,z

# # # expected dir_deg = 180
# # # expected speed = 2
# # curr_pos = [0, 2, 0]  # x,y,z
# # prev_pos = [0, 0, 0]  # x,y,z

# # expected dir_deg = 270
# # expected speed = 1
# curr_pos = [1, 0, 0]  # x,y,z
# prev_pos = [2, 0, 0]  # x,y,z

# # expected dir_deg = 0
# # expected speed = 1
# curr_pos = [1, 0, 0]  # x,y,z
# prev_pos = [1, 1, 0]  # x,y,z

# # dir = del x / del y
# del_x = (curr_pos[0] - prev_pos[0])
# del_y = -(curr_pos[1] - prev_pos[1])

# if del_y == 0:
#     dir_deg = 270
# else:
#     dir = math.tanh(del_x/del_y)
#     dir_deg = dir*(180/math.pi)

# # print(del_y)

# # dir = math.tan((curr_pos[0] - prev_pos[0]) / (curr_pos[1] - prev_pos[1]))

# # dir = math.tanh(del_y/del_x)


# # speed = abs(del_x/del_y)
# speed = math.hypot(del_x, del_y)


# # print(dir)
# # print(dir_deg)
# # print(speed)


def calc_dir_speed(curr_pos, prev_pos):
    """ 
    block coordinates: origin is top left, so x increases to the right and y increases to the bottom

    degrees coordinates: 0/360 is at 12 o'clock, 90 is at 3 o'clock, 180 at 6 o'clock, 270 at 9 o'clock 
    """

    del_x = (curr_pos[0] - prev_pos[0])  # x increases right
    del_y = (curr_pos[1] - prev_pos[1])  # y increases down
    # del_y = (prev_pos[1] - curr_pos[1])  # y increases down

    # print(f"delx: {del_x},  dely: {del_y}")

    # dir = math.tanh(del_x/del_y)*(180/math.pi)
    # speed = math.hypot(del_x, del_y)

    dir = math.atan2(del_y, del_x)*(180/math.pi)+90
    speed = math.hypot(del_y, del_x)

    return dir, speed


def tests(precision=3):
    # test_arr = [[[0, 2, 0], [0, 0, 0], 180, 2]]

    tests_arr = []

    test1 = {"curr_pos": [2, 1, 0],
             "prev_pos": [0, 0, 0],
             "exp_dir": 116.565,
             "exp_speed": 2.236}
    tests_arr.append(test1)

    test2 = {"curr_pos": [0, 2, 0],
             "prev_pos": [0, 0, 0],
             "exp_dir": 180.0,
             "exp_speed": 2.0}
    tests_arr.append(test2)

    test3 = {"curr_pos": [0, 1, 0],
             "prev_pos": [1, 1, 0],
             "exp_dir": 270.0,
             "exp_speed": 1.0}
    tests_arr.append(test3)

    test4 = {"curr_pos": [1, 1, 0],
             "prev_pos": [1, 2, 0],
             "exp_dir": 0.0,
             "exp_speed": 1.0}
    tests_arr.append(test4)

    test4 = {"curr_pos": [2, 2, 0],
             "prev_pos": [0, 2, 0],
             "exp_dir": 90.0,
             "exp_speed": 2.0}
    tests_arr.append(test4)

    print()
    print(
        f"test\tdir_test\tspeed_test\texp_dir, dir\t\texp_speed, speed")

    for i, test in enumerate(tests_arr):
        dir, speed = calc_dir_speed(test["curr_pos"], test["prev_pos"])
        dir = round(dir, precision)
        speed = round(speed, precision)
        exp_dir = round(test["exp_dir"], precision)
        exp_speed = round(test["exp_speed"], precision)

        dir_test = False
        speed_test = False

        if dir == exp_dir:
            dir_test = True

        if speed == exp_speed:
            speed_test = True

        # print(f"dir_test: {dir_test}, speed_test: {speed_test}")
        print(
            f"{i}\t{dir_test}\t\t{speed_test}\t\t{exp_dir}, {dir}\t\t{exp_speed}, {speed}")
    print()


if __name__ == "__main__":
    tests()
