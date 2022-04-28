import os
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time
from datetime import datetime
import logging


def _configure_cmc_logger():
	global cmc_logger
	cmc_logger = logging.getLogger(__name__)
	cmc_logger.setLevel(logging.DEBUG)

	file_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt="%d-%b-%y %H:%M:%S")
	stream_formatter = logging.Formatter('%(levelname)s - function: %(funcName)s - %(message)s')

	file_handler = logging.FileHandler('cmc_api.log')
	file_handler.setFormatter(file_formatter)

	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(stream_formatter)

	cmc_logger.addHandler(file_handler)
	cmc_logger.addHandler(stream_handler)


def cnc_configuration():
	_configure_cmc_logger()
	global CNC_API_KEY
	global BASE_URL
	global SANDBOX_URL
	global HEADERS
	global cmc_logger
	CNC_API_KEY = os.environ['COIN_API_KEY']
	BASE_URL = 'https://pro-api.coinmarketcap.com'
	SANDBOX_URL = 'https://sandbox-api.coinmarketcap.com'
	HEADERS = {
		'Accepts': 'application/json',
		'X-CMC_PRO_API_KEY': CNC_API_KEY,
	}
	cmc_logger.info(f'Starting script')


def prepare_session() -> Session:
	request_session = Session()
	request_session.headers.update(HEADERS)
	return request_session


def get_time() -> datetime:
	t = datetime.utcfromtimestamp(time.time())
	return t


def get_updated_prices_from_cmc() -> dict:
	""" Query the APi for the latest prices, it consumes credits.

	:param: request_session
	:return: json
	"""
	request_session = prepare_session()
	timestamp = str(get_time())[0:10].replace("-", "_")
	if os.path.exists(f"price-{timestamp}.json"):
		cmc_logger.info(f'JSON File already exist: price-{timestamp}.json')
		data = get_price_from_json_file(timestamp)
		cmc_logger.debug(f"Date obtained from Json file\n{data}")
		return {
			'timestamp': data['timestamp'],
			'data': data['data']
		}
	else:
		params = {
			'start': '1',
			'limit': '1000',
			'convert': 'USD',
		}
		endpoint = '/v1/cryptocurrency/listings/latest'
		url = BASE_URL + endpoint
		# url = SANDBOX_URL + endpoint
		try:
			response = request_session.get(url, params=params)
		except (ConnectionError, Timeout, TooManyRedirects) as e:
			cmc_logger.error(f"error with the connection to CMC API\n{e}")
		else:
			data = json.loads(response.text)
			cmc_logger.info(f'Error Message: {data["status"]["error_message"]}, '
			                f'Error code: {data["status"]["error_code"]},'
			                f'status: {data["status"]["timestamp"]}')

			timestamp = data['status']['timestamp'].replace("-", "_").replace(":", "_")
			timestamp = timestamp[0:10]

			result = {
				'timestamp': data['status']['timestamp'],
				'data': data['data']
			}

			with open(f'price-{timestamp}.json', 'w') as file:
				json.dump(result, file, indent=6)
				cmc_logger.info(f'File created: price-{timestamp}.json')

			return {
				'timestamp': data['status']['timestamp'],
				'data': data['data']
			}


def get_map():
	request_session = prepare_session()
	if os.path.exists(f"map.json"):
		cmc_logger.info('File map already exist')
	else:
		endpoint = '/v1/cryptocurrency/map'
		url = BASE_URL + endpoint
		params = {
			'sort': 'cmc_rank',
		}
		map_resp = request_session.get(url=url, params=params)
		cmc_map = json.loads(map_resp.text)
		with open('map.json', 'w') as file:
			json.dump(cmc_map['data'], file, indent=6)
			cmc_logger.info(f'creating map.json file')


def get_price_from_json_file(timestamp: str) -> dict:
	with open(f'price-{timestamp}.json', 'r') as file:
		payload = json.loads(file.read())
	return payload

