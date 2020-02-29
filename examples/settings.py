CONNECTION_STRING = "..."  # Get yours - instructions in README
QUEUE = "..."  # Name of the queue

try:
    from settings_local import *
except ImportError:
    pass
