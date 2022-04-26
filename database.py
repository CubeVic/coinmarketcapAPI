import sqlite3
from sqlite3 import Connection, Cursor
from datetime import datetime
import json
import time
import logging
import os
from sql_expression import CREATE_TABLE, IS_TABLE_EXIST, IS_TABLE_EMPTY, INSERT_MANY, SELECT_LAST_UPDATED, UPDATE_MANY


def _configure_logger():
	""" Configure the logger for this module
	Description:
		Configuration of two logger, one logger will log the information in a file, the second one will
		log the information to the console.
	:return: None
	"""
	global logger
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)

	file_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt="%d-%b-%y %H:%M:%S")
	stream_formatter = logging.Formatter('%(levelname)s - function: %(funcName)s - %(message)s')

	file_handler = logging.FileHandler('sql.log')
	file_handler.setFormatter(file_formatter)

	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(stream_formatter)

	logger.addHandler(file_handler)
	logger.addHandler(stream_handler)


def sql_configure() -> (Connection, Cursor):
	"""Configuration for the SQL, it will create a connection and a table if it doesn't exist.
	Description:
		It will create a connection to the database and a table called "prices".
		Table prices will contain the information for the crytpo.

	:return: connector, cursor
	"""
	_configure_logger()
	connection = sqlite3.connect("cryptodatabase.db")
	cursor = connection.cursor()
	cursor.execute(CREATE_TABLE)
	return connection, cursor


def insert_all(connection: Connection, cursor: Cursor, data_dump: dict):
	"""Insert all the records provided as parameters in the table "prices"

	:param connection:
	:param cursor:
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
		cursor.executemany(INSERT_MANY, records)
	except sqlite3.OperationalError as e:
		logger.exception(f"table doesn't exist.\nOriginal Traceback\n{e}")
	else:
		connection.commit()
		logger.info("values added to the database")
	finally:
		connection.close()


# Update records
def update_records(connection: Connection, cursor: Cursor, data_dump: dict):
	"""Update the records in the database

	Description:
		Update all the records in the database,
		it needs a payload with the data that will be used to update the database

	:param connection:
	:param cursor:
	:param data_dump:
	:return:
	"""
	timestamp = _get_todays_timestamp()
	records = []

	if os.path.exists(f"price-{timestamp}.json"):
		logger.info(f'File price-{timestamp}.json exist')

		try:
			last_updated_from_db = cursor.execute(SELECT_LAST_UPDATED).fetchone()[0]
		except TypeError as e:
			logger.exception(f"table in the database is empty.\n\tHere original Traceback\n\t{e}")
			logger.info('Executing function insert_all to populate database')
			insert_all(connection=connection, cursor=cursor, data_dump=data_dump)
		else:
			last_updated_from_file = data_dump[0]['last_updated']
			if last_updated_from_db != last_updated_from_file:
				logger.info('updating')
				for i in range(len(data_dump)):
					data = data_dump[i]
					r = (data['cmc_rank'], data['max_supply'], data['circulating_supply'], data['total_supply'],
						 data['last_updated'],
						 data['quote']['USD']['price'],
						 data['quote']['USD']['percent_change_1h'],data['quote']['USD']['percent_change_24h'],
						 data['quote']['USD']['percent_change_7d'], data['quote']['USD']['percent_change_30d'],
						 data['quote']['USD']['percent_change_60d'], data['quote']['USD']['percent_change_90d'],
						 data['id'])
					records.append(r)
					cursor.executemany(UPDATE_MANY, records)
				else:
					logger.info('database no need update')
			connection.commit()
		finally:
			connection.close()


def read_from_json_file() -> dict:
	"""Read the data from the json file.

	Description:
		The Json contain the latest information obtain from CMC API.

	:return:
	"""

	timestamp = _get_todays_timestamp()

	with open(f'price-{timestamp}.json') as file:
		read_data = json.load(file)
	return read_data['data']


def _get_todays_timestamp() -> str:
	"""Get today's timestamp

	:return:
	"""
	t = str(datetime.utcfromtimestamp(time.time()))
	timestamp = t[0: 10].replace("-", "_")
	return timestamp


def update_records_from_json_file():
	try:
		data_dump = read_from_json_file()
	except Exception as e:
		logging.exception(f"Error getting data from json file")

	try:
		conn, cur = sql_configure()
	except Exception as e:
		logging.error(f"====Error====\n{e}")
	else:
		update_records(connection=conn, cursor=cur, data_dump=data_dump)

