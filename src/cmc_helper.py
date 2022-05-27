"""Helper Classes
Contains Enum with the endpoints URI
"""
import enum
import os

cmc_headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": os.environ["CMC_API"],
}


class Urls(enum.Enum):
    """Different URLS"""
    BASE = "https://pro-api.coinmarketcap.com"
    SANDBOX = "https://sandbox-api.coinmarketcap.com"


class Cryptocurrency(enum.Enum):
    """Cryptocurrency endpoints"""
    CMC_ID_MAP = "/v1/cryptocurrency/map"
    LATEST_LIST_PRICE = "/v1/cryptocurrency/listings/latest"
    INFO = "/v2/cryptocurrency/info"
    QUOTE_LATEST = "/v2/cryptocurrency/quotes/latest"
    CATEGORY = "/v1/cryptocurrency/category"
    CATEGORIES = "/v1/cryptocurrency/categories"


class CryptocurrencyEndPointsArgs(enum.Enum):
    """Cryptocurrency EndPoint Arguments"""
    ID_MAP_ARGS = ["listing_status", "start", "limit", "sort", "symbol", "aux"]
    LIST_PRICE_ARGS = [
        "start", "limit", "price_min", "price_max", "market_cap_min", "market_cap_max", "volume_24h_min",
        "volume_24h_max", "circulating_supply_min", "circulating_supply_max", "percent_change_24h_min",
        "percent_change_24h_max", "convert", "convert_id", "sort", "sort_dir", "cryptocurrency_type",
        "tag", "aux"]
    INFO_ARGS = ["id", "slug", "symbol", "address", "aux"]
    QUOTES_LATEST_ARGS = ["id", "slug", "symbol", "convert", "convert_id", "aux", "skip_invalid"]
    CATEGORIES_ARGS = ["start", "limit", "id", "slug", "symbol"]
    CATEGORY_ARGS = ["id", "start", "limit", "convert", "convert_id"]


class Fiat(enum.Enum):
    """FIAT EndPoint"""
    FIAT = "/v1/fiat/map"


class FiatEndPointArgs(enum.Enum):
    """FIAT EndPoint arguments"""
    FIAT_ARGS = ["start", "limit", "sort", "include_metals"]


class Exchange(enum.Enum):
    """Exchange EndPoint"""
    EXCHANGE_MAP = "/v1/exchange/map"
    EXCHANGE_INFO = "/v1/exchange/info"


class ExchangeEndPointArgs(enum.Enum):
    """Exchange EndPoint Arguments"""
    EXCHANGE_MAP_ARGS = ["listing_status", "slug", "start", "limit", "sort", "aux", "crypto_id"]
    EXCHANGE_INFO_ARGS = ["id", "slug", "aux"]


class GlobalMetrics(enum.Enum):
    """Global Metrics EndPoint"""
    LATEST_GLOBAL_METRICS = "/v1/global-metrics/quotes/latest"


class GlobalMetricsEndPointArgs(enum.Enum):
    """Global Metrics EndPoint Arguments"""
    LATEST_GLOBAL_METRICS_ARGS = ["convert", "convert_id"]


class Tools(enum.Enum):
    """Tools EndPoint"""
    PRICE_CONVERSION = "/v1/tools/price-conversion"


class ToolsEndPointArgs(enum.Enum):
    """Tools EndPoint Arguments"""
    PRICE_CONVERSION_ARG = ["amount", "id", "symbol", "time", "convert", "convert_id"]


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
    KEY_INFO = "/v1/key/info"


class KeyEndPointArgs(enum.Enum):
    """Key EndPoint Arguments"""
    KEY_INFO_ARGS = []
