
import os
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

API_KEY = os.environ['COIN_API_KEY']
BASE_URL = 'https://pro-api.coinmarketcap.com/'
SANDBOX_URL = 'https://sandbox-api.coinmarketcap.com/'
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': API_KEY,
}


def get_updated_prices(session):
  """ Query the APi for the latest prices, it consumes credits.

  :param session:
  :return: json
  """
  session.headers.update(headers)
  params = {
    'start' : '1',
    'limit' : '5000',
    'convert': 'USD',
  }
  endpoint = 'v1/cryptocurrency/listings/latest'
  url = BASE_URL + endpoint
  response = session.get(url, params=params)
  data = json.loads(response.text)

  timestamp = data['status']['timestamp'].replace("-", "_").replace(":", "_")
  with open(f'price-{timestamp}.json', 'w') as file:
    json.dump(data['data'], file, indent=6)
  return data


def get_map(session, endpoint):
  url = BASE_URL + endpoint
  params = {
    'sort': 'cmc_rank',
  }
  map_resp = session.get(url=url, params=params)
  map = json.loads(map_resp.text)
  with open('map.json','w') as file:
    json.dump(map['data'], file, indent=6)


def get_price_from_db(timestamp):
  data = []
  with open(f'price-{timestamp}.json', 'r') as file:
    data = json.loads(file.read())
  return data


if __name__ == '__main__':

  s = Session()
  # get_updated_prices(session=s)
  timestamp = '2022_04_18T08_23_29.742Z'
  data = get_price_from_db(timestamp=timestamp)
  for d in data:
    print(f"{d}\n{'+++++'*4}")