import json
import urllib
from typing import Any

import requests
from requests import Session

import cmc_utils
from cmc_helper import Urls, Cryptocurrency, Fiat, Exchange, GlobalMetrics, Tools, Key
from cmc_helper import CryptocurrencyEndPointsArgs as Crypto_endpoint_args
from cmc_helper import cmc_headers
from abc import ABC, abstractmethod
from collections.abc import Callable

http_code = int()
response_content_json = dict()


def extraction_data_list(payload: dict) -> (dict, list):
    """Data value in the response contain a list of dictionaries"""
    metadata = {"timestamp": payload["status"]["timestamp"],
                "credit_count": payload["status"]["credit_count"],
                "error_message": payload["status"]["error_message"],
                "list_keys": [k for k in payload["data"][0].keys()]}
    data = payload["data"]
    return metadata, data


def extraction_data_dict(payload: dict) -> (dict, dict):
    """Data value in the response contain a dictionary each key of the dictionary represent an item,
    item can have a dictionary inside"""

    metadata = {"timestamp": payload["status"]["timestamp"],
                "credit_count": payload["status"]["credit_count"],
                "error_message": payload["status"]["error_message"],
                }
    dict_keys = list(payload["data"].values())[0]
    print(f' type: {dict_keys}\n {dict_keys}')
    list_keys = list(dict_keys.keys())
    metadata["list_keys"] = list_keys
    data = payload["data"]
    return metadata, data


def extraction_data_nested_list(payload: dict) -> (dict, dict):
    """Data value in the response contain a data key that contain a list of dictionaries"""

    metadata = {"timestamp": payload["status"]["timestamp"],
                "credit_count": payload["status"]["credit_count"],
                "error_message": payload["status"]["error_message"],
                "list_keys": [k for k in payload["data"]["data"][0].keys()]}

    data = payload["data"]["data"]
    return metadata, data

def extraction_data_single_dict(payload: dict) -> (dict, dict):
    """Data value in the response contain the information in a dictionary form

     These responses are mostly about one specific item, not several
     """
    metadata = {"timestamp": payload["status"]["timestamp"],
                "credit_count": payload["status"]["credit_count"],
                "error_message": payload["status"]["error_message"],
                "list_keys": [k for k in payload["data"].keys()]}
    data = payload["data"]
    return metadata, data

def extration_data_original_format(payload: dict) -> (dict, dict):
    metadata = payload["status"]
    data = payload["data"]
    return metadata, data


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

    # @staticmethod
    # def _extract_data_keys(raw_response_data: dict) -> str:
    #     print(raw_response_data["data"])
    #     # some response contains list of dict-like object other are nested dict-like items
    #     if type(raw_response_data["data"]) == list:
    #         list_keys = [k for k in raw_response_data["data"][0].keys()]
    #     else:
    #         print(type(raw_response_data["data"]))
    #         if raw_response_data["data"].get("data", False):
    #             list_keys = [k for k in raw_response_data["data"]["data"][0].keys()]
    #         else:
    #             dict_keys = list(raw_response_data["data"].values())[0]
    #             print(f' type: {dict_keys}\n {dict_keys}')
    #             list_keys = list(dict_keys.keys())
    #
    #     return ",".join(list_keys)

    # Use template patter to implement the extract data keys and _response_builder

    # def _response_builder(self, raw_response: str) -> dict:
    #
    #     response = {}
    #     print(raw_response)
    #     json_raw_response = json.loads(raw_response)
    #     try:
    #         data = json_raw_response["data"]
    #     except KeyError as e:
    #         self.cmc_logger.error(
    #             f"there is not {e} in the response, possible request error.\n{json_raw_response}"
    #         )
    #     else:
    #         response_timestamp = json_raw_response["status"]["timestamp"]
    #         response_cost = json_raw_response["status"]["credit_count"]
    #         key_list = self._extract_data_keys(json_raw_response)
    #         response["metadata"] = {
    #                 "timestamp": response_timestamp,
    #                 "credit_count": response_cost,
    #                 "key_list": key_list,
    #             }
    #
    #         if type(data) == list:
    #             response["data"] = data
    #         else:
    #             if data.get("data", False):
    #                 response["data"] = data["data"]
    #             else:
    #                 response["data"] = data
    #
    #         return response

    def _response_builder(self, raw_response: str, extract_method: Callable[[dict],(dict,Any)]) -> dict:

        response = {"metadata": {},
                    "data": {}
                    }
        print(raw_response)
        json_raw_response = json.loads(raw_response)

        metadata, data = extract_method(payload=json_raw_response)
        response["metadata"] = metadata
        response["data"] = data

        return response


    @staticmethod
    def _validate_args(expected_args, given_args):
        print(
            f"Validating args:\nexpected {expected_args} vs given {list(given_args.keys())}"
        )
        params = {k: v for (k, v) in given_args.items() if v and k in expected_args}
        print(f"params {params}")
        return params

    def fetch_data(self, endpoint: str, params: dict, extract_method) -> (http_code, response_content_json):

        url_endpoint = self.url + endpoint
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
            self.cmc_logger.info(msg=f"response => {map_resp.status_code}")
            return map_resp.status_code, self._response_builder(raw_response=map_resp.text,extract_method=extract_method) # until template for extration data finished
            # return map_resp.status_code, map_resp.text



