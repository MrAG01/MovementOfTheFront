from components.items import Items

class ProductionExecutor:
    def __init__(self, inventory, on_end_callback):
        self.inventory = inventory
        self.time_counter = 0
        self.output = None
        self.on_end_callback = on_end_callback
        self.current_rule = None


    def try_start(self, production_rule):
        _input: Items = production_rule.input

        if _input:
            # print("CHECKING:", _input, "RESULT:", self.inventory.has_amount(_input))
            if not self.inventory.has_amount(_input):
                return False
            else:
                self.inventory.subs(_input)

        self.current_rule = production_rule
        self.time_counter = production_rule.time
        self.output = production_rule.output
        return True

    def get_current_rule(self):
        return self.current_rule

    def is_running(self):
        return self.time_counter > 0

    def update(self, delta_time):
        if self.is_running():
            self.time_counter -= delta_time
            if self.time_counter <= 0:
                self.time_counter = 0
                self.inventory.adds(self.output)
                if self.on_end_callback is not None:
                    self.on_end_callback()
