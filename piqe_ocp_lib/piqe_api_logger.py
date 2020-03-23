import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


"""
How to use :
For tests dir :
1) Import piqe_logger class in main conftest.py of project and pass
__loggername__ as an argument.
2) Create a fixture with (scope='session', autouse=True)

i.e.
import pytest
from css_common.lib.logger.piqe_logger import piqe_logger
from css_common.unittests import __loggername__


@pytest.fixture(scope='session', autouse=True)
def setup_logger():
    logger = piqe_logger(__loggername__)
    return logger

For Lib dir :
1) Do this : logger = logging.getLogger(__loggername__)

i.e.
import logging
from css_common.unittests import __loggername__

logger = logging.getLogger(__loggername__)

class ModuleA(object):

    def method_a1(self):
        logger.debug('Message from ModuleA, method_a1')

    def method_a2(self):
        logger.debug('Message from ModuleA, method_a2')

                   OR

For Logger in main conftest.py (project level) :
1) Create logger at project level (main) conftest.py with (scope='session', autouse=True)
"""


LOG_DIR = os.path.join(os.getcwd(), "logs")
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
FILENAME = "piqe_api_logger_{}.log".format(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
FILEPATH = os.path.join(LOG_DIR, FILENAME)


class piqe_api_logger(object):
    _logger = None

    def __new__(cls, *args, **kwargs):
        if cls._logger is None:
            cls._logger = super(piqe_api_logger, cls).__new__(cls)
            # Put any initialization here.
            cls._logger = logging.getLogger(args[0])
            cls._logger.setLevel(logging.DEBUG)

            # Create a file handler for logging level above DEBUG
            file_handler = RotatingFileHandler(FILEPATH, maxBytes=1024 * 1024 * 1024, backupCount=20)

            # Create a logging format
            log_formatter = logging.Formatter(
                '%(asctime)s - '
                '[%(levelname)s] - '
                '%(name)s - '
                '%(module)s@%(funcName)s:%(lineno)d - '
                '%(message)s')
            file_handler.setFormatter(log_formatter)

            # Create a stream handler for logging level above INFO
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            stream_handler.setFormatter(log_formatter)

            # Add the handlers to the logger
            cls._logger.addHandler(file_handler)
            cls._logger.addHandler(stream_handler)

        return cls._logger
