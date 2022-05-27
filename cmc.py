import enum
import urllib
from typing import Any
import requests
from requests import Session
import cmc_utils
from cmc_helper import Urls, Cryptocurrency, Fiat, Exchange, GlobalMetrics, Tools, Key
from cmc_helper import CryptocurrencyEndPointsArgs as Crypto_ep_args
from cmc_helper import FiatEndPointArgs as Fiat_ep_args
from cmc_helper import ExchangeEndPointArgs as Ex_ep_args
from cmc_helper import cmc_headers
from cmc_datahandler import AbstractDataHandler, HandlerDataDict, HandlerDataSingleDict, HandlerDataList, \
    HandlerOriginalStructure
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
        self.data_handler = AbstractDataHandler

    @property
    def url(self):
        return self._base_url

    @url.setter
    def url(self, value):
        self._base_url = value

    def _check_args(self,exp_args: Any, given_args: dict) -> dict:
        self.cmc_logger.debug(
            f"Validating args:\nexpected {exp_args} vs given {list(given_args.keys())}"
        )
        params = {k: v for (k, v) in given_args.items() if v and k in exp_args}
        self.cmc_logger.debug(f"params to be used: {params}")
        return params

    def fetch_data(
        self, endpoint: enum, endpoint_args, params: dict, data_handler_class
    ) -> (http_code, response_content_json):

        _params = self._check_args(
            exp_args=endpoint_args.value,
            given_args=params
        )

        self.data_handler = data_handler_class
        url_endpoint = self.url + endpoint.value
        try:
            # Make ' and , safe characters
            param_sq = urllib.parse.urlencode(_params, safe=',"')
            map_resp = self.request_session.get(url=url_endpoint, params=param_sq)

        except requests.exceptions.ConnectionError as connection_error:
            self.cmc_logger.error(
                msg=f"There is something wrong with the connection.\n{connection_error}"
            )
        except requests.exceptions.Timeout as timeout:
            self.cmc_logger.error(msg=f"Timeout. \n{timeout}")

        else:
            self.cmc_logger.info(msg=f"response => {map_resp.status_code}")

            response = self.data_handler.response_builder(
                raw_resp=map_resp.text, ext_method=data_handler_class.data_extraction
            )
            return map_resp.status_code, response


