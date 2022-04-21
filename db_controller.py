# import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from model import Price


from sqlalchemy.engine.base import Engine, Connection

#
# Base = declarative_base()
#
#
# class Price(Base):
#     __tablename__ = 'prices'
#
#     name = Column(String)
#     fullname = Column(String)
#     nickname = Column(String)
#     Id = Column('Id', Integer(), primary_key=True)
#     name = Column('name', String(length=255), nullable=False)
#     symbol = Column('symbol', String(length=255))
#     slug = Column('slug', String(length=255))
#     data_added = Column('data_added', String(length=255))
#     max_supply = Column('max_supply', Float())
#     circulating_supply = Column('circulating_supply', Float())
#     total_supply = Column('total_supply', Float())
#     last_updated = Column('last_updated', DateTime())
#     price = Column('price', Float())
#     percent_change_1h = Column('percent_change_1h', Float())
#     percent_change_24h = Column('percent_change_24h', Float())
#     percent_change_7d = Column('percent_change_7d', Float())
#     percent_change_30d = Column('percent_change_30d', Float())
#     percent_change_60d = Column('percent_change_60d', Float())
#     percent_change_90d = Column('percent_change_90d', Float())


def sqlalchemy_configuration() -> Engine:
    engine = create_engine('sqlite:///prices.sqlite')
    return engine


def get_connection(engine: Engine) -> Connection:
    #TODO: Error handling
    conn = engine.connect()
    print(f"Connection establish")
    return conn

# def insert_table(tablename: ):
#     pass
#     # Building the query
#     ins = tablename


# Executing the Query

if __name__ == '__main__':
    engine = sqlalchemy_configuration()
    from model import init_price_table
    init_price_table(engine=engine)
    conn = get_connection(engine)

    session = Session(bind=engine)
    record = Price(Id=1,name='name',symbol='symbole', slug='slug', data_added='2022-04-21', max_supply=1.0, circulating_supply=1.0, total_supply=1.0, last_updated='2022-04-21', price=1.0,percent_change_1h=1.0, percent_change_24h= 1.0,percent_change_7d= 1.0, percent_change_30d= 1.0, percent_change_60d= 1.0, percent_change_90d=1.0)
    session.add(record)
    session.commit()