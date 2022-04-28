import json
import sqlite3
from datetime import datetime
import time
import logging

from models import Prices


def initialize_configure_logger():
	""" Configure the logger for this module
	Description:
		Configuration of two logger, one logger will log the information in a file, the second one will
		log the information to the console.
	:return: None
	"""
	global initialize_logger
	initialize_logger = logging.getLogger(__name__)
	initialize_logger.setLevel(logging.DEBUG)

	file_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt="%d-%b-%y %H:%M:%S")
	stream_formatter = logging.Formatter('%(levelname)s - function: %(funcName)s - %(message)s')

	file_handler = logging.FileHandler('initialize.log')
	file_handler.setFormatter(file_formatter)

	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(stream_formatter)

	initialize_logger.addHandler(file_handler)
	initialize_logger.addHandler(stream_handler)


def _get_todays_timestamp() -> str:
	"""Get today's timestamp

	:return:
	"""
	t = str(datetime.utcfromtimestamp(time.time()))
	timestamp = t[0: 10].replace("-", "_")

	return timestamp


def _read_from_json_file() -> dict:
	"""Read the data from the json file.

	Description:
		The Json contain the latest information obtain from CMC API.

	:return:
	"""

	timestamp = _get_todays_timestamp()

	with open(f'price-{timestamp}.json') as file:
		read_data = json.load(file)

	return read_data['data']


def insert_all(db, data_dump: dict):
	"""Insert all the records provided as parameters in the table "prices"

	:param db:
	:param data_dump:
	:return: None
	"""
	records = []

	for i in range(len(data_dump)):
		data = data_dump[i]
		r = (data['id'], data['name'], data['symbol'], data['slug'], data['cmc_rank'], data['date_added'],
		     data['max_supply'], data['circulating_supply'], data['total_supply'], data['last_updated'],
		     data['quote']['USD']['price'],
		     data['quote']['USD']['percent_change_1h'], data['quote']['USD']['percent_change_24h'],
		     data['quote']['USD']['percent_change_7d'], data['quote']['USD']['percent_change_30d'],
		     data['quote']['USD']['percent_change_60d'], data['quote']['USD']['percent_change_90d'])
		records.append(r)

	try:
		db.create_table()
		db.insert_many(records)
	except sqlite3.OperationalError as e:
		initialize_logger.exception(f"table doesn't exist.\nOriginal Traceback\n{e}")
	else:
		initialize_logger.info("values added to the database")


initialize_configure_logger()
initialize_logger.info('Creating connection do database ...')
db = Prices()
initialize_logger.info('Reading JSON file ...')
data_dump = _read_from_json_file()
initialize_logger.info('Inserting records ...')
insert_all(db=db, data_dump=data_dump)
