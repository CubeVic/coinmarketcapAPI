import os
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time
from datetime import datetime
import logging
import enum

import urllib.parse


def configure_logger():
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


class Cryptocurrency(enum.Enum):
    cmc_id_map = "/v1/cryptocurrency/map"
    latest_list_price = "/v1/cryptocurrency/listings/latest"
    info = "/v2/cryptocurrency/info"


class CmcApi:
    BASE_URL = "https://pro-api.coinmarketcap.com"
    SANDBOX_URL = "https://sandbox-api.coinmarketcap.com"

    timestamp = str(datetime.utcfromtimestamp(time.time()))[0:10].replace("-", "_")
    cmc_logger = configure_logger()

    def __init__(self, cmc_api, is_sandbox_url):
        self.cmc_logger.info(f"Starting CMC")
        self.HEADERS = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": cmc_api,
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
        """Sets the domain for the end point as sandbox if the option is true"""
        if is_sandbox_url:
            self.cmc_logger.info(f"Setting the Sandbox URL {self.SANDBOX_URL}")
            self.uri = self.SANDBOX_URL
        else:
            self.cmc_logger.info(f"Setting the URL {self.BASE_URL}")
            self.uri = self.BASE_URL

    @staticmethod
    def _get_from_json_file(name: str, timestamp: str) -> any:
        if os.path.exists(f"json_files/{name}-{timestamp}.json"):
            with open(f"{name}-{timestamp}.json", "r") as file:
                payload = json.loads(file.read())
                return {"timestamp": payload["timestamp"], "data": payload["data"]}
        return False

    @staticmethod
    def _write_to_json_file(name: str, timestamp: str, payload: any):
        """Write payload in a json file"""
        with open(f"json_files/{name}-{timestamp}.json", "w") as file:
            json.dump(payload, file, indent=6)
            print(f"File created: {name}-{timestamp}.json")

    def get_map(self, sort: str = "cmc_rank"):

        endpoint = Cryptocurrency.cmc_id_map.value
        url = self.BASE_URL + endpoint
        params = {
            "sort": sort,
        }
        map_resp = self.request_session.get(url=url, params=params)
        results = json.loads(map_resp.text)

        self._write_to_json_file(name="cmc_map", timestamp=self.timestamp, payload=results)
        return results

    def get_updated_prices(
        self, start: str = "1", limit: str = "1000", convert: str = "USD"
    ) -> dict:
        """Query the APi for the latest prices, it consumes credits.

        :param: request_session
        :return: json
        """
        params = {
            "start": start,
            "limit": limit,
            "convert": convert,
        }
        endpoint = Cryptocurrency.latest_list_price.value
        url = (self.SANDBOX_URL + endpoint if self.is_sandbox_url else self.BASE_URL + endpoint)

        try:
            response = self.request_session.get(url, params=params)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            self.cmc_logger.error(f"error with the connection to CMC API\n{e}")
        else:
            data = json.loads(response.text)
            self.cmc_logger.debug(
                f'There is an Error{data["status"]["error_message"]} {data["status"]["error_code"]}'
            )

            results = {
                "timestamp": data["status"]["timestamp"],
                "data": data["data"],
            }

            self._write_to_json_file(name="prices",timestamp=self.timestamp,payload=results)

            return results

    def get_info(
        self,
        tokens_coins_ids: str = "1",
        info_aux: str = "urls,logo,description,platform,date_added,notice,status",
    ):
        #make sure i'm no passing a coma at the end of the ID string
        if "," in tokens_coins_ids[-1]:
            tokens_coins_ids = tokens_coins_ids[:-1]

        params = {
            "id": tokens_coins_ids,
            "aux": info_aux,
        }
        endpoint = Cryptocurrency.info.value
        url = (self.SANDBOX_URL + endpoint if self.is_sandbox_url else self.BASE_URL + endpoint)

        # adding params as string query
        sq = urllib.parse.urlencode(params, safe=",")
        response = self.request_session.get(url=url, params=sq)
        data = json.loads(response.text)
        self.cmc_logger.debug(f"response: {response.status_code} and answer \n{response.text}")
        results = {
            "timestamp": data["status"]["timestamp"],
            "data": data["data"]
        }

        self._write_to_json_file(name="info", timestamp=self.timestamp, payload=results)

        return results
