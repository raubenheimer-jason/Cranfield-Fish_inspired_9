from constants.constants import *


class BlockPosition:
    """
    Stores the position in seperate region and block
    Used for UAV position and Block position
    [x, y]
    """

    def __init__(self, local_position=None, region_position=None, abs_position=None):
        """
        local_position  = position within a specific region
        region_position = position of the region within the grid
        [x, y]
        """
        # TODO: add check to make sure position and state is valid

        if local_position and region_position:
            local_pos = local_position
            region_pos = region_position
            z = None
        elif abs_position:
            # calculate local and region pos from abs pos
            a_pos = [abs_position[0], abs_position[1]]
            pos = self.abs_to_region_block_pos(abs_pos=a_pos)
            local_pos = pos[0]
            region_pos = pos[1]
            z = abs_position[2]
        else:
            print("Error in BlockPosition")

        self.local_position = local_pos
        self.region_position = region_pos
        self.z = z

    def update_abs_pos(self, x_abs_pos, y_abs_pos, z_abs_pos):
        reg_bl_pos = self.abs_to_region_block_pos((x_abs_pos, y_abs_pos))
        self.local_position = reg_bl_pos[0]
        self.region_position = reg_bl_pos[1]
        self.z = z_abs_pos

    def update_xy_position(self, local_pos, region_pos):
        """only update local and region position (z stays the same)"""
        self.local_position = local_pos
        self.region_position = region_pos

    def get_abs_x(self):
        return self.get_abs_position()[0]

    def get_abs_y(self):
        return self.get_abs_position()[1]

    def get_abs_z(self):
        return self.z

    def update_z_position(self, z):
        """Update the z position"""
        self.z = z

    def get_local_position(self):
        """[x, y]"""
        return self.local_position

    def get_region_position(self):
        """[x, y]"""
        return self.region_position

    def get_abs_position(self):
        """Return absolute position (basically ignoring regions, how big is the area in terms of a x a blocks)"""
        # ((number of regions accross/down) * (number of blocks in a region)) + (local number of blocks accross/down)
        x_pos = (self.region_position[0] *
                 REGION_SIZE) + self.local_position[0]
        y_pos = (self.region_position[1] *
                 REGION_SIZE) + self.local_position[1]
        z_pos = self.z

        return [x_pos, y_pos, z_pos]

    def abs_to_region_block_pos(self, abs_pos):
        """converts absolute position to region and block position
        return [[bl_x, bl_y], [reg_x, reg_y]]
        return (local, region)
        """
        abs_x = abs_pos[0]
        abs_y = abs_pos[1]

        reg_x = abs_x // REGION_SIZE
        reg_y = abs_y // REGION_SIZE

        bl_x = abs_x - reg_x*REGION_SIZE
        bl_y = abs_y - reg_y*REGION_SIZE

        return [[bl_x, bl_y], [reg_x, reg_y]]
