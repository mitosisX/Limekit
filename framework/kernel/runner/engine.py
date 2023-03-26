import js2py

"""
20 March, 2023 8:23 AM (Monday)

Basic structure
"""
class Engine(object):
    def __init__(self):
        self.engine = js2py.EvalJs(objects = 2, enable_require=True)
        
    """
    For executing any incoming JavaScript code
    """
    def execute(self, script):
        pass
    
    def setObject(self, **object):
        pass
        
    