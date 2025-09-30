# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
""" Import this script to set up the python path.
"""

import os
import sys

TOF_PYTHON_ROOT_DIR = os.path.normpath(os.path.dirname(__file__) + "/..") 
"""Change this path depending on the relative path between this file and the TOF python root dir."""

if TOF_PYTHON_ROOT_DIR not in sys.path:
    sys.path.append(TOF_PYTHON_ROOT_DIR)

HEX_FILE = os.path.dirname(__file__) + "\\..\\hex\\tmf8829_application.hex"
