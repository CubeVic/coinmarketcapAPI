import os
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time
from datetime import datetime
import logging
import enum

import urllib.parse


class Cryptocurrency(enum.Enum):
	cmc_id_map = '/v1/cryptocurrency/map'
	latest_list_price = '/v1/cryptocurrency/listings/latest'
	info = '/v2/cryptocurrency/info'
	quote_latest= '/v2/cryptocurrency/quotes/latest'


class CmcApi:
	BASE_URL = 'https://pro-api.coinmarketcap.com'
	SANDBOX_URL = 'https://sandbox-api.coinmarketcap.com'

	timestamp = str(datetime.utcfromtimestamp(time.time()))[0:10].replace("-", "_")

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

	def __init__(self, cmc_api, is_sandbox_url):
		self.cmc_logger.info(f'Starting CMC')
		self.HEADERS = {
			'Accepts': 'application/json',
			'X-CMC_PRO_API_KEY': cmc_api,
		}
		self.is_sandbox_url = is_sandbox_url
		self.uri = ""
		self.request_session = Session()
		self.request_session.headers.update(self.HEADERS)

	@property
	def is_sandbox_url(self):
		return self.uri

	@is_sandbox_url.setter
	def is_sandbox_url(self, is_sandbox_url):
		if is_sandbox_url:
			self.cmc_logger.info(f'Setting the Sandbox URL {self.SANDBOX_URL}')
			self.uri = self.SANDBOX_URL
		else:
			self.cmc_logger.info(f'Setting the URL {self.BASE_URL}')
			self.uri = self.BASE_URL

	@staticmethod
	def _get_price_from_json_file(timestamp: str) -> dict:
		with open(f'json_files/price-{timestamp}.json', 'r') as file:
			payload = json.loads(file.read())
		return payload

	@staticmethod
	def _get_info_from_json_file() -> dict:
		with open(f'json_files/info.json', 'r') as file:
			payload = file.read()
		print(f"payload ..... {payload}")
		return payload

	def get_map(self, sort: str = 'cmc_rank'):

		if os.path.exists(f"map.json"):
			self.cmc_logger.info('File map already exist')
		else:
			# endpoint = '/v1/cryptocurrency/map'
			endpoint = Cryptocurrency.cmc_id_map.value
			url = self.BASE_URL + endpoint
			params = {
				'sort': sort,
			}
			map_resp = self.request_session.get(url=url, params=params)
			cmc_map = json.loads(map_resp.text)
			with open('map.json', 'w') as file:
				json.dump(cmc_map['data'], file, indent=6)
				self.cmc_logger.info(f'creating map.json file')

	def get_updated_prices_from_cmc(self, start: str = '1', limit: str = '1000', convert: str = 'USD') -> dict:
		""" Query the APi for the latest prices, it consumes credits.

		:param: request_session
		:return: json
		"""

		if os.path.exists(f"json_files/price-{self.timestamp}.json"):
			self.cmc_logger.debug(f'JSON File already exist: price-{self.timestamp}.json')
			data = self._get_price_from_json_file(self.timestamp)
			self.cmc_logger.debug(f"Date obtained from Json file")

			return {
				'timestamp': data['timestamp'],
				'data': data['data']
			}
		else:
			params = {
				'start': start,
				'limit': limit,
				'convert': convert,
			}

			endpoint = Cryptocurrency.latest_list_price.value
			url = self.SANDBOX_URL + endpoint if self.is_sandbox_url else self.BASE_URL + endpoint
			try:
				response = self.request_session.get(url, params=params)
			except (ConnectionError, Timeout, TooManyRedirects) as e:
				self.cmc_logger.error(f"error with the connection to CMC API\n{e}")
			else:
				data = json.loads(response.text)
				self.cmc_logger.debug(f'There is an Error{data["status"]["error_message"]} {data["status"]["error_code"]}')

				timestamp = data['status']['timestamp'].replace("-", "_").replace(":", "_")
				timestamp = timestamp[0:10]

				result = {
					'timestamp': data['status']['timestamp'],
					'data': data['data']
				}

				with open(f'json_files/price-{timestamp}.json', 'w') as file:
					json.dump(result, file, indent=6)
					self.cmc_logger.info(f'File created: price-{timestamp}.json')

				return result

	def get_info(self, id: str= '1', info_aux: str = 'urls,logo,description,tags,platform,date_added,notice,status' ):
		if id == "":
			raise Exception

		if os.path.exists(f'json_files/info.json'):
			self.cmc_logger.debug('File info already exist')
			data = self._get_info_from_json_file()
			results = {
				'timestamp': data['status']['timestamp'],
				'data': data['data']
			}

		else:
			params = {'id': id[:-1],
					'aux': info_aux,
					}

			endpoint = Cryptocurrency.info.value
			url = self.SANDBOX_URL + endpoint if self.is_sandbox_url else self.BASE_URL + endpoint

			# adding params as string query
			sq = urllib.parse.urlencode(params, safe=',"')
			response = self.request_session.get(url=url, params=sq)
			print(f' is this the data {response.url}')

			data = json.loads(response.text)
			print(f'response {data}')
			results = {
				'timestamp': data['status']['timestamp'],
				'data': data['data']
			}

		with open(f'json_files/info.json', 'w') as file:
			json.dump(results, file, indent=6)
			self.cmc_logger.info(f'File created: info.json')

		return results
