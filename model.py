from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base


from sqlalchemy.engine.base import Engine
Base = declarative_base()


class Price(Base):
    __tablename__ = 'prices'

    id = Column('id', Integer(), primary_key=True)
    name = Column('name', String(length=255), nullable=False)
    symbol = Column('symbol', String(length=255))
    slug = Column('slug', String(length=255))
    cmc_rank = Column('cmc_rank', Integer())
    date_added = Column('data_added', String(length=255))
    max_supply = Column('max_supply', Float())
    circulating_supply = Column('circulating_supply', Float())
    total_supply = Column('total_supply', Float())
    last_updated = Column('last_updated', String())
    price = Column('price', Float())
    percent_change_1h = Column('percent_change_1h', Float())
    percent_change_24h = Column('percent_change_24h', Float())
    percent_change_7d = Column('percent_change_7d', Float())
    percent_change_30d = Column('percent_change_30d', Float())
    percent_change_60d = Column('percent_change_60d', Float())
    percent_change_90d = Column('percent_change_90d', Float())


def init_price_table(engine: Engine):
    #TODO: verify if the table exist and create one if it doesnt.
    print(engine.has_table(table_name='prices'))
    if engine.has_table(table_name='prices'):
        # drop the table if exist
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    else:
        Base.metadata.create_all(engine)
