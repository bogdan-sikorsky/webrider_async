import os
import sys
import time
import logging
import datetime

from pathlib import Path


def get_logger(log_level: str = 'debug', file_output: bool = False):
    log_lvl = logging.DEBUG
    if log_level == 'debug':
        log_lvl = logging.DEBUG
    elif log_level == 'info':
        log_lvl = logging.INFO
    elif log_level == 'warning':
        log_lvl = logging.WARNING
    elif log_level == 'error':
        log_lvl = logging.ERROR

    logger_format = '%(asctime)s - [%(levelname)s] - %(message)s'
    logging.Formatter.converter = time.gmtime

    current_directory = os.getcwd()
    if file_output:
        log_path = Path(current_directory).joinpath("logs")
        log_file_date = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
        log_file_name = f'log_{log_file_date}.log'
        log_file = Path(log_path).joinpath(log_file_name)

        if not os.path.exists(log_path):
            os.mkdir(log_path)

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
