from game.building.consumption.consumption_rule import ConsumptionRule


class ConsumptionExecutor:
    def __init__(self, inventory, consumption_rule: ConsumptionRule):
        self.inventory = inventory
        self.consumption_rule = consumption_rule
        self.time_counter = 0

    def is_running(self):
        return self.time_counter > 0

    def update(self, delta_time):
        if self.is_running():
            self.time_counter -= delta_time
            if self.time_counter <= 0:

                if self.inventory.subs(self.consumption_rule.production):
                    self.time_counter = self.consumption_rule.time
                else:
                    self.time_counter = 0
        else:
            if self.inventory.subs(self.consumption_rule.production):
                self.time_counter = self.consumption_rule.time
            else:
                self.time_counter = 0