class Cmc(Wrapper):
    def __init__(self, url: str):
        super().__init__(url)

    def get_cmc_id_map(
        self, sort: str = "cmc_rank", listing_status: str = "active", **kwargs
    ):
        # arg_list = ['listing_status', 'start', 'limit', 'sort', 'symbol', 'aux']
        # creating the params for the string query base in kwargs
        kwargs["sort"] = sort
        kwargs["listing_status"] = listing_status
        params = self._validate_args(
            expected_args=Crypto_endpoint_args.id_map_args.value, given_args=kwargs
        )

        endpoint = Cryptocurrency.cmc_id_map.value

        _, response = self.fetch_data(endpoint=endpoint, params=params, extract_method=extraction_data_list)

        cmc_utils.save_to_json(file_name="cmc_ids_mapping", payload=response)
        return response

    def get_info(self, cmc_id: str, **kwargs):
        # id, slug, symbol, address, aux
        kwargs["id"] = cmc_id
        params = self._validate_args(
            expected_args=Crypto_endpoint_args.info_arg.value, given_args=kwargs
        )

        endpoint = Cryptocurrency.info.value
        url = self.url + endpoint

        _, response = self.fetch_data(endpoint=endpoint, params=params, extract_method=extraction_data_dict)

        cmc_utils.save_to_json(file_name="info", payload=response)
        return response

    def get_listing(self, start: int, limit: int, **kwargs):
        # In base Plan of the API this end point accept just one currency convert
        kwargs["start"] = start
        kwargs["limit"] = limit
        params = self._validate_args(
            expected_args=Crypto_endpoint_args.list_price_args.value, given_args=kwargs
        )

        endpoint = Cryptocurrency.latest_list_price.value
        url = self.url + endpoint

        _, response = self.fetch_data(endpoint=endpoint, params=params,extract_method=extraction_data_list)
        timestamp = cmc_utils.get_todays_timestamp()

        cmc_utils.save_to_json(
            file_name=f"latest_listing_{timestamp} ", payload=response
        )
        return response

    def get_categories(self, start: int, limit: int, **kwargs):
        """ Get the categories

        Get the coin categories form CoinmarketCap

        Args:
            start (int):
            limit (int):

        """

        kwargs["start"] = start
        kwargs["limit"] = limit
        params = self._validate_args(expected_args=Crypto_endpoint_args.categories_args.value, given_args=kwargs)

        endpoint = Cryptocurrency.categories.value

        _, response = self.fetch_data(endpoint=endpoint, params=params, extract_method=extraction_data_list)
        # cmc_utils.save_to_json(file_name="test", payload=response)
        cmc_utils.save_to_json(file_name=f"categories", payload=response)
        return response

    def get_category(self, cmc_id: str, **kwargs):
        """ Get information of a single category

        Args:
            cmc_id (str): Then Category ID given by Coin market Cap. on the API is named id.
            **kwargs (Any): Can be used to pass the other supported parameter in this endpoint.

                    -> start (int, optional): >=1 Optionally offset the start (1-based index) of the paginated list of
                        coins to return.
                    -> limit (int, optional): [1 .. 1000] Optionally specify the number of coins to return.
                        Use this parameter and the "start" parameter to determine your own pagination size.
                    -> convert (str): Optionally calculate market quotes in up to 120 currencies at once by passing a
                        comma-separated list of cryptocurrency or fiat currency symbols.
                        Each additional convert option beyond the first requires an additional call credit. A list of
                        supported fiat options can be found here. Each conversion is returned in its own "quote" object.
                    -> convert_id (str): Optionally calculate market quotes by CoinMarketCap ID instead of symbol.
                        This option is identical to convert outside of ID format. Ex: convert_id=1,2781 would
                        replace convert=BTC,USD in your query. This parameter cannot be used when convert is used.


        """
        kwargs["id"] = cmc_id

        params = self._validate_args(expected_args=Crypto_endpoint_args.category_args.value, given_args=kwargs)

        endpoint = Cryptocurrency.category.value

        _, response = self.fetch_data(endpoint=endpoint, params=params, extract_method=extraction_data_single_dict)

        cmc_utils.save_to_json(file_name=f"category_{response['data']['title']}", payload=response)
        return response




base_url = Urls.sandbox.value
# base_url = Urls.base.value
cmc = Cmc(url=base_url)


# cmc.get_cmc_id_map(listing_status="active", start=1, limit=1000)
# ids_string = cmc_utils.get_cmc_ids()
# print(len(ids_string))
# cmc.get_info(cmc_id=ids_string)
# cmc.get_listing(start=1, limit=1000, convert="USD")
#
# cmc.get_categories(start=1, limit=5000)
# cmc.get_category(cmc_id="625d09d246203827ab52dd53")

