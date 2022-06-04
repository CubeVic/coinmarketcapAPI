import json
from abc import ABC, abstractmethod
from typing import Any
from collections.abc import Callable

from src.cmc_api.cmc_utils import read_configuration_file


class AbstractDataHandler(ABC):
    @staticmethod
    @abstractmethod
    def data_extraction(payload: dict) -> (dict, Any):
        pass

    @staticmethod
    def response_builder(
        raw_resp: str, ext_method: Callable[[dict], (dict, Any)]
    ) -> dict:
        """Create the response to the request

        Reformation of the response provided by the endpoint, adding some usefully keys and removing others.

        Args:
                raw_resp (str): The response from the endpoint.
                ext_method (Callable[[dict], (dict, Any)]): The method use to extract the information.

        Return:
                (dict): Returns a response in dict format

        """
        json_raw_response = json.loads(raw_resp)

        metadata, data = ext_method(json_raw_response)
        response = {"metadata": metadata, "data": data}

        return response


class HandlerDataList(AbstractDataHandler):
    """Data value in the response contain a list of dictionaries"""

    @staticmethod
    def data_extraction(payload: dict) -> (dict, list):
        """
        If the endpoint return a value data that contain information in a list where each item is a dictionary.

        Args:
                payload (dict): The response from the endpoint in json form.

        Return:
                (dict, list): Returns a tuple where first parameter is metadata and the second is data.

        """
        metadata = {
            "timestamp": payload["status"]["timestamp"],
            "credit_count": payload["status"]["credit_count"],
            "error_message": payload["status"]["error_message"],
            "list_keys": [k for k in payload["data"][0].keys()],
        }
        data = payload["data"]
        return metadata, data


class HandlerDataDict(AbstractDataHandler):
    """Data value in the response contain a dictionary each key of the dictionary represent an item,
    item can have a dictionary inside"""

    @staticmethod
    def data_extraction(payload: dict) -> (dict, dict):
        """
        If the endpoint return a value data that contain information in a dictionary where each item is another dictionary.

        Args:
                payload (dict): The response from the endpoint in json form.

        Return:
                (dict, dict): Returns a tuple where first parameter is metadata and the second is data.

        """

        metadata = {
            "timestamp": payload["status"]["timestamp"],
            "credit_count": payload["status"]["credit_count"],
            "error_message": payload["status"]["error_message"],
        }
        dict_keys = list(payload["data"].values())[0]
        list_keys = list(dict_keys.keys())
        metadata["list_keys"] = list_keys
        data = payload["data"]
        return metadata, data


class HandlerDataNestedDataKey(AbstractDataHandler):
    """Data value in the response contain a data key that contain a list of dictionaries"""

    @staticmethod
    def data_extraction(payload: dict) -> (dict, dict):
        """
        If the endpoint return a value data that contain a directory which key is data and the value has different forms.

        Args:
                payload (dict): The response from the endpoint in json form.

        Return:
                (dict, dict): Returns a tuple where first parameter is metadata and the second is data.

        """

        metadata = {
            "timestamp": payload["status"]["timestamp"],
            "credit_count": payload["status"]["credit_count"],
            "error_message": payload["status"]["error_message"],
            "list_keys": [k for k in payload["data"]["data"][0].keys()],
        }

        data = payload["data"]["data"]
        return metadata, data


class HandlerDataSingleDict(AbstractDataHandler):
    """Data value in the response contain the information in a dictionary form"""

    @staticmethod
    def data_extraction(payload: dict) -> (dict, dict):
        """
        These extractions are focus in result of a request that is trying to get information about one single item, example
        information about one coin , one category, one blockchain.

        Args:
                payload (dict): The response from the endpoint in json form.

        Return:
                (dict, dict): Returns a tuple where first parameter is metadata and the second is data.

        """
        metadata = {
            "timestamp": payload["status"]["timestamp"],
            "credit_count": payload["status"]["credit_count"],
            "error_message": payload["status"]["error_message"],
            "list_keys": [k for k in payload["data"].keys()],
        }
        data = payload["data"]
        return metadata, data


class HandlerOriginalStructure(AbstractDataHandler):
    @staticmethod
    def data_extraction(payload: dict) -> (dict, dict):
        """This is for testing, the format is similar to original replay

        Args:
                payload (dict): The response from the endpoint in json form.

        Return:
                (dict, dict): Returns a tuple where first parameter is metadata and the second is data.

        """
        metadata = payload["status"]
        data = payload["data"]
        return metadata, data
