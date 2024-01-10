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
# switch(variable)
#   .case(1, function() print("Case 1") end)
#   .case(2, function() print("Case 2") end)
#   .case(3, function() print("Case 3") end)
#   .default(function() print("Case 3") end)
# )
