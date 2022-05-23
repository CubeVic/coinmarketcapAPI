import enum
import os

cmc_headers = {
	'Accepts': 'application/json',
	'X-CMC_PRO_API_KEY': os.environ['CMC_API'],
}


class Urls(enum.Enum):
	base = 'https://pro-api.coinmarketcap.com'
	sandbox = 'https://sandbox-api.coinmarketcap.com'


class Cryptocurrency(enum.Enum):
	cmc_id_map = '/v1/cryptocurrency/map'
	latest_list_price = '/v1/cryptocurrency/listings/latest'
	info = '/v2/cryptocurrency/info'
	quote_latest = '/v2/cryptocurrency/quotes/latest'
	category = "/v1/cryptocurrency/category"
	categories = "/v1/cryptocurrency/categories"


class Cryptocurrency_endpoints_arguments(enum.Enum):
	cmc_id_map_args = ['listing_status', 'start', 'limit', 'sort', 'symbol', 'aux']


class Fiat(enum.Enum):
	fiat = "/v1/fiat/map"


class Exchange(enum.Enum):
	exchange_map = "/v1/exchange/map"
	exchange_info = "/v1/exchange/info"


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
