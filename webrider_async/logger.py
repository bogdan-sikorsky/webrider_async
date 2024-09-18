import os
import sys
import time
import logging
import datetime

from pathlib import Path


def get_logger(log_level: str = 'debug', file_output: bool = False, log_dir: str = None):
    # Define log level mapping
    log_lvl = logging.DEBUG
    if log_level == 'debug':
        log_lvl = logging.DEBUG
    elif log_level == 'info':
        log_lvl = logging.INFO
    elif log_level == 'warning':
        log_lvl = logging.WARNING
    elif log_level == 'error':
        log_lvl = logging.ERROR
    else:
        print("""---UNRECOGNIZED LOG LEVEL, APPLYING DEFAULT LOG LEVEL---""")


    logger_format = '%(asctime)s - [%(levelname)s] - %(message)s'
    logging.Formatter.converter = time.gmtime

    # Set the default log directory to project root if not provided
    if file_output:
        # If log_dir is not specified, use the project root
        if log_dir is None:
            log_dir = os.getcwd()  # Project root directory

        log_path = Path(log_dir).joinpath("webrider_logs")  # Default "logs" folder
        log_file_date = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
        log_file_name = f'log_{log_file_date}.log'
        log_file = Path(log_path).joinpath(log_file_name)

        # Create the log directory if it doesn't exist
        if not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)

        logging.basicConfig(
            level=log_lvl,
            format=logger_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    else:
        logging.basicConfig(
            level=log_lvl,
            format=logger_format,
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )

    return logging.getLogger()
