import json
import urllib

import requests
from requests import Session

import cmc_utils
from cmc_helper import Urls, Cryptocurrency, Fiat, Exchange, GlobalMetrics, Tools, Key
from cmc_helper import CryptocurrencyEndPointsArgs as Crypto_endpoint_args
from cmc_helper import cmc_headers
from abc import ABC, abstractmethod

http_code = int()
response_content_json = dict()


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

        # some response contains list of dict-like object other are nested dict-like items
        if type(raw_response_data["data"]) == list:
            list_keys = [k for k in raw_response_data["data"][0].keys()]
        else:
            dict_keys = list(raw_response_data["data"].values())[0]
            list_keys = list(dict_keys.keys())

        return ",".join(list_keys)

    def _response_builder(self, raw_response: str) -> dict:

        json_raw_response = json.loads(raw_response)
        try:
            data = json_raw_response["data"]
        except KeyError as e:
            self.cmc_logger.error(
                f"there is not {e} in the response, possible request error.\n{json_raw_response}"
            )
        else:
            response_timestamp = json_raw_response["status"]["timestamp"]
            response_cost = json_raw_response["status"]["credit_count"]
            key_list = self._extract_data_keys(json_raw_response)
            response = {
                "metadata": {
                    "timestamp": response_timestamp,
                    "credit_count": response_cost,
                    "key_list": key_list,
                },
                "data": data,
            }
            return response

    @staticmethod
    def _validate_args(expected_args, given_args):
        print(f"Validating args:\nexpected {expected_args} vs given {list(given_args.keys())}")
        params = {k: v for (k, v) in given_args.items() if v and k in expected_args}
        print(f"params {params}")
        return params

    def fetch_data(self, url_endpoint: str, params: str) -> (http_code, response_content_json):
        try:
            # Make ' and , safe characters
            param_sq = urllib.parse.urlencode(params, safe=',"')
            map_resp = self.request_session.get(url=url_endpoint, params=param_sq)

        except requests.exceptions.ConnectionError as connection_error:
            self.cmc_logger.error(
                msg=f"There is something wrong with the connection.\n{connection_error}"
            )
        except requests.exceptions.Timeout as timeout:
            self.cmc_logger.error(msg=f"Timeout. \n{timeout}")

        else:
            self.cmc_logger.info(msg=f'response => {map_resp.status_code}')
            print(params)
            print(map_resp.url)
            return map_resp.status_code, self._response_builder(map_resp.text)


class Cmc(Wrapper):
    def __init__(self, url: str):
        super().__init__(url)

    def get_cmc_id_map(self, sort: str = "cmc_rank", listing_status: str = "active", **kwargs):
        # arg_list = ['listing_status', 'start', 'limit', 'sort', 'symbol', 'aux']
        # creating the params for the string query base in kwargs
        kwargs['sort'] = sort
        kwargs['listing_status'] = listing_status
        params = self._validate_args(expected_args=Crypto_endpoint_args.id_map_args.value, given_args=kwargs)

        endpoint = Cryptocurrency.cmc_id_map.value
        url = self.url + endpoint

        _, response = self.fetch_data(url_endpoint=url, params=params)

        cmc_utils.save_to_json(file_name="cmc_ids_mapping", payload=response)
        return response

    def get_info(self, cmc_id: str, **kwargs):
        # id, slug, symbol, address, aux
        kwargs["id"] = cmc_id
        params = self._validate_args(expected_args=Crypto_endpoint_args.info_arg.value, given_args=kwargs)

        endpoint = Cryptocurrency.info.value
        url = self.url + endpoint

        _, response = self.fetch_data(url_endpoint=url, params=params)

        cmc_utils.save_to_json(file_name="info", payload=response)
        return response

    def get_listing(self, start: int, limit: int, **kwargs):
        # In base Plan of the API this end point accept just one currency convert
        kwargs["start"] = start
        kwargs["limit"] = limit
        params = self._validate_args(expected_args=Crypto_endpoint_args.list_price.value, given_args=kwargs)

        endpoint = Cryptocurrency.latest_list_price.value
        url = self.url + endpoint

        _, response = self.fetch_data(url_endpoint=url, params=params)
        timestamp = cmc_utils._get_todays_timestamp()

        cmc_utils.save_to_json(file_name=f"latest_listing_{timestamp}", payload=response)
        return response



# base_url = Urls.sandbox.value
base_url = Urls.base.value
cmc = Cmc(url=base_url)

# cmc.get_cmc_id_map(listing_status="active", start=1, limit=1000, aux="")
# print(cmc.get_map(listing_status="active", start=1, aux=""))

ids_string = cmc_utils.get_cmc_ids()

# cmc.get_info(cmc_id=ids_string)
# cmc.get_listing(start=1, limit=1000, convert_id="2820")
cmc.get_listing(start=1, limit=1000, convert="USD")




# adding params as string query
# sq = urllib.parse.urlencode(params, safe=',"')
# response = self.request_session.get(url=url, params=sq)
