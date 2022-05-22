""" This is the initialization script
1. It will create the database called Cryptocurrency
2. It will check if there are any json files containing the information to populate the database
3. If there is no json files it will call the Coin market cap API to get information
4. It will populate the database
"""
import json
import sqlite3
from datetime import datetime
import time
import logging
from logging import Logger

from cmc_api import CmcApi
from models import MydataBase, Prices, Info
import os


def initialize_configure_logger() -> Logger:
	""" Configure the logger for this module
	Description:
		Configuration of two logger, one logger will log the information in a file, the second one will
		log the information to the console.
	:return: None
	"""
	init_logger = logging.getLogger(__name__)
	init_logger.setLevel(logging.INFO)

	file_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt="%d-%b-%y %H:%M:%S")
	stream_formatter = logging.Formatter('%(levelname)s - function: %(funcName)s - %(message)s')

	file_handler = logging.FileHandler('logs/initialize.log')
	file_handler.setFormatter(file_formatter)

	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(stream_formatter)

	init_logger.addHandler(file_handler)
	init_logger.addHandler(stream_handler)
	return init_logger


def _get_todays_timestamp() -> str:
	"""Get today's timestamp

	:return:
	"""
	t = str(datetime.utcfromtimestamp(time.time()))
	timestamp = t[0: 10].replace("-", "_")

	return timestamp


def _read_price_info_from_json_file() -> dict:
	"""Read the data from the json file.

	Description:
		The Json contain the latest information obtain from CMC API.

	:return:
	"""

	timestamp = _get_todays_timestamp()
	try:
		with open(f'json_files/price-{timestamp}.json') as file:
			read_data = json.load(file)
		return read_data
	except FileNotFoundError as e:
		return e


def _read_info_from_json_file():
	"""Read the json file containing information from CMC crytocurrency info end point

	:return:
	"""
	try:
		with open(f'json_files/info.json') as file:
			read_data = json.load(file)
			return read_data
	except FileNotFoundError as e:
		return e


def insert_all_prices(db_table_prices, price_data: dict):
	"""Insert all the records provided as parameters in the table "prices"

	:param db_table_prices:
	:param price_data:
	:return: None
	"""
	records = []

	for i in range(len(price_data)):
		data = price_data[i]
		r = (
			data['id'],
			data['name'],
			data['symbol'],
			data['slug'],
			data['cmc_rank'],
			data['date_added'],
			data['max_supply'],
			data['circulating_supply'],
			data['total_supply'],
			data['last_updated'],
			data['quote']['USD']['price'],
			data['quote']['USD']['percent_change_1h'],
			data['quote']['USD']['percent_change_24h'],
			data['quote']['USD']['percent_change_7d'],
			data['quote']['USD']['percent_change_30d'],
			data['quote']['USD']['percent_change_60d'],
			data['quote']['USD']['percent_change_90d'])
		records.append(r)

	try:
		db_table_prices.create_table()
		db_table_prices.insert_many(records)
	except sqlite3.OperationalError as e:
		init_logger.exception(f"table doesn't exist.\nOriginal Traceback\n{e}")
	else:
		init_logger.debug("values added to the database")


def insert_all_info(db_table_info, info_data: dict, cmc_ides: str):
	"""It will insert the data regarding cryptocurrency info to the table info in the database

	:param db_table_info:
	:param info_data:
	:param cmc_ides:
	:return:
	"""
	records = []
	id_list = cmc_ides.split(',')

	for i in id_list:
		data = info_data[i]
		r = (
			data['id'],
			data['name'],
			data['symbol'],
			data['category'],
			data['description'],
			data['slug'],
			data['logo'],
			data['subreddit'],
			data['notice'],
			str(data['urls']),
			str(data['platform']),
			data['twitter_username'],
			data['date_launched'],
			str(data['contract_address']),
			data['status'])
		records.append(r)
		# print(f'last records {records[0]}')
		try:
			db_table_info.create_table()
			db_table_info.insert_many(records)
		except sqlite3.OperationalError as e:
			init_logger.exception(f"table doesn't exist.\nOriginal Traceback\n{e}")
		else:
			init_logger.debug("values of info added to the database")


init_logger = initialize_configure_logger()
init_logger.info('Creating connection do database ...')

# instance of the coin market cap API
cmc = CmcApi(cmc_api=os.environ['CMC_API'], is_sandbox_url=False)

db = MydataBase()
db_prices = Prices()
db_info = Info()

timestamp = _get_todays_timestamp()
price_data_payload = ''
cmc_ids = ''
info_data_payload = ''

init_logger.info('Checking if json files exist')

# Getting the data from the json files if exist otherwise hit the api to obtain data.
if os.path.exists(f'json_files/price-{timestamp}.json'):
	init_logger.debug('getting price data from the jsons files')
	price_data_payload = _read_price_info_from_json_file()
else:
	init_logger.debug('Calling CMC API to get prices')
	price_data_payload = cmc.get_updated_prices()


ids = [str(data['id'])for data in price_data_payload['data']]
cmc_ids = ",".join(ids)


if os.path.exists('json_files/info.json'):
	init_logger.debug('getting info data from the jsons files')
	info_data_payload = _read_info_from_json_file()
else:
	init_logger.debug('Calling CMC API to get info')
	# first get the ids
	info_data_payload = cmc.get_info(tokens_coins_ids=cmc_ids)

# populate database
insert_all_prices(db_table_prices=db_prices, price_data=price_data_payload['data'])
insert_all_info(db_table_info=db_info, info_data=info_data_payload['data'], cmc_ides=cmc_ids)
