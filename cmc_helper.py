import enum
import os

cmc_headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": os.environ["CMC_API"],
}


class Urls(enum.Enum):
    base = "https://pro-api.coinmarketcap.com"
    sandbox = "https://sandbox-api.coinmarketcap.com"


class Cryptocurrency(enum.Enum):
    cmc_id_map = "/v1/cryptocurrency/map"
    latest_list_price = "/v1/cryptocurrency/listings/latest"
    info = "/v2/cryptocurrency/info"
    quote_latest = "/v2/cryptocurrency/quotes/latest"
    category = "/v1/cryptocurrency/category"
    categories = "/v1/cryptocurrency/categories"


class CryptocurrencyEndPointsArgs(enum.Enum):
    id_map_args = ["listing_status", "start", "limit", "sort", "symbol", "aux"]
    list_price_args = [
        "start", "limit", "price_min", "price_max", "market_cap_min", "market_cap_max", "volume_24h_min",
        "volume_24h_max", "circulating_supply_min", "circulating_supply_max", "percent_change_24h_min",
        "percent_change_24h_max", "convert", "convert_id", "sort", "sort_dir", "cryptocurrency_type",
        "tag", "aux"]
    info_arg = ["id", "slug", "symbol", "address", "aux"]
    quotes_latest_args = ["id", "slug", "symbol", "convert", "convert_id", "aux", "skip_invalid"]
    categories_args = ["start", "limit", "id", "slug", "symbol"]
    category_args = ["id", "start", "limit", "convert", "convert_id"]


class Fiat(enum.Enum):
    fiat = "/v1/fiat/map"


class FiatEndPointArgs(enum.Enum):
    fiat_args = ["start", "limit", "sort", "include_metals"]


class Exchange(enum.Enum):
    exchange_map = "/v1/exchange/map"
    exchange_info = "/v1/exchange/info"


class ExchangeEndPointArgs(enum.Enum):
    exchange_map_args = ["listing_status","slug","start","limit","sort","aux","crypto_id"]
    exchange_info_args = ["id", "slug", "aux"]


class GlobalMetrics(enum.Enum):
    latest_global_metrics = "/v1/global-metrics/quotes/latest"


class Tools(enum.Enum):
    price_conversion = "/v1/tools/price-conversion"


# not support for free tier
class Blockchain(enum.Enum):
    pass


# Deprecated
class Partners(enum.Enum):
    pass


class Key(enum.Enum):
    key_info = "/v1/key/info"
