import sqlite3
import logging
from datetime import datetime
import time

from sql_expression import (COLUMNS,
							CREATE_PRICES_TABLE,
							DROP_TABLE,
							DROP_INFO_TABLE,
							INSERT_PRICE_MANY,
							SELECT_CMC_IDS,
							SELECT_ALL,
							SELECT_LAST_UPDATED,
							UPDATE_PRICE_MANY,
							CREATE_INFO_TABLE,
							INSERT_INFO_MANY
							)
import os


def _configure_logger():
	""" Configure the logger for this module
	Description:
		Configuration of two logger, one logger will log the information in a file, the second one will
		log the information to the console.
	:return: None
	"""
	global sql_logger
	sql_logger = logging.getLogger(__name__)
	sql_logger.setLevel(logging.INFO)

	file_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt="%d-%b-%y %H:%M:%S")
	stream_formatter = logging.Formatter('%(levelname)s - function: %(funcName)s - %(message)s')

	file_handler = logging.FileHandler('logs/model.log')
	file_handler.setFormatter(file_formatter)

	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(stream_formatter)

	sql_logger.addHandler(file_handler)
	sql_logger.addHandler(stream_handler)


class MydataBase:

	def __init__(self):
		_configure_logger()
		self.con = sqlite3.connect('cryptodatabase.db')
		sql_logger.info("Connecting to the de database")
		self.cur = self.con.cursor()


class Prices(MydataBase):

	def __init__(self):
		super(Prices, self).__init__()
		self.create_table()

	@staticmethod
	def columns_names() -> list:
		return COLUMNS

	def create_table(self):
		# self.cur.execute(DROP_TABLE)
		self.cur.execute(CREATE_PRICES_TABLE)
		sql_logger.debug('create table')

	def insert(self, item):
		self.cur.execute(INSERT_PRICE_MANY, item)
		sql_logger.debug('inserting item')
		self.con.commit()

	def insert_many(self, items):
		self.cur.executemany(INSERT_PRICE_MANY, items)
		sql_logger.debug('inserting items')
		self.con.commit()

	def read_all(self) -> (list, list):
		"""Return a tuple with the column names adn a list of all records

		:return:
		"""
		self.cur.execute(SELECT_ALL)
		sql_logger.info('fetching data')
		rows = self.cur.fetchall()
		return self.columns_names(), rows

	def update_all(self, items):

		timestamp = str(datetime.utcfromtimestamp(time.time()))[0:10].replace("-", "_")
		records = []

		if os.path.exists(f"json_files/price-{timestamp}.json"):
			sql_logger.info(f'File price-{timestamp}.json exist')
			try:
				last_updated_from_db = self.cur.execute(SELECT_LAST_UPDATED).fetchone()[0]
				sql_logger.info(f"Last updated - Database records: {last_updated_from_db}")
			except TypeError as e:
				sql_logger.exception(f"table in the database is empty.\n\tHere original Traceback\n\t{e}")
				sql_logger.info('Executing function insert_all to populate database')
				self.insert_many(items=items)
			else:
				last_updated_from_file = items[0]['last_updated']
				sql_logger.info(f"Last updated - json file: {last_updated_from_file}")
				if last_updated_from_db != last_updated_from_file:
					sql_logger.info('updating')
					for i in range(len(items)):
						data = items[i]
						r = (
							data['cmc_rank'],
							data['max_supply'],
							data['circulating_supply'],
							data['total_supply'],
							data['last_updated'],
							data['quote']['USD']['price'],
							data['quote']['USD']['percent_change_1h'], data['quote']['USD']['percent_change_24h'],
							data['quote']['USD']['percent_change_7d'], data['quote']['USD']['percent_change_30d'],
							data['quote']['USD']['percent_change_60d'], data['quote']['USD']['percent_change_90d'],
							data['id'])
						records.append(r)
						self.cur.executemany(UPDATE_PRICE_MANY, r)
				else:
					sql_logger.info('database no need update')
		self.con.commit()

	def select_last_updated(self) -> str:
		self.cur.execute(SELECT_LAST_UPDATED)
		try:
			row = self.cur.fetchone()[0]
			sql_logger.info(f'This is what we got:\n{row}')
		except Exception as e:
			sql_logger.error(f'something when wrong, maybe the database is empty\n{e}')
		return row

	def select_all_ids(self) -> str:
		self.cur.execute(SELECT_CMC_IDS)
		rows = self.cur.fetchall()
		id = ""
		for row in rows:
			id+=str(row[0])+","
		return id


class Info(MydataBase):

	def __init__(self):
		super(Info, self).__init__()
		self.create_table()

	def create_table(self):
		# self.cur.execute(DROP_INFO_TABLE)
		self.cur.execute(CREATE_INFO_TABLE)
		sql_logger.debug('create Info table')

	def insert(self, item):
		self.cur.execute(INSERT_INFO_MANY, item)
		sql_logger.debug('inserting Info item')
		self.con.commit()

	def insert_many(self, items):
		self.cur.executemany(INSERT_INFO_MANY, items)
		sql_logger.debug('inserting Info items')
		self.con.commit()

