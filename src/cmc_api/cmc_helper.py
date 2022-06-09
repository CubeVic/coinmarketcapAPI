"""Helper Classes
Contains Enum with the endpoints URI
"""
import enum


def get_headers(api_key):
    """Create the headers"""
    cmc_headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }
    return cmc_headers


class Urls(enum.Enum):
    """Different URLS"""

    BASE = "https://pro-api.coinmarketcap.com"
    SANDBOX = "https://sandbox-api.coinmarketcap.com"


class CryptocurrencyEndPointsArgs(enum.Enum):
    """Cryptocurrency EndPoint Arguments"""

    ID_MAP_ARGS = ["listing_status", "start", "limit", "sort", "symbol", "aux"]
    LIST_PRICE_ARGS = [
        "start",
        "limit",
        "price_min",
        "price_max",
        "market_cap_min",
        "market_cap_max",
        "volume_24h_min",
        "volume_24h_max",
        "circulating_supply_min",
        "circulating_supply_max",
        "percent_change_24h_min",
        "percent_change_24h_max",
        "convert",
        "convert_id",
        "sort",
        "sort_dir",
        "cryptocurrency_type",
        "tag",
        "aux",
    ]
    INFO_ARGS = ["id", "slug", "symbol", "address", "aux"]
    QUOTES_LATEST_ARGS = [
        "id",
        "slug",
        "symbol",
        "convert",
        "convert_id",
        "aux",
        "skip_invalid",
    ]
    CATEGORIES_ARGS = ["start", "limit", "id", "slug", "symbol"]
    CATEGORY_ARGS = ["id", "start", "limit", "convert", "convert_id"]


class Cryptocurrency(enum.Enum):
    """Cryptocurrency endpoints"""

    CMC_ID_MAP = [
        "/v1/cryptocurrency/map",
        CryptocurrencyEndPointsArgs.ID_MAP_ARGS.value,
    ]
    LATEST_LIST_PRICE = [
        "/v1/cryptocurrency/listings/latest",
        CryptocurrencyEndPointsArgs.LIST_PRICE_ARGS.value,
    ]
    INFO = ["/v2/cryptocurrency/info", CryptocurrencyEndPointsArgs.INFO_ARGS.value]
    QUOTE_LATEST = [
        "/v2/cryptocurrency/quotes/latest",
        CryptocurrencyEndPointsArgs.QUOTES_LATEST_ARGS.value,
    ]
    CATEGORY = [
        "/v1/cryptocurrency/category",
        CryptocurrencyEndPointsArgs.CATEGORY_ARGS.value,
    ]
    CATEGORIES = [
        "/v1/cryptocurrency/categories",
        CryptocurrencyEndPointsArgs.CATEGORIES_ARGS.value,
    ]


class FiatEndPointArgs(enum.Enum):
    """FIAT EndPoint arguments"""

    FIAT_ARGS = ["start", "limit", "sort", "include_metals"]


class Fiat(enum.Enum):
    """FIAT EndPoint"""

    FIAT = ["/v1/fiat/map", FiatEndPointArgs.FIAT_ARGS.value]


class ExchangeEndPointArgs(enum.Enum):
    """Exchange EndPoint Arguments"""

    EXCHANGE_MAP_ARGS = [
        "listing_status",
        "slug",
        "start",
        "limit",
        "sort",
        "aux",
        "crypto_id",
    ]
    EXCHANGE_INFO_ARGS = ["id", "slug", "aux"]


class Exchange(enum.Enum):
    """Exchange EndPoint"""

    EXCHANGE_MAP = ["/v1/exchange/map", ExchangeEndPointArgs.EXCHANGE_MAP_ARGS.value]
    EXCHANGE_INFO = ["/v1/exchange/info", ExchangeEndPointArgs.EXCHANGE_INFO_ARGS.value]


class GlobalMetricsEndPointArgs(enum.Enum):
    """Global Metrics EndPoint Arguments"""

    LATEST_GLOBAL_METRICS_ARGS = ["convert", "convert_id"]


class GlobalMetrics(enum.Enum):
    """Global Metrics EndPoint"""

    LATEST_GLOBAL_METRICS = [
        "/v1/global-metrics/quotes/latest",
        GlobalMetricsEndPointArgs.LATEST_GLOBAL_METRICS_ARGS.value,
    ]


class ToolsEndPointArgs(enum.Enum):
    """Tools EndPoint Arguments"""

    PRICE_CONVERSION_ARG = ["amount", "id", "symbol", "time", "convert", "convert_id"]


class Tools(enum.Enum):
    """Tools EndPoint"""

    PRICE_CONVERSION = [
        "/v1/tools/price-conversion",
        ToolsEndPointArgs.PRICE_CONVERSION_ARG.value,
    ]


# # not support for free tier
# class Blockchain(enum.Enum):
#     pass
#
#
# # Deprecated
# class Partners(enum.Enum):
#     pass


class Key(enum.Enum):
    """Key EndPoint"""

    KEY_INFO = ["/v1/key/info", ""]