class Cmc(Wrapper):
    def __init__(self, url: str):
        super().__init__(url)

    def get_cmc_id_map(
        self, sort: str = "cmc_rank", listing_status: str = "active", **kwargs
    ) -> dict:
        """

        :param sort:
        :param listing_status:
        :param kwargs:
        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """

        # creating the params for the string query base in kwargs
        kwargs["sort"] = sort
        kwargs["listing_status"] = listing_status

        _, response = self.fetch_data(
            endpoint=Cryptocurrency.cmc_id_map,
            endpoint_args=Crypto_ep_args.id_map_args,
            params=kwargs,
            data_handler_class=HandlerDataList)

        cmc_utils.save_to_json(file_name="cmc_ids_mapping", payload=response)
        return response

    def get_info(self, cmc_id: str, **kwargs):
        """

        :param cmc_id:
        :param kwargs:
        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """
        # id, slug, symbol, address, aux
        kwargs["id"] = cmc_id

        _, response = self.fetch_data(
            endpoint=Cryptocurrency.info,
            endpoint_args=Crypto_ep_args.info_arg,
            params=kwargs,
            data_handler_class=HandlerDataDict)

        cmc_utils.save_to_json(file_name="info", payload=response)
        return response

    def get_listing(self, start: int, limit: int, **kwargs):
        """

        :param start:
        :param limit:
        :param kwargs:
        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """
        # In base Plan of the API this end point accept just one currency convert
        kwargs["start"] = start
        kwargs["limit"] = limit

        _, response = self.fetch_data(
            endpoint=Cryptocurrency.latest_list_price,
            endpoint_args=Crypto_ep_args.list_price_args,
            params=kwargs,
            data_handler_class=HandlerDataList)
        timestamp = cmc_utils.get_todays_timestamp()

        cmc_utils.save_to_json(
            file_name=f"latest_listing_{timestamp} ", payload=response
        )
        return response

    def get_categories(self, start: int, limit: int, **kwargs):
        """Get the categories

        Get the coin categories form Coin market Cap

        Args:
            start (int):
            limit (int):

        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """

        kwargs["start"] = start
        kwargs["limit"] = limit

        _, response = self.fetch_data(
            endpoint=Cryptocurrency.categories,
            endpoint_args=Crypto_ep_args.categories_args,
            params=kwargs,
            data_handler_class=HandlerDataList)
        # cmc_utils.save_to_json(file_name="test", payload=response)
        cmc_utils.save_to_json(file_name=f"categories_sandbox", payload=response)
        return response

    def get_category(self, cmc_id: str, **kwargs):
        """Get information of a single category

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
        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}

        """
        kwargs["id"] = cmc_id

        _, response = self.fetch_data(
            endpoint=Cryptocurrency.category,
            endpoint_args=Crypto_ep_args.category_args,
            params=kwargs,
            data_handler_class=HandlerDataSingleDict)
        cmc_utils.save_to_json(
            file_name=f"category_{response['data']['title']}", payload=response
        )
        return response

    def get_quote_latest(self, cmc_id: str, skip_invalid: bool = True, **kwargs):
        """Get the latest market quote of one or more currencies, on free tear conversion is limited

        Args:
            cmc_id  (str): on the API is call 'id', One or more comma-separated cryptocurrency CoinMarketCap IDs.
                Example: 1,2.
            skip_invalid (bool): Pass true to relax request validation rules. When requesting records on multiple
            cryptocurrencies an error is returned if no match is found for 1 or more requested cryptocurrencies. If set
            to true, invalid lookups will be skipped allowing valid cryptocurrencies to still be returned.
            **kwargs (Any): Can be used to pass other parameters to the endpoint.

                -> slug (str): Alternatively pass a comma-separated list of cryptocurrency slugs.
                    Example:"bitcoin, ethereum".
                -> symbol (str): Alternatively pass one or more comma-separated cryptocurrency symbols.
                    Example: "BTC,ETH". At least one "id" or "slug" or "symbol" is required for this request.
                -> convert (str, optional): Optionally calculate market quotes in up to 120 currencies at once by
                    passing a comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert
                    option beyond the first requires an additional call credit. A list of supported fiat options can be
                    found here. Each conversion is returned in its own "quote" object.
                -> convert_id (str, optional): Optionally calculate market quotes by CoinMarketCap ID instead of symbol.
                    This option is identical to convert outside of ID format. Ex: convert_id=1,2781 would replace
                    convert=BTC,USD in your query. This parameter cannot be used when convert is used.
                -> aux (str):
                    "num_market_pairs,cmc_rank,date_added,tags,platform,max_supply,circulating_supply,total_supply,
                    is_active,is_fiat" Optionally specify a comma-separated list of supplemental data fields to return.
                    Pass num_market_pairs,cmc_rank,date_added,tags,platform,max_supply,circulating_supply,total_supply,
                    market_cap_by_total_supply,volume_24h_reported,volume_7d,volume_7d_reported,volume_30d,
                    volume_30d_reported,is_active,is_fiat to include all auxiliary fields.
        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """
        kwargs["id"] = cmc_id
        kwargs["skip_invalid"] = skip_invalid

        _, response = self.fetch_data(
            endpoint=Cryptocurrency.quote_latest,
            endpoint_args=Crypto_ep_args.quotes_latest_args,
            params=kwargs,
            data_handler_class=HandlerDataSingleDict)
        timestamp = cmc_utils.get_todays_timestamp()
        cmc_utils.save_to_json(
            file_name=f"cmc_id_{cmc_id}_quote_{timestamp}", payload=response
        )
        return response

    # Fiat endPoint
    def get_fiat(self, **kwargs) -> dict:
        """ Returns a mapping of all supported fiat currencies to unique CoinMarketCap ids

        Args:
            **kwargs :
                -> start (int, optional): default = 1, Optionally offset the start (1-based index) of the paginated list
                    of items to return.
                -> limit (int, optional): [ 1 .. 5000 ] Optionally specify the number of results to return.
                    Use this parameter and the "start" parameter to determine your own pagination size.
                -> sort (str): sorting default = "id", possible values "id", "name" What field to sort the list by.
                -> include_metals (bool): default = false on API, here default = True. Pass true to include precious
                    metals.

        Return:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """
        kwargs["include_metals"] = True
        _, response = self.fetch_data(
            endpoint=Fiat.fiat,
            endpoint_args=Fiat_ep_args.fiat_args,
            params=kwargs,
            data_handler_class=HandlerDataList)
        cmc_utils.save_to_json(
            file_name=f"fiat_ids.json",
            payload=response
        )

        return response

    # Exchange endPoint
    def get_exchange_map(self,listing_status: str = 'active', **kwargs) -> dict:
        """ Returns a paginated list of all active cryptocurrency exchanges by CoinMarketCap ID

        Args:
            listing_status	(str): default = "active" Only active exchanges are returned by default. Pass inactive to
                get a list of exchanges that are no longer active. Pass untracked to get a list of exchanges that are
                registered but do not currently meet methodology requirements to have ac
            **kwargs :
                -> slug	(str, optional): Optionally pass a comma-separated list of exchange slugs (lowercase URL
                    friendly shorthand name with spaces replaced with dashes) to return CoinMarketCap IDs for.
                    If this option is passed, other options will be ignored.
                -> start (int, optional): >=1 Optionally offset the start (1-based index) of the paginated list of items
                    to return.
                -> limit (int): [ 1 .. 5000 ] Optionally specify the number of results to return. Use this parameter and
                    the "start" parameter to determine your own pagination size.
                -> sort (str): default= "id", can be "volume_24h" or "id". What field to sort the list of exchanges by.
                -> aux (str, optional): Optionally specify a comma-separated list of supplemental data fields to return.
                    Default =  "first_historical_data,last_historical_data,is_active". Pass first_historical_data,
                    last_historical_data,is_active,status to include all auxiliary fields.
                -> crypto_id (str, optional): Optionally include one fiat or cryptocurrency IDs to filter market pairs
                    by. For example ?crypto_id=1 would only return exchanges that have BTC.

        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """
        kwargs["listing_status"] = listing_status
        _, response = self.fetch_data(
            endpoint=Exchange.exchange_map,
            endpoint_args=Ex_ep_args.exchange_map_args,
            params=kwargs,
            data_handler_class=HandlerDataList)
        cmc_utils.save_to_json(
            file_name=f"Exchange_cmc_id.json",
            payload=response
        )

        return response

    def get_exchange_info(self,cmc_ex_id: str, **kwargs) -> dict:
        """ Returns metadata for one or more exchanges.

        Information include launch date, logo, official website URL, social links, and market fee documentation URL.

        Args:
            cmc_ex_id (str): on the API the parameter is 'id'. One or more comma-separated CoinMarketCap cryptocurrency
                exchange ids. Example: "1,2".
            **kwargs:
                -> slug (str): Alternatively, one or more comma-separated exchange names in URL friendly shorthand "slug"
                format (all lowercase, spaces replaced with hyphens). Example: "binance,gdax". At least one "id" or
                "slug" is required.
                -> aux (str): Optionally specify a comma-separated list of supplemental data fields to return.
                Default = "urls,logo,description,date_launched,notice". Pass urls,logo,description,date_launched,
                notice,status to include all auxiliary fields.

        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """
        kwargs["id"] = cmc_ex_id
        _, response = self.fetch_data(
            endpoint=Exchange.exchange_info,
            endpoint_args=Ex_ep_args.exchange_info_args,
            params=kwargs,
            data_handler_class=HandlerDataDict)
        cmc_utils.save_to_json(
            file_name=f"Exchange_{cmc_ex_id}.json",
            payload=response
        )

        return response

# base_url = Urls.sandbox.value
base_url = Urls.base.value
cmc = Cmc(url=base_url)

# cmc.get_cmc_id_map(listing_status="active", start=1, limit=1000)
# ids_string = cmc_utils.get_cmc_ids()
# print(len(ids_string))
# cmc.get_info(cmc_id=ids_string)
# cmc.get_listing(start=1, limit=1000, convert="USD")
#
# cmc.get_categories(start=1, limit=5000)
# cmc.get_category(cmc_id="625d09d246203827ab52dd53")


# cmc.get_quote_latest(cmc_id=1)
# print(cmc.get_fiat())
# print(cmc.get_exchange_map())
print(cmc.get_exchange_info(cmc_ex_id="16"))
