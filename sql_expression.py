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

IS_TABLE_EXIST = """SELECT name FROM sqlite_master 
                WHERE type='table' AND name=prices"""
IS_TABLE_EMPTY = """SELECT EXISTS (SELECT 1 FROM prices)"""

INSERT_MANY = """INSERT INTO prices
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

SELECT_LAST_UPDATED = """SELECT last_updated from prices"""

UPDATE_MANY = """UPDATE prices SET 
					cmc_rank=?,
					max_supply=?,
					circulating_supply=?,
					total_supply=?,
					last_updated=?,
					price=?, 
					percent_change_1h=?,
					percent_change_24h=?,
					percent_change_7d=?,
					percent_change_30d=?,
					percent_change_60d=?,
					percent_change_90d=? 
						WHERE id=?"""