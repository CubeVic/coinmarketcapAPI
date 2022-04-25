import os
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time
from datetime import datetime


def cnc_configuration():
    global CNC_API_KEY
    global BASE_URL
    global SANDBOX_URL
    global HEADERS
    CNC_API_KEY = os.environ['COIN_API_KEY']
    BASE_URL = 'https://pro-api.coinmarketcap.com'
    SANDBOX_URL = 'https://sandbox-api.coinmarketcap.com'
    HEADERS = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CNC_API_KEY,
    }


def prepare_session(headers: dict) -> Session:
    session = Session()
    session.headers.update(headers)
    return session


def get_time() -> datetime:
    t = datetime.utcfromtimestamp(time.time())
    return t


def get_updated_prices(session: Session):
    """ Query the APi for the latest prices, it consumes credits.

  :param session:
  :return: json
  """
    time = str(get_time())[0:10].replace("-", "_")
    if os.path.exists(f"price-{time}.json"):
        print('File already exist')
    else:
        params = {
            'start': '1',
            'limit': '1000',
            'convert': 'USD',
        }
        endpoint = '/v1/cryptocurrency/listings/latest'
        url = BASE_URL + endpoint
        # url = SANDBOX_URL + endpoint
        response = session.get(url, params=params)
        data = json.loads(response.text)

        timestamp = data['status']['timestamp'].replace("-", "_").replace(":", "_")
        timestamp = timestamp[0:10]
        result = {'timestamp': data['status']['timestamp'],
                'data': data['data'] }
        with open(f'price-{timestamp}.json', 'w') as file:
            json.dump(result, file, indent=6)
            print(f'File created price-{timestamp}.json')
        return {'timestamp': data['status']['timestamp'],
                'data': data['data'] }


def get_map(session: Session):

    if os.path.exists(f"map.json"):
        print('passed')
    else:
        endpoint = '/v1/cryptocurrency/map'
        url = BASE_URL + endpoint
        params = {
            'sort': 'cmc_rank',
        }
        map_resp = session.get(url=url, params=params)
        map = json.loads(map_resp.text)
        with open('map.json', 'w') as file:
            json.dump(map['data'], file, indent=6)
            print(f'File map create')


def get_price_from_db(timestamp: datetime) -> dict:
    data = []
    with open(f'price-{timestamp}.json', 'r') as file:
      data = json.loads(file.read())
    return data


if __name__ == '__main__':
    cnc_configuration()
    session = prepare_session(headers=HEADERS)
    print(get_updated_prices(session=session))
