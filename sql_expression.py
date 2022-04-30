COLUMNS = [
	"id",
	"name",
	"symbol",
	"slug",
	"cmc_rank",
	"date_added",
	"max_supply",
	"circulating_supply",
	"total_supply",
	"last_updated",
	"price",
	"percent_change_1h",
	"percent_change_24h",
	"percent_change_7d",
	"percent_change_30d",
	"percent_change_60d",
	"percent_change_90d"]

CREATE_PRICES_TABLE = """
				CREATE TABLE IF NOT EXISTS prices(
					id integer PRIMARY KEY,
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

IS_TABLE_EXIST = """SELECT name FROM sqlite_master WHERE type='table' AND name=prices"""

IS_TABLE_EMPTY = """SELECT EXISTS (SELECT 1 FROM prices)"""

INSERT_PRICE_MANY = """INSERT OR IGNORE INTO prices VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

SELECT_LAST_UPDATED = """SELECT last_updated from prices"""

SELECT_CMC_IDS = """ SELECT id from prices"""

UPDATE_PRICE_MANY = """
			UPDATE prices SET
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

SELECT_ALL = """ SELECT * FROM prices """

DROP_TABLE = """ DROP TABLE prices"""

#####################################
DROP_INFO_TABLE = """ DROP TABLE info"""

CREATE_INFO_TABLE = """
			CREATE TABLE IF NOT EXISTS info(
				id INTEGER PRIMARY KEY,
				name TEXT,
				symbol TEXT,
				category TEXT,
				description MEDIUMTEXT,
				slug TEXT,
				logo TEXT,
				subreddit TEXT,
				notice TEXT,
				urls MEDIUMTEXT,
				platform TEXT,
				twitter_username TEXT,
				date_launched  TEXT,
				contract_address LONGTEXT,
				status TEXT, 
				FOREIGN KEY(id) REFERENCES prices(id))"""

INSERT_INFO_MANY = """INSERT OR IGNORE INTO info VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
