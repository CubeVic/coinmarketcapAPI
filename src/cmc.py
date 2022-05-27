import enum
from urllib import parse
from typing import Any
from requests import Session, exceptions
from src import cmc_utils
from src.cmc_helper import Cryptocurrency, Fiat, Exchange, GlobalMetrics, Tools, Key
from src.cmc_helper import (CryptocurrencyEndPointsArgs as Crypto_ep_args,
                            FiatEndPointArgs as Fiat_ep_args,
                            ExchangeEndPointArgs as Ex_ep_args,
                            GlobalMetricsEndPointArgs as GM_ep_args,
                            ToolsEndPointArgs as T_ep_args,
                            KeyEndPointArgs as K_ep_args
                            )
from src.cmc_helper import cmc_headers
from src.cmc_datahandler import (AbstractDataHandler,
                                 HandlerDataDict,
                                 HandlerDataSingleDict,
                                 HandlerDataList,)
from abc import ABC


http_code = int()
response_content_json = dict()


# prepare for possible changes due to free and paid end points difference.
class Wrapper(ABC):
    """Abstract class"""
    cmc_logger = cmc_utils.fetch_cmc_logger()

    def __init__(self, url: str):
        self._base_url = url
        self.request_session = Session()
        self.request_session.headers.update(cmc_headers)
        self.data_handler = AbstractDataHandler

    @property
    def url(self):
        """Property url"""
        return self._base_url

    @url.setter
    def url(self, value):
        self._base_url = value

    def _check_args(self, exp_args: Any, given_args: dict) -> dict:
        self.cmc_logger.debug(
            f"Validating args:\nexpected {exp_args} vs given {list(given_args.keys())}"
        )
        params = {k: v for (k, v) in given_args.items() if v and k in exp_args}
        self.cmc_logger.debug(f"params to be used: {params}")
        return params

    def fetch_data(
        self, endpoint: object, endpoint_args: object, params: dict, data_handler_class: object
    ) -> tuple[int, dict]:
        """Fetch will do the request to the end point provided and extract the information with the extraction function

        Args:
            endpoint (enum): The URI for the endpoint.
            endpoint_args (enum): The URI for the query parameters.
            params (dict): Parameters for the search query.
            data_handler_class (AbstractDataHandler): class that will extract the information.

        Returns:
             (tuple[int, dict]): response contain the http code and the data

        """

        _params = self._check_args(
            exp_args=endpoint_args.value,
            given_args=params
        )

        self.data_handler = data_handler_class
        url_endpoint = self.url + endpoint.value
        try:
            # Make ' and , safe characters
            param_sq = parse.urlencode(_params, safe=',"')
            map_resp = self.request_session.get(url=url_endpoint, params=param_sq)

        except exceptions.ConnectionError as connection_error:
            self.cmc_logger.error(
                msg=f"There is something wrong with the connection.\n{connection_error}"
            )
        except exceptions.Timeout as timeout:
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
        """Returns a mapping of all cryptocurrencies to unique CoinMarketCap ids.

        Args:
            listing_status (str): default = "active". Only active cryptocurrencies are returned by default.
                Pass inactive to get a list of cryptocurrencies that are no longer active. Pass untracked to get a list
                of cryptocurrencies that are listed but do not yet meet methodology requirements to have tracked markets
                available. You may pass one or more comma-separated values.
            sort (str): default = "cmc_rank", options "cmc_rank", "id". What field to sort the list of cryptocurrencies
                by.
            **kwargs:
                -> start (int, optional): >= 1 Optionally offset the start ( 1-based index) of the paginated list of
                    items to return.
                -> limit (int, optional): [ 1 .. 5000 ] Optionally specify the number of results to return. Use this
                    parameter and the "start" parameter to determine your own pagination size.
                -> symbol (str): Optionally pass a comma-separated list of cryptocurrency symbols to return
                    CoinMarketCap IDs for. If this option is passed, other options will be ignored.
                -> aux (str, optional): default = "platform,first_historical_data,last_historical_data,is_active"
                    Optionally specify a comma-separated list of supplemental data fields to return.
                    Pass platform,first_historical_data,last_historical_data,is_active,status to include all auxiliary
                    fields.

        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                    data: "the data requested"}
        """

        # creating the params for the string query base in kwargs
        kwargs["sort"] = sort
        kwargs["listing_status"] = listing_status

        _, response = self.fetch_data(
            endpoint=Cryptocurrency.CMC_ID_MAP,
            endpoint_args=Crypto_ep_args.ID_MAP_ARGS,
            params=kwargs,
            data_handler_class=HandlerDataList)

        cmc_utils.save_to_json(file_name="cmc_ids_mapping", payload=response)
        return response

    def get_info(self, cmc_id: str, **kwargs):
        """Returns all static metadata available for one or more cryptocurrencies. This information includes details
        like logo, description, official website URL, social links, and links to a cryptocurrency's technical
        documentation.

        Args:
            cmc_id (str): One or more comma-separated CoinMarketCap cryptocurrency IDs. Example: "1,2"
            **kwargs:
                -> slug (str) Alternatively pass a comma-separated list of cryptocurrency slugs.
                    Example: "bitcoin,ethereum".
                -> symbol (str): Alternatively pass one or more comma-separated cryptocurrency symbols.
                    Example: "BTC,ETH". At least one "id" or "slug" or "symbol" is required for this request.
                -> address (str): Alternatively pass in a contract address.
                    Example: "0xc40af1e4fecfa05ce6bab79dcd8b373d2e436c4e"
                -> aux (str): default = "urls,logo,description,tags,platform,date_added,notice". Optionally specify a
                    comma-separated list of supplemental data fields to return.
                    Pass urls,logo,description,tags,platform,date_added,notice,status to include all auxiliary fields.

        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """
        # id, slug, symbol, address, aux
        kwargs["id"] = cmc_id

        _, response = self.fetch_data(
            endpoint=Cryptocurrency.INFO,
            endpoint_args=Crypto_ep_args.INFO_ARGS,
            params=kwargs,
            data_handler_class=HandlerDataDict)

        cmc_utils.save_to_json(file_name="info", payload=response)
        return response

    def get_listing(self, start: int, limit: int, **kwargs):
        """Returns a paginated list of all active cryptocurrencies with latest market data.

        Args:
            start (int): >= 1. Optionally offset the start (1-based index) of the paginated list of items to return.
            limit (int): [ 1 .. 5000 ] Optionally specify the number of results to return. Use this parameter and the
                "start" parameter to determine your own pagination size.
            **kwargs:
                -> price_min (int): [ 0 .. 100000000000000000 ] Optionally specify a threshold of minimum USD price to
                    filter results by.
                -> price_max (int): [ 0 .. 100000000000000000 ] Optionally specify a threshold of maximum USD price to
                    filter results by.
                -> market_cap_min (int): [ 0 .. 100000000000000000 ] Optionally specify a threshold of minimum market
                    cap to filter results by.
                -> market_cap_max (int): [ 0 .. 100000000000000000 ] Optionally specify a threshold of maximum market
                    cap to filter results by.
                -> volume_24h_min (int): [ 0 .. 100000000000000000 ] Optionally specify a threshold of minimum 24 hour
                    USD volume to filter results by.
                -> volume_24h_max (int): [ 0 .. 100000000000000000 ] Optionally specify a threshold of maximum 24 hour
                    USD volume to filter results by.
                -> circulating_supply_min (int): [ 0 .. 100000000000000000 ]Optionally specify a threshold of minimum
                    circulating supply to filter results by.
                -> circulating_supply_max (int): [ 0 .. 100000000000000000 ] Optionally specify a threshold of maximum
                    circulating supply to filter results by.
                -> percent_change_24h_min (int): >= -100 Optionally specify a threshold of minimum 24 hour percent
                    change to filter results by.
                -> percent_change_24h_max (int): >= -100 Optionally specify a threshold of maximum 24 hour percent
                    change to filter results by.
                -> convert (str): Optionally calculate market quotes in up to 120 currencies at once by passing a
                    comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert option
                    beyond the first requires an additional call credit. A list of supported fiat options can be found
                    here. Each conversion is returned in its own "quote" object.
                -> convert_id (str): Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This
                    option is identical to convert outside of ID format. Ex: convert_id=1,2781 would replace
                    convert=BTC,USD in your query. This parameter cannot be used when convert is used.
                -> sort	(str): default = "market_cap". options = "name""symbol""date_added""market_cap"
                    "market_cap_strict""price""circulating_supply""total_supply""max_supply""num_market_pairs"
                    "volume_24h""percent_change_1h""percent_change_24h""percent_change_7d"
                    "market_cap_by_total_supply_strict""volume_7d""volume_30d" What field to sort the list of
                    cryptocurrencies by.
                -> sort_dir (str): options = "asc", "desc" The direction in which to order cryptocurrencies against the
                    specified sort.
                -> cryptocurrency_type (str): default = "all". options = "all""coins""tokens".The type of cryptocurrency
                    to include.
                -> tag (str): default = "all",options = "all","defi","filesharing".The tag of cryptocurrency to include.
                -> aux (str): default = "num_market_pairs,cmc_rank,date_added,tags,platform,max_supply,
                    circulating_supply,total_supply". Optionally specify a comma-separated list of supplemental data
                    fields to return. Pass num_market_pairs,cmc_rank,date_added,tags,platform,max_supply,
                    circulating_supply,total_supply,market_cap_by_total_supply,volume_24h_reported,volume_7d,
                    volume_7d_reported,volume_30d,volume_30d_reported,is_market_cap_included_in_calc to include all
                    auxiliary fields.
        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """
        # In base Plan of the API this end point accept just one currency convert
        kwargs["start"] = start
        kwargs["limit"] = limit

        _, response = self.fetch_data(
            endpoint=Cryptocurrency.LATEST_LIST_PRICE,
            endpoint_args=Crypto_ep_args.LIST_PRICE_ARGS,
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
            start (int): >= 1 Optionally offset the start (1-based index) of the paginated list of items to return.
            limit (int): [ 1 .. 5000 ] Optionally specify the number of results to return. Use this parameter and the
                "start" parameter to determine your own pagination size.
            **kwargs:
                -> id (str): Filtered categories by one or more comma-separated cryptocurrency CoinMarketCap IDs.
                    Example: 1,2.
                -> slug (str): Alternatively filter categories by a comma-separated list of cryptocurrency slugs.
                    Example: "bitcoin,ethereum".
                -> symbol (str): Alternatively filter categories one or more comma-separated cryptocurrency symbols.
                    Example: "BTC,ETH".

        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """

        kwargs["start"] = start
        kwargs["limit"] = limit

        _, response = self.fetch_data(
            endpoint=Cryptocurrency.CATEGORIES,
            endpoint_args=Crypto_ep_args.CATEGORIES_ARGS,
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
            (dict): {metadata: {
                        "timestamp": "",
                        "credit_count": "",
                        "error_message": "",
                        "list_keys": ""
                    },
                    data: "the data requested"}

        """
        kwargs["id"] = cmc_id

        _, response = self.fetch_data(
            endpoint=Cryptocurrency.CATEGORY,
            endpoint_args=Crypto_ep_args.CATEGORY_ARGS,
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
            endpoint=Cryptocurrency.QUOTE_LATEST,
            endpoint_args=Crypto_ep_args.QUOTES_LATEST_ARGS,
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
            endpoint=Fiat.FIAT,
            endpoint_args=Fiat_ep_args.FIAT_ARGS,
            params=kwargs,
            data_handler_class=HandlerDataList)
        cmc_utils.save_to_json(
            file_name=f"fiat_ids.json",
            payload=response
        )

        return response

    # Exchange endPoint
    def get_exchange_map(self, listing_status: str = 'active', **kwargs) -> dict:
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
            endpoint=Exchange.EXCHANGE_MAP,
            endpoint_args=Ex_ep_args.EXCHANGE_MAP_ARGS,
            params=kwargs,
            data_handler_class=HandlerDataList)
        cmc_utils.save_to_json(
            file_name=f"Exchange_cmc_id.json",
            payload=response
        )

        return response

    def get_exchange_info(self, cmc_ex_id: str, **kwargs) -> dict:
        """ Returns metadata for one or more exchanges.

        Information include launch date, logo, official website URL, social links, and market fee documentation URL.

        Args:
            cmc_ex_id (str): on the API the parameter is 'id'. One or more comma-separated CoinMarketCap cryptocurrency
                exchange ids. Example: "1,2".
            **kwargs:
                -> slug (str): Alternatively, one or more comma-separated exchange names in URL friendly shorthand
                    "slug" format (all lowercase, spaces replaced with hyphens). Example: "binance,gdax". At least one
                    "id" or "slug" is required.
                -> aux (str): Optionally specify a comma-separated list of supplemental data fields to return.
                    Default = "urls,logo,description,date_launched,notice". Pass urls,logo,description,date_launched,
                    notice,status to include all auxiliary fields.

        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """
        kwargs["id"] = cmc_ex_id
        _, response = self.fetch_data(
            endpoint=Exchange.EXCHANGE_INFO,
            endpoint_args=Ex_ep_args.EXCHANGE_INFO_ARGS,
            params=kwargs,
            data_handler_class=HandlerDataDict)
        cmc_utils.save_to_json(
            file_name=f"Exchange_{cmc_ex_id}.json",
            payload=response
        )

        return response

    # GlobalMetrics endPoint
    def get_latest_global_metrics(self, **kwargs) -> dict:
        """Returns the latest global cryptocurrency market metrics.

        Use the "convert" option to return market values in multiple fiat and cryptocurrency conversions
        (for the basic tier this might be limited to one)

        Args:
            **kwargs:
                -> convert	(str, optional): Optionally calculate market quotes in up to 120 currencies at once by
                    passing a comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert
                    option beyond the first requires an additional call credit. A list of supported fiat options can be
                    found here. Each conversion is returned in its own "quote" object.
                -> convert_id (str, optional): Optionally calculate market quotes by CoinMarketCap ID instead of symbol.
                    This option is identical to convert outside of ID format. Ex: convert_id=1,2781 would replace
                    convert=BTC,USD in your query. This parameter cannot be used when convert is used.

        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """
        _, response = self.fetch_data(
            endpoint=GlobalMetrics.LATEST_GLOBAL_METRICS,
            endpoint_args=GM_ep_args.LATEST_GLOBAL_METRICS_ARGS,
            params=kwargs,
            data_handler_class=HandlerDataSingleDict)
        timestamp = cmc_utils.get_todays_timestamp()
        cmc_utils.save_to_json(
            file_name=f"Global_metrics_{timestamp}.json",
            payload=response
        )

        return response

    # Tools endPoint
    def get_price_conversion(self, amount: float, cmc_id: str, **kwargs):
        """Convert an amount of one cryptocurrency or fiat currency into one or more different currencies utilizing the
            latest market rate for each currency.

        Args:
            amount (int): [ 1e-8 .. 1000000000000 ] Required An amount of currency to convert. Example: 10.43.
            cmc_id (str): on the API is  'id', The CoinMarketCap currency ID of the base cryptocurrency or fiat to
                convert from. Example: "1"
            **kwargs:
                -> symbol (str): Alternatively the currency symbol of the base cryptocurrency or fiat to convert from.
                    Example: "BTC". One "id" or "symbol" is required.
                -> time (str, optional): Optional timestamp (Unix or ISO 8601) to reference historical pricing during
                    conversion. If not passed, the current time will be used. If passed, we'll reference the closest
                    historic values available for this conversion.
                -> convert (str): Pass up to 120 comma-separated fiat or cryptocurrency symbols to convert the source
                    amount to.
                -> convert_id (str, optional): Optionally calculate market quotes by CoinMarketCap ID instead of symbol.
                    This option is identical to convert outside of ID format. Ex: convert_id=1,2781 would replace
                    convert=BTC,USD in your query. This parameter cannot be used when convert is used.

        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """
        kwargs["amount"] = amount
        kwargs["id"] = cmc_id
        _, response = self.fetch_data(
            endpoint=Tools.PRICE_CONVERSION,
            endpoint_args=T_ep_args.PRICE_CONVERSION_ARG,
            params=kwargs,
            data_handler_class=HandlerDataSingleDict)
        timestamp = cmc_utils.get_todays_timestamp()
        cmc_utils.save_to_json(
            file_name=f"Price_conversion_{cmc_id}_{timestamp}.json",
            payload=response
        )

        return response

    # Key endPoint
    def get_key(self):
        """Returns API key details and usage stats. This endpoint can be used to programmatically monitor your key usage
            compared to the rate limit and daily/monthly credit limits available to your API plan.

        Returns:
            (dict): {metadata: {"timestamp": "", "credit_count": "", "error_message": "", "list_keys": ""},
                data: "the data requested"}
        """
        _, response = self.fetch_data(
            endpoint=Key.KEY_INFO,
            endpoint_args=K_ep_args.KEY_INFO_ARGS,
            params={},
            data_handler_class=HandlerDataSingleDict)
        cmc_utils.save_to_json(
            file_name=f"API_info.json",
            payload=response
        )

        return response
