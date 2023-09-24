import limekit

# Everything that needs to be initialized in the engines
INSTALLED_PARTS = [
    "limekit.framework.components",
    "limekit.framework.handle",
]

IS_IDE = True  # If frozen, this shall be set to False

# The path to the installed limekit module
limekit_SITEPACKAGE_DIR = limekit.__path__[0]
