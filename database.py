import sqlite3
from datetime import datetime
import json
import time
import logging
import os

# conn = sqlite3.connect("cryptodatabase.db")
# cur = conn.cursor()

CREATE_TABLE = """CREATE TABLE IF NOT EXISTS prices(
                    id integer,
                    name text,
                    symbol text,
                    slug text,
                    cmc_rank integer,
                    date_added text,
                    max_supply real,
                    circulating_supply real,
                    total_supply real,
                    last_updated text,
                    price real,
                    percent_change_1h real,
                    percent_change_24h real,
                    percent_change_7d real,
                    percent_change_30d real,
                    percent_change_60d real,
                    percent_change_90d real)"""

IS_TABLE = """SELECT name FROM sqlite_master 
                WHERE type='table' AND name=prices"""
IS_TABLE_EMPTY = """SELECT EXISTS (SELECT 1 FROM prices)"""

INSERT_MANY = """INSERT INTO prices
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

SELECT_LAST_UPDATED = """SELECT last_updated from prices"""

UPDATEMANY = """UPDATE prices 
                    SET cmc_rank=?,max_supply=?,circulating_supply=?,total_supply=?,last_updated=?,
                        price=?, percent_change_1h=?,percent_change_24h=?,percent_change_7d=?,percent_change_30d=?,
                        percent_change_60d=?,percent_change_90d=? 
                    WHERE id=?"""

def sqlconfigure():
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

    conn = sqlite3.connect("cryptodatabase.db")
    cur = conn.cursor()
    cur.execute(CREATE_TABLE)
    return conn, cur


def insert_all(conn, cur, data_dump):
    records = []
    for i in range(len(data_dump)):
        data = data_dump[i]
        r = (data['id'], data['name'], data['symbol'], data['slug'], data['cmc_rank'], data['date_added'], data['max_supply'],
                data['circulating_supply'], data['total_supply'], data['last_updated'], data['quote']['USD']['price'],
                data['quote']['USD']['percent_change_1h'],data['quote']['USD']['percent_change_24h'],
                data['quote']['USD']['percent_change_7d'],data['quote']['USD']['percent_change_30d'],
                data['quote']['USD']['percent_change_60d'],data['quote']['USD']['percent_change_90d'])
        records.append(r)
    cur.executemany(INSERT_MANY, records)
    logger.info("values added to the database")
    conn.commit()
    conn.close()


# Update records
def update_records(conn, cur, data_dump):
    t = str(datetime.utcfromtimestamp(time.time()))
    timestamp = t[0: 10].replace("-", "_")
    records = []

    if os.path.exists(f"price-{timestamp}.json"):
        logger.info(f'File price-{timestamp}.json exist')

        # Check if the table is empty
        if not cur.execute(IS_TABLE_EMPTY).fetchone()[0]:
            insert_all(conn=conn, cur=cur, data_dump=data_dump)
        else:

            last_updated_from_db = cur.execute(SELECT_LAST_UPDATED).fetchone()[0]

            last_updated_from_file = data_dump[0]['last_updated']
            if last_updated_from_db != last_updated_from_file:
                logger.info('updating')
                for i in range(len(data_dump)):
                    data = data_dump[i]
                    r = (data['cmc_rank'],data['max_supply'],data['circulating_supply'],data['total_supply'],data['last_updated'],
                        data['quote']['USD']['price'],data['quote']['USD']['percent_change_1h'],data['quote']['USD']['percent_change_24h'],
                        data['quote']['USD']['percent_change_7d'],data['quote']['USD']['percent_change_30d'],
                        data['quote']['USD']['percent_change_60d'],data['quote']['USD']['percent_change_90d'], data['id'])
                    records.append(r)
                cur.executemany(UPDATEMANY, records)
            else:
                logger.info('database no need update')
            conn.commit()
            conn.close()


def read_from_json_file():
    t = str(datetime.utcfromtimestamp(time.time()))
    timestamp = t[0: 10].replace("-", "_")

    with open(f'price-{timestamp}.json') as file:
        read_data = json.load(file)
    return read_data['data']

############################################
conn, cur = sqlconfigure()


data_dump = read_from_json_file()
# insert_all(data_dump)

update_records(conn=conn, cur=cur, data_dump=data_dump)