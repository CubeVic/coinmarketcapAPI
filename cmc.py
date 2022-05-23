import json

import requests
from requests import Session

import cmc_utils
from cmc_helper import Urls, Cryptocurrency, Fiat, Exchange, GlobalMetrics, Tools, Key
from cmc_helper import Cryptocurrency_endpoints_arguments as c_enpoint_args
from cmc_helper import cmc_headers
from abc import ABC, abstractmethod


# prepare for possible changes due to free and paid end points difference.
class Wrapper(ABC):

	cmc_logger = cmc_utils.fetch_cmc_logger()

	def __init__(self, url: str):
		self._base_url = url
		self.request_session = Session()
		self.request_session.headers.update(cmc_headers)

	@property
	def url(self):
		return self._base_url

	@url.setter
	def url(self, value):
		self._base_url = value

	@staticmethod
	def _extract_data_keys(raw_response_data: dict) -> str:
		list_keys = [k for k in raw_response_data['data'][0].keys()]
		return ",".join(list_keys)

	def _response_builder(self, raw_response: str) -> dict:

		json_raw_response = json.loads(raw_response)
		print(f'printing form response builder {json_raw_response}')
		try:
			data = json_raw_response['data']
		except KeyError as e:
			self.cmc_logger.error(f'there is not {e} in the response, possible request error.\n{json_raw_response}')
		else:
			response_timestamp = json_raw_response['status']['timestamp']
			response_cost = json_raw_response['status']['credit_count']
			key_list = self._extract_data_keys(json_raw_response)
			response = {
				'metadata': {
					'timestamp': response_timestamp,
					'credit_count': response_cost,
					'key_list': key_list,
				},
				'data': data}
			return response

	@staticmethod
	def _validate_arguments(expected_args, given_args):
		print(f'expected {expected_args} vs given {given_args}')
		params = {k: v for (k, v) in given_args.items() if v and k in expected_args}
		print(f'here the arguments for the params {params}')
		return params


class Cmc(Wrapper):

	def __init__(self, url: str):
		super().__init__(url)

	def get_map(self, sort: str = 'cmc_rank', listing_status: str = 'active', **kwargs):
		# arg_list = ['listing_status', 'start', 'limit', 'sort', 'symbol', 'aux']
		# creating the params for the string query base in kwargs
		params = self._validate_arguments(expected_args=c_enpoint_args.cmc_id_map_args.value, given_args=kwargs)
		params['sort'] = sort
		params['listing_status'] = listing_status

		endpoint = Cryptocurrency.cmc_id_map.value
		url = self.url + endpoint

		try:
			map_resp = self.request_session.get(url=url, params=params)

		except requests.exceptions.ConnectionError as connection_error:
			self.cmc_logger.error(msg=f'There is something wrong with the connection.\n{connection_error}')
		except requests.exceptions.Timeout as timeout:
			self.cmc_logger.error(msg=f'Timeout. \n{timeout}')

		else:
			response = self._response_builder(raw_response=map_resp.text)
			cmc_utils.save_to_json(file_name='cmc_ids_mapping', payload=response)
			return response


base_url = Urls.sandbox.value
cmc = Cmc(url=base_url)

print(cmc.get_map(listing_status="active",start=1,limit=5000, aux=""))
print(cmc.get_map(listing_status="active",start=1, aux=""))

# adding params as string query
# sq = urllib.parse.urlencode(params, safe=',"')
# response = self.request_session.get(url=url, params=sq)
