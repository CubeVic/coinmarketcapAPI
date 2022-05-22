import cmc_api
from models import Prices
import os

if __name__ == '__main__':
	# Remember to run initialize the script
	db_prices = Prices()
	cmc = cmc_api.CmcApi(os.environ['CMC_API'], is_sandbox_url=False)

	cmc.get_updated_prices_from_cmc()
	cmc.get_map()

	# print(db_prices.select_last_updated())
	ids = db_prices.select_all_ids()
	print(f'ids {ids}')
	print(cmc.get_info(id=ids))
