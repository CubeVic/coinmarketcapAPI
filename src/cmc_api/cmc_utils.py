"""Helper functions - Utils"""
import configparser
import enum
import json
import logging
from datetime import datetime
from json import JSONDecodeError
from typing import Any, Protocol, Callable
import time
import os
from urllib import parse

from requests import exceptions


def fetch_cmc_logger(
    log_file_location: str = "../logs/",
    log_file_name: str = "cmc_api.log",
    log_level: str | int = logging.DEBUG,
    logger_name: str = __name__,
) -> logging.Logger:
    """Set the Log Objects"""

    if not os.path.isdir(log_file_location):
        os.makedirs(name="../logs")

    location_file = log_file_location + log_file_name
    string_formatter_file = "%(asctime)s - %(message)s"
    string_formatter_stream = "%(levelname)s - function: %(funcName)s - %(message)s"

    c_logger = logging.getLogger(logger_name)
    c_logger.setLevel(log_level)

    file_formatter = logging.Formatter(
        string_formatter_file, datefmt="%d-%b-%y %H:%M:%S"
    )
    stream_formatter = logging.Formatter(string_formatter_stream)

    file_handler = logging.FileHandler(location_file)
    file_handler.setFormatter(file_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)

    c_logger.addHandler(file_handler)
    c_logger.addHandler(stream_handler)

    c_logger.propagate = False

    return c_logger


logger = fetch_cmc_logger(
    log_file_name="cmc_utils.log", log_level=logging.ERROR, logger_name="utils"
)


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
        with open(
            file=f"json_files/{file_name}.json", mode="r", encoding="utf-8"
        ) as file:
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


def create_config_file(file_name: str = "config.ini"):
    """Create the config file"""
    config = configparser.ConfigParser()
    config["DEFAULT"] = {
        "current_day_used": 0,
        "current_day_left": 33,
        "current_month_used": 0,
        "current_month_left": 333,
        "Last_updated": 0,
    }

    with open(file=file_name, mode="w", encoding="utf-8") as configfile:
        config.write(configfile)


def get_configuration_file(name: str = "config.ini", section: str = "DEFAULT"):
    """Get the configuration from configuration file and provide and config object to edit them"""

    # You should change 'test' to your preferred folder.
    my_config = "config.ini"

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


def read_configuration_file(config_key: str | bool = False, file: str = "config.ini"):
    """Read the configuration files and get back the value of the key provided"""

    config, configurations = get_configuration_file(name=file)
    if config_key:
        return config, configurations[config_key]
    return config, configurations


def save_dict_value_to_configuration_file(dict_value):
    """Read the configuration files and get back the value of the key provided"""

    config, configurations = get_configuration_file()

    for key, value in dict_value.items():
        configurations[key] = f"{value}"

    with open(file="config.ini", mode="w", encoding="utf-8") as configfile:
        config.write(configfile)


def _check_args(exp_args: Any, given_args: dict) -> dict:
    logger.debug(
        f"Validating args:\nexpected {exp_args} vs given {list(given_args.keys())}"
    )
    params = {k: v for (k, v) in given_args.items() if v and k in exp_args}
    logger.debug(f"params to be used: {params}")
    return params


class DataHandler(Protocol):
    @staticmethod
    def data_extraction(payload: dict) -> (dict, Any):
        ...

    @staticmethod
    def response_builder(raw_resp: str, ext_method: Callable[[dict], Any]) -> dict:
        ...


def prepare_request(url, uri_and_args, params) -> (str, str):
    """Prepare safe parameters and the full URL"""

    endpoint, endpoint_args = uri_and_args.value
    _params = _check_args(exp_args=endpoint_args, given_args=params)

    # Make ' and , safe characters
    safe_param = parse.urlencode(_params, safe=',"')

    url_endpoint = url + endpoint

    return url_endpoint, safe_param


def fetch_data(
    request_session,
    url: str,
    uri_and_args: enum.Enum,
    params: dict,
    data_handler_class: DataHandler,
) -> tuple[int, dict]:
    """Fetch will do the request to the end point provided and extract
    the information with the extraction function

    Args:
            request_session (request):
            url (str):
            uri_and_args (enum.Enum):
            params (dict): Parameters for the search query.
            data_handler_class (DataHandler): class that will extract the information.

    Returns:
            (tuple[int, dict]): response contain the http code and the data

    """

    url_endpoint, safe_param = prepare_request(
        url=url, uri_and_args=uri_and_args, params=params
    )

    try:

        map_resp = request_session.get(url=url_endpoint, params=safe_param)
        if map_resp.status_code == 414:
            raise exceptions.HTTPError(f"414 Request-URI Too Large\n{map_resp.url}")
    except exceptions.ConnectionError as connection_error:
        logger.error(
            msg="There is something wrong with the connection.\n%s" % connection_error
        )

    except exceptions.Timeout as timeout:
        logger.error(msg="Timeout \n%s" % timeout)

    except exceptions.HTTPError as e:
        logger.error(msg="error %s" % e)
        return 414, "error"
    else:
        logger.debug(msg="response => %s" % map_resp.status_code)
        raw_response = map_resp.text
        status_code = map_resp.status_code
        response = data_handler_class.response_builder(
            raw_resp=raw_response, ext_method=data_handler_class.data_extraction
        )
        return status_code, response


def update_configuration_file(value_to_add: dict) -> None:
    values = {
        "current_day_used": value_to_add["data"]["usage"]["current_day"][
            "credits_used"
        ],
        "current_day_left": value_to_add["data"]["usage"]["current_day"][
            "credits_left"
        ],
        "current_month_used": value_to_add["data"]["usage"]["current_month"][
            "credits_left"
        ],
        "current_month_left": value_to_add["data"]["usage"]["current_month"][
            "credits_left"
        ],
        "Last_updated": value_to_add["metadata"]["timestamp"],
    }
    save_dict_value_to_configuration_file(values)
