import sys
from limekit.framework.core.engine.parts import EnginePart


class CMD(EnginePart):
    args = sys.argv
    name = "cmd"
