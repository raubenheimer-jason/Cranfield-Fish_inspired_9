from constants.constants import *


class Region:
    """
    A region constists of multiple blocks (array of 'Block' objects)
    A region can also have a state...

    Regions and blocks can be in one of the following states: unassigned, assigned or explored.

    Assigned region: is a region with at least one assigned block.

    When all blocks in a region have been explored, then the region is said to be explored as well.

    At the start of the mission, the statuses of the regions and blocks are set to unassigned and change as the mission progresses.

    "the profitability of the region is increased" <-- the region posessed the profitability
    """

    def __init__(self, position, block_arr, state="unassigned"):
        # TODO: add check to make sure position and state is valid
        self.position = position  # region position in the grid [reg_x, reg_y]
        self.block_arr = block_arr  # array of block objects
        self.state = state  # state of the region
        self.profit = 0

        self.num_explored_blocks = 0
        self.num_assigned_blocks = 0

    def get_region_position(self):
        """ return the region position in the grid [reg_x, reg_y]"""
        return self.position

    def get_block_arr(self):
        return self.block_arr

    def get_state(self):
        return self.state

    def get_profit(self):
        return self.profit

    def set_state(self, state):
        # TODO: add check to make sure position and state is valid
        self.state = state

    def get_block_state(self, block):
        """returns the state of a single block"""
        bl_state = self.block_arr[block[1]][block[0]].get_state()
        return bl_state

    def increment_profit(self):
        """self.profit = self.profit + 1"""
        self.profit = self.profit + 1

    def increment_num_explored_blocks(self):
        """increment the number of explored blocks"""
        self.num_explored_blocks += 1

    def get_num_explored_blocks(self):
        """returns the num_explored_blocks"""
        return self.num_explored_blocks

    def get_num_assigned_blocks(self):
        """returns the num_assigned_blocks"""
        return self.num_assigned_blocks

    def increment_num_assigned_blocks(self):
        """increment the number of assigned blocks"""
        self.num_assigned_blocks += 1

    def decrement_num_assigned_blocks(self):
        """decrement the number of assigned blocks"""
        self.num_assigned_blocks -= 1

    def has_unassigned_block(self):
        """ Returns True if there is at least one unassigned block in this region"""

        num_explored_assigned = self.num_assigned_blocks + self.num_explored_blocks
        if num_explored_assigned >= TOTAL_REGION_BLOCKS:
            return False
        else:
            return True

    def update_block_state(self, state, bl_pos):

        prev_state = self.block_arr[bl_pos[1]][bl_pos[0]].get_state()

        if prev_state == "unassigned" and state == "assigned":
            self.increment_num_assigned_blocks()
        elif prev_state == "assigned" and state == "explored":
            self.increment_num_explored_blocks()
            self.decrement_num_assigned_blocks()
        else:
            return

        self.block_arr[bl_pos[1]][bl_pos[0]].set_state(state)

        # check if region state needs to be updated...
        if not self.state == "explored":
            if self.num_explored_blocks == TOTAL_REGION_BLOCKS:
                self.set_state("explored")
            elif self.state == "unassigned" and self.num_assigned_blocks > 0:
                self.set_state("assigned")
