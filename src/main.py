"""Main file"""
from cmc_api import cmc, cmc_helper
from src.cmc_api import cmc_utils

if __name__ == '__main__':
	# base_url = cmc_helper.Urls.SANDBOX.value
	base_url = cmc_helper.Urls.BASE.value
	cmc = cmc.Cmc(url=base_url)

	cmc.get_cmc_id_map(listing_status="active", start=1, limit=1000)
	ids_string = cmc_utils.get_cmc_ids()
	# print(len(ids_string))
	# cmc.get_info(cmc_id=ids_string)
	# cmc.get_listing(start=1, limit=1000, convert="USD")
	# cmc.get_categories(start=1, limit=5000)
	# cmc.get_category(cmc_id="625d09d246203827ab52dd53")
	# cmc.get_quote_latest(cmc_id=1)
	# print(cmc.get_fiat())
	# print(cmc.get_exchange_map())
	# print(cmc.get_exchange_info(cmc_ex_id="16"))
	# print(cmc.get_latest_global_metrics())
	# print(cmc.get_price_conversion(amount=1.0, cmc_id="1"))
	print(cmc.get_key_info())
