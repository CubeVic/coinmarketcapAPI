import sqlite3

conn = sqlite3.connect("cryptodatabase.db")
cur = conn.cursor()

cur.execute(""" CREATE TABLE prices(
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
                    percent_change_90d real)""")

def insert_all(data_dump):
    records = []
    for i in range(len(data)):
        data = data_dump[i]
        r = (data['id'],data['name'],data['symbol'],data['slug'],data['cmc_rank'],data['date_added'],data['max_supply'],
                data['circulating_supply'],data['total_supply'],data['last_updated'],data['quote']['USD']['price'],
                data['quote']['USD']['percent_change_1h'],data['quote']['USD']['percent_change_24h'],
                data['quote']['USD']['percent_change_7d'],data['quote']['USD']['percent_change_30d'],
                data['quote']['USD']['percent_change_60d'],data['quote']['USD']['percent_change_90d'])
        records.append(r)
    cur.executemany("""INSERT INTO prices
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", records)

conn.commit()
conn.close()