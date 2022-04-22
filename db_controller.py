from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from model import Price
from datetime import datetime
import time
import json

from sqlalchemy.engine.base import Engine, Connection


def sqlalchemy_configuration() -> Engine:
    engine = create_engine('sqlite:///prices.sqlite')
    return engine


def get_connection(engine: Engine) -> Connection:
    #TODO: Error handling
    conn = engine.connect()
    print(f"Connection establish")
    return conn


def _prepare_several_insert(data_dump) -> list:
    records = []
    for i in range(len(data_dump)):
        data = data_dump[i]
        price = Price(id=data['id'],
                      name=data['name'],
                      symbol=data['symbol'],
                      slug=data['slug'],
                      cmc_rank=data['cmc_rank'],
                      date_added=data['date_added'],
                      max_supply=data['max_supply'],
                      circulating_supply=data['circulating_supply'],
                      total_supply=data['total_supply'],
                      last_updated=data['last_updated'],
                      price=data['quote']['USD']['price'],
                      percent_change_1h=data['quote']['USD']['percent_change_1h'],
                      percent_change_24h=data['quote']['USD']['percent_change_24h'],
                      percent_change_7d=data['quote']['USD']['percent_change_7d'],
                      percent_change_30d=data['quote']['USD']['percent_change_30d'],
                      percent_change_60d=data['quote']['USD']['percent_change_60d'],
                      percent_change_90d=data['quote']['USD']['percent_change_90d'])
        records.append(price)
    return records


def insert_all(connection, data_dump):
    session = Session(bind=connection)
    records_to_insert = _prepare_several_insert(data_dump)
    session.add_all(records_to_insert)
    session.commit()
    print('')


def insert_single(connection, data: dict):
    session = Session(bind=connection)

    price = Price(id=data['id'],
                      name=data['name'],
                      symbol=data['symbol'],
                      slug=data['slug'],
                      cmc_rank=data['cmc_rank'],
                      date_added=data['date_added'],
                      max_supply=data['max_supply'],
                      circulating_supply=data['circulating_supply'],
                      total_supply=data['total_supply'],
                      last_updated=data['last_updated'],
                      price=data['quote']['USD']['price'],
                      percent_change_1h=data['quote']['USD']['percent_change_1h'],
                      percent_change_24h=data['quote']['USD']['percent_change_24h'],
                      percent_change_7d=data['quote']['USD']['percent_change_7d'],
                      percent_change_30d=data['quote']['USD']['percent_change_30d'],
                      percent_change_60d=data['quote']['USD']['percent_change_60d'],
                      percent_change_90d=data['quote']['USD']['percent_change_90d'])
    session.add(price)
    session.commit()


if __name__ == '__main__':
    engine = sqlalchemy_configuration()
    from model import init_price_table
    init_price_table(engine=engine)

    conn = get_connection(engine)
    t = str(datetime.utcfromtimestamp(time.time()))
    timestamp = t[0: 10].replace("-", "_")

    with open(f'price-{timestamp}.json') as file:
        read_data = json.load(file)
    # print(read_data['data'])

    insert_all(connection=engine, data_dump=read_data['data'])
