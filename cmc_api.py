import os
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time
from datetime import datetime
import logging


class CmcApi:
	BASE_URL = 'https://pro-api.coinmarketcap.com'
	SANDBOX_URL = 'https://sandbox-api.coinmarketcap.com'

	timestamp = str(datetime.utcfromtimestamp(time.time()))[0:10].replace("-", "_")

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

	def __init__(self, cmc_api, is_sandbox_url):
		self.cmc_logger.info(f'Starting CMC')
		self._cmc_api = cmc_api
		self.HEADERS = {
			'Accepts': 'application/json',
			'X-CMC_PRO_API_KEY': self._cmc_api,
		}
		self._is_sandbox_url = is_sandbox_url
		self.uri = ""
		self.request_session = Session()
		self.request_session.headers.update(self.HEADERS)

	@property
	def cmc_api(self):
		return "key"

	@cmc_api.setter
	def cmc_api(self, cmc_api):
		self.cmc_logger.info('Adding key')
		self._cmc_api = cmc_api

	@cmc_api.deleter
	def cmc_api(self):
		del self.cmc_api

	@property
	def is_sandbox_url(self):
		return self._is_sandbox_url

	@is_sandbox_url.setter
	def is_sandbox_url(self, is_sandbox_url):
		if is_sandbox_url:
			self.cmc_logger.info(f'Setting the Sandbox URL {self.SANDBOX_URL}')
			self.uri = self.SANDBOX_URL
		else:
			self.cmc_logger.info(f'Setting the URL {self.BASE_URL}')
			self.uri = self.BASE_URL

	def get_updated_prices_from_cmc(self) -> dict:
		""" Query the APi for the latest prices, it consumes credits.

		:param: request_session
		:return: json
		"""

		if os.path.exists(f"price-{self.timestamp}.json"):
			self.cmc_logger.info(f'JSON File already exist: price-{self.timestamp}.json')
			data = self._get_price_from_json_file(self.timestamp)
			self.cmc_logger.debug(f"Date obtained from Json file\n{data}")
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
			url = self.SANDBOX_URL + endpoint if self.is_sandbox_url else self.BASE_URL + endpoint
			try:
				response = self.request_session.get(url, params=params)
			except (ConnectionError, Timeout, TooManyRedirects) as e:
				self.cmc_logger.error(f"error with the connection to CMC API\n{e}")
			else:
				data = json.loads(response.text)
				self.cmc_logger.info(f'Error Message: {data["status"]["error_message"]}, '
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
					self.cmc_logger.info(f'File created: price-{timestamp}.json')

				return {
					'timestamp': data['status']['timestamp'],
					'data': data['data']
				}

	def get_map(self):

		if os.path.exists(f"map.json"):
			self.cmc_logger.info('File map already exist')
		else:
			endpoint = '/v1/cryptocurrency/map'
			url = self.BASE_URL + endpoint
			params = {
				'sort': 'cmc_rank',
			}
			map_resp = self.request_session.get(url=url, params=params)
			cmc_map = json.loads(map_resp.text)
			with open('map.json', 'w') as file:
				json.dump(cmc_map['data'], file, indent=6)
				self.cmc_logger.info(f'creating map.json file')

	@staticmethod
	def _get_price_from_json_file(timestamp: str) -> dict:
		with open(f'price-{timestamp}.json', 'r') as file:
			payload = json.loads(file.read())
		return payload
