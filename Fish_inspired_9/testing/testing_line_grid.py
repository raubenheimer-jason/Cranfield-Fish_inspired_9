
from sympy.abc import x, y
from sympy import Eq, solve
import math

# line intercepting blocks on a grid

GRID_SIZE = 3  # smaller grid within the region
REGION_SIZE = 2  # larger areas, made up of blocks

ABS_GRID_SIZE = GRID_SIZE*REGION_SIZE

BLOCK_SIZE = 20  # pix

ABS_PIX = ABS_GRID_SIZE*BLOCK_SIZE

# diag max pix
MAX_PIX = math.ceil(math.hypot(ABS_PIX, ABS_PIX))

# print(MAX_PIX)
# 0 deg   = 12 o'clock
# 90 deg  = 3 o'clock
# 180 deg = 6 o'clock
# 270 deg = 9 o'clock

prev_pos = [0, 0]
curr_pos = [1, 1]

# dir_deg = 90

# should intersect all blocks to the right

# move one pix at a time in the x and y directions keeping the dir_deg constant

# create equation for path: y = m*x + c
# slope = d_y/d_x ... but it is different because y is positive down
dy = curr_pos[1]-prev_pos[1]
dx = curr_pos[0]-prev_pos[0]
m = dy/dx
c = curr_pos[1] - m * curr_pos[0]

# print(m)


# def f(x, m, c):

#     # slope:

#     return m*x + c


# print(f(2, m, c))


"""
horizontal line:
    y = mx+c
    y = c
    intersect y axis at 5
    --> 0 = 0x + 5

45 deg line:
    y = mx+c
    intersect origin, slope = +1
    y = x


"""

# sol = solve([Eq(y, 5),
#              Eq(y, x)])
sol = solve([Eq(y, 5),
             Eq(y, 2)])

# sol = solve([ Eq(2*w + x + 4*y + 3*z, 5),
#               Eq(w - 2*x + 3*z, 3),
#               Eq(3*w + 2*x - y + z, -1),
#               Eq(4*x - 5*z, -3) ])
print(sol)
print({s: sol[s].evalf() for s in sol})


# for step in range(MAX_PIX):

#     new_x = 0

# move_x = 0
