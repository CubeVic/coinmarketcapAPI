"""Helper functions - Utils"""
import configparser
import json
import logging
from datetime import datetime
from json import JSONDecodeError
from typing import Any
import time
import os


def fetch_cmc_logger(log_file_location: str = "src/logs/",
                     log_file_name: str = "cmc_api.log",
                     log_level: str | int = logging.DEBUG,
                     logger_name: str = __name__) -> logging.Logger:
    """ Set the Log Objects """
    location_file = log_file_location + log_file_name
    string_formatter_file = "%(asctime)s - %(message)s"
    string_formatter_stream = "%(levelname)s - function: %(funcName)s - %(message)s"

    c_logger = logging.getLogger(logger_name)
    c_logger.setLevel(log_level)

    file_formatter = logging.Formatter(
        string_formatter_file, datefmt="%d-%b-%y %H:%M:%S"
    )
    stream_formatter = logging.Formatter(
        string_formatter_stream
    )

    file_handler = logging.FileHandler(location_file)
    file_handler.setFormatter(file_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)

    c_logger.addHandler(file_handler)
    c_logger.addHandler(stream_handler)

    c_logger.propagate = False

    return c_logger


logger = fetch_cmc_logger(log_file_name="cmc_utils.log",
                          log_level=logging.ERROR,
                          logger_name="utils")


def get_todays_timestamp() -> str:
    """Get today's timestamp


    Returns:
            (str): Timestamp when the request was made
    """
    timestamp = str(datetime.utcfromtimestamp(time.time()))
    timestamp = timestamp[0:10].replace("-", "_")

    return timestamp


def save_to_json(file_name: str, payload: Any, timestamp: str = "") -> None:
    """Save to a json file.

    Args:
            file_name (str): name for the file.
            payload (Any):  Data to save on the file.
            timestamp (str, optional): timestamp.

    """

    # You should change 'test' to your preferred folder.
    my_json_directory = "json_files"

    # If folder doesn't exist, then create it.
    if not os.path.isdir(my_json_directory):
        os.makedirs(my_json_directory)
        print("created directory: ", my_json_directory)

    file_location = f"json_files/{file_name}{timestamp}.json"
    if payload is not None:
        with open(file=file_location, mode="w", encoding="utf-8") as file:
            json.dump(payload, file, indent=6)
    else:
        raise ValueError(f"There is not data to be save on {file_name}{timestamp}.json")


def get_info_from_json_file(file_name: str) -> dict | None:
    """Read the json file

    Args:
            file_name (str): nome for the file.

    Returns:
            (dict): information on the json file.
    """

    try:
        with open(file=f"json_files/{file_name}.json", mode="r", encoding="utf-8") as file:
            payload = file.read()
            data_payload = json.loads(payload)
    except FileNotFoundError as error:
        logger.error("The file %s.json doesnt exist\n%s ", file_name, error)
        return None
    except JSONDecodeError as error:
        logger.error("The file %s.json exist but is empty\n%s\n", file_name, error)
        return None
    else:
        return data_payload


def get_cmc_ids() -> str | None:
    """Get the Coin Market Cap ids

    Returns:
            (str): list of ids
    """
    try:
        maps = get_info_from_json_file(file_name="cmc_ids_mapping")
        ids = [str(data["id"]) for data in maps["data"]]
        ids_string = ",".join(ids)

    #     # return ids_string
    except TypeError:
        logger.error(msg="The cmc mapping file doesn't exist")
        return None
    else:
        return ids_string


def create_config_file(file_name: str = 'config.ini'):
    """Create the config file"""
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        "current_day_used": 0,
        "current_day_left": 33,
        "current_month_used": 0,
        "current_month_left": 333,
        "Last_updated": 0,
    }

    with open(file=file_name, mode='w', encoding="utf-8") as configfile:
        config.write(configfile)


def get_configuration_file(name: str = 'config.ini', section: str = 'DEFAULT'):
    """Get the configuration from configuration file and provide and config object to edit them"""

    # You should change 'test' to your preferred folder.
    my_config = 'config.ini'

    # If file doesn't exist, then create it.
    if not os.path.isfile(my_config):
        create_config_file()
        logger.info("created file: %s", my_config)

    config = configparser.ConfigParser()
    config.read(name)
    if section:
        configurations = config[section]
    else:
        configurations = ""
    return config, configurations


def read_configuration_file(config_key: str | bool = False, file: str = 'config.ini'):
    """Read the configuration files and get back the value of the key provided"""

    config, configurations = get_configuration_file(name=file)
    if config_key:
        return config, configurations[config_key]
    return config, configurations


def save_dict_value_to_configuration_file(dict_value):
    """Read the configuration files and get back the value of the key provided

    """

    config, configurations = get_configuration_file()

    for key, value in dict_value.items():
        configurations[key] = f'{value}'

    with open(file='config.ini', mode='w', encoding="utf-8") as configfile:
        config.write(configfile)
