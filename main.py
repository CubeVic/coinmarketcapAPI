import cmc_api
import database

if __name__ == '__main__':
	cmc_api.cnc_configuration()
	database.sql_configure()
	database.get_all_records()

