import logging
import sys

logger = logging.getLogger("taqu")
logger.setLevel(logging.DEBUG)
hdlr = logging.StreamHandler(sys.stdout)
hdlr.setLevel(logging.DEBUG)
logger.addHandler(hdlr)
