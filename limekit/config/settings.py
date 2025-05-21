import limekit

# Everything that needs to be initialized in the engines
INSTALLED_PARTS = [
    "limekit.framework.components",
    "limekit.framework.core.mechanism",
    # "limekit.framework.components.layouts",
    # "limekit.framework.components.charts",
    "limekit.framework.gui",
    "limekit.framework.handle",
    #
    #
    #
    # New
    "limekit.core",
    "limekit.components",
    "limekit.gui",
    "limekit.utils",
]

# You'll sometimes not want some dir walked
IGNORE_PARTS = [
    "limekit.components.charts",
]

IS_IDE = True  # If frozen, this shall be set to False

# The path to the installed limekit module
limekit_SITEPACKAGE_DIR = limekit.__path__[0]
