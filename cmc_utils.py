import json
import logging
from typing import Any


def fetch_cmc_logger() -> logging.Logger:
	cmc_logger = logging.getLogger(__name__)
	cmc_logger.setLevel(logging.DEBUG)

	file_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt="%d-%b-%y %H:%M:%S")
	stream_formatter = logging.Formatter('%(levelname)s - function: %(funcName)s - %(message)s')

	file_handler = logging.FileHandler('logs/cmc_api.log')
	file_handler.setFormatter(file_formatter)

	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(stream_formatter)

	cmc_logger.addHandler(file_handler)
	cmc_logger.addHandler(stream_handler)

	return cmc_logger


def save_to_json(file_name: str, payload: Any, timestamp: str = "") -> None:
	file_location = f'json_files/{file_name}{timestamp}.json'
	if payload is not None:
		with open(file_location, 'w') as file:
			json.dump(payload, file, indent=6)
	else:
		raise ValueError(f"There is not data to be save on {file_name}{timestamp}.json")
