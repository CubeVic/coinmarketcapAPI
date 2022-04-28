import cmc_api
from models import Prices
import os

if __name__ == '__main__':
	db = Prices()
	# data = cmc_api.get_updated_prices_from_cmc()
	# print(db.read_all())
	cmc = cmc_api.CmcApi(os.environ['CMC_API'], is_sandbox_url=False)
	cmc.get_updated_prices_from_cmc()
	cmc.get_map()

