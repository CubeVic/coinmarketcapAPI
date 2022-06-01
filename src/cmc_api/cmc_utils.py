import json
import logging
from datetime import datetime
from typing import Any
import time


def fetch_cmc_logger() -> logging.Logger:
    cmc_logger = logging.getLogger(__name__)
    cmc_logger.setLevel(logging.DEBUG)

    file_formatter = logging.Formatter(
        "%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"
    )
    stream_formatter = logging.Formatter(
        "%(levelname)s - function: %(funcName)s - %(message)s"
    )

    file_handler = logging.FileHandler("logs/cmc_api.log")
    file_handler.setFormatter(file_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)

    cmc_logger.addHandler(file_handler)
    cmc_logger.addHandler(stream_handler)

    return cmc_logger


def get_todays_timestamp() -> str:
    """Get today's timestamp


    Returns:
            (str): Timestamp when the request was made
    """
    t = str(datetime.utcfromtimestamp(time.time()))
    timestamp = t[0:10].replace("-", "_")

    return timestamp


def save_to_json(file_name: str, payload: Any, timestamp: str = "") -> None:
    """Save to a json file.

    Args:
            file_name (str): name for the file.
            payload (Any):  Data to save on the file.
            timestamp (str, optional): timestamp.

    """
    file_location = f"json_files/{file_name}{timestamp}.json"
    if payload is not None:
        with open(file_location, "w") as file:
            json.dump(payload, file, indent=6)
    else:
        raise ValueError(f"There is not data to be save on {file_name}{timestamp}.json")


def get_info_from_json_file(file_name: str) -> dict:
    """Read the json file

    Args:
            file_name (str): nome for the file.

    Returns:
            (dict): information on the json file.
    """
    with open(f"json_files/{file_name}.json", "r") as file:
        payload = file.read()
    return json.loads(payload)


def get_cmc_ids() -> str:
    """Get the Coin Market Cap ids

    Returns:
            (str): list of ids
    """
    maps = get_info_from_json_file(file_name="cmc_ids_mapping")
    ids = [str(data["id"]) for data in maps["data"]]
    ids_string = ",".join(ids)
    return ids_string
