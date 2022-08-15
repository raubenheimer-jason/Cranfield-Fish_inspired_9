from blockPosition.blockPosition import BlockPosition


class Block:
    """
    Regions and blocks can be in one of the following states: unassigned, assigned or explored.
    - Assigned block: is a block that has been selected by a UAV but where the search for a survivor is yet to be completed.
    - A block is said to be explored when a search for a survivor has been completed.
    - At the start of the mission, the statuses of the regions and blocks are set to unassigned and change as the mission progresses.
    """

    def __init__(self, position: BlockPosition, state="unassigned"):
        # TODO: add check to make sure position and state is valid
        self.position = position  # Position object
        self.state = state  # ? rather store as number, not string? Maybe struct?

    def get_local_position(self):
        return self.position.get_local_position()

    def get_region_position(self):
        return self.position.get_region_position()

    def get_abs_position(self):
        """Return absolute position (basically ignoring regions, how big is the area in terms of a x a blocks)"""
        return self.position.get_abs_position()

    def get_state(self):
        return self.state

    def set_state(self, state):
        # TODO: add check to make sure state is valid
        self.state = state
