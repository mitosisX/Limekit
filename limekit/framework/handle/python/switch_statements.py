from limekit.framework.core.engine.parts import EnginePart
import lupa


# 23 October, 2023 - ChatGPT
# Behold the switch-case lua implementation!
class Switch(EnginePart):
    name = "switch"

    def __init__(self, var):
        self.var = var
        self.cases = []

    def case(self, condition, action):
        self.cases.append((condition, action))
        return self

    def default(self, callable):
        for case_condition, case_action in self.cases:
            if case_condition == self.var:
                case_action()
                return
        else:
            # This is the default case
            # print("Default case")
            if callable:
                callable()


# Usage
# variable = 2
# Switch(variable).case(1, lambda: print("Case 1")).case(2, lambda: print("Case 2")).case(
#     3, lambda: print("Case 3")
# ).check()
