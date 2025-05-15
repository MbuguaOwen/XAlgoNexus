class ExecutionSafety:
    def __init__(self):
        self.leg1_filled = False
        self.leg2_filled = False
        self.leg3_filled = False

    def reset(self):
        self.leg1_filled = False
        self.leg2_filled = False
        self.leg3_filled = False

    def update_leg_status(self, leg_id: int, filled: bool):
        if leg_id == 1:
            self.leg1_filled = filled
        elif leg_id == 2:
            self.leg2_filled = filled
        elif leg_id == 3:
            self.leg3_filled = filled

    def is_cycle_complete(self):
        return self.leg1_filled and self.leg2_filled and self.leg3_filled

    def detect_incomplete_cycle(self):
        return self.leg1_filled and (not self.leg2_filled or not self.leg3_filled)