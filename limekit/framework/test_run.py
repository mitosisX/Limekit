# Yeah, I know... This looks half done. But hey, it's working right?
import os


# print(os.getcwd())
def run():
    from limekit.framework.core.engine.app_engine import Engine

    engine = Engine()
    engine.start()
