import cmc_api
from models import Prices

if __name__ == '__main__':
	db = Prices()
	cmc_api.cnc_configuration()
	data = cmc_api.get_updated_prices_from_cmc()
	# print(db.read_all())
