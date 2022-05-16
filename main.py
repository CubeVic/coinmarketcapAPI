import cmc_api
from models import Prices
import os

if __name__ == '__main__':
	db = Prices()
	cmc = cmc_api.CmcApi(os.environ['CMC_API'], is_sandbox_url=False)

	# cmc.get_updated_prices()
	# cmc.get_map()

	print(db.select_last_updated())
	ids = db.select_all_ids()
	print(cmc.get_info(tokens_coins_ids=ids))
