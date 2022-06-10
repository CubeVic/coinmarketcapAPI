# Introduction


![python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=blue&color=ffffff&labelColor=purple)
![Coin Market Cap](https://img.shields.io/badge/coinmarketcap-Code?style=for-the-badge&logo=coinmarketcap&logoColor=gray&color=ffffff)

CMC_API is a Python-client for the Coin Market Cap API.   

This client provides support for the basic or free tier at the moment.
However, it is open for extension to anyone who has access to paid packages.  

It provides access to all the available endpoints on the API and produces a result similar to the original API with some 
minor difference. 
The most relevant difference is the addition of a list of keys available in each answer, as shown in the below example.
```json
{
      "metadata": {
            "timestamp": "2022-06-04T04:26:55.117Z",
            "credit_count": 0,
            "error_message": null,
            "list_keys": [
                  "plan",
                  "usage"
            ]
      },
...
```

----------------------------------------
## Index

- [About](#beginner-about)
  - [Why Use the Client](#Why use the Client)
- [Usage](#zap-usage)
- [Deployment](#rocket-deployment)  
  - [Pre-Requisites](#Pre-Requisites)
  - [File Structure](#File-Structure)
- [Community](#cherry_blossom-community)
  - [Contribution](#fire-contribution)
  - [Branches](#cactus-branches)
  - [Guideline](#exclamation-guideline)  
- [Resources](#page_facing_up-resources)
- [License](#lock-license)
----------------------------------------
##  About
The CoinMarketCap API is an API provided by the company with the same name. This API provides cryptocurrency data such as price, volume, market cap, and exchange data.

This project is a wrapper around this API that facilitates its usage for python projects.

### Why use the Client:

1. It will reduce the coding time since the code for request and parsing of the data is already done, and the user only needs to call a function. 
2. It provides the option to save the response data to save in credit calls for data that is not updated constantly.
3. It provides metadata information in the response. This metadata contains the "cost" per request in credits and a list of the keys in the data part of the response so users can retrieve information with ease.

## Usage
1. Decided with URL you will use:
   1. `BASE`:base is the real API and provide the real 
   data. `cmc_helper.Urls.BASE.value`
   2. `SANDBOX`: sandbox is for testing, and returns dummy data. `cmc_helper.Urls.SANDBOX.value`
2. Create an Object of class `Cmc()`, passing the URL to be use `cmc = Cmc(url=cmc_helper.Urls.BASE.value)`
3. use the object of type `Cmc()` to call a function. `cmc.get_cmc_id_map()`

```python
from cmc_api import cmc, cmc_helper

base_url = cmc_helper.Urls.BASE.value
cmc = cmc.Cmc(url=base_url, api_key="YOU_LICENSE_KEY", save_to_json=True)
cmc.get_cmc_id_map(listing_status="active", start=1, limit=1000)
```
The response will be similar to:

```json
{
  "metadata": {
    "timestamp": "2022-06-04T13:14:05.108Z",
    "credit_count": 1,
    "error_message": null,
    "list_keys": [
      "id",
      "name",
      "symbol",
      "slug",
      "rank",
      "is_active",
      "first_historical_data",
      "last_historical_data",
      "platform"
    ]
  },
  "data": [
    {
      "id": 1,
      "name": "Bitcoin",
      "symbol": "BTC",
      "slug": "bitcoin",
      "rank": 1,
      "is_active": 1,
      "first_historical_data": "2013-04-28T18:47:21.000Z",
      "last_historical_data": "2022-06-04T13:09:00.000Z",
      "platform": null
    },
    ...
  ]
}
```

##  Development
Still working in this part but any contribution or suggestion is more than welcome

### Pre-Requisites
- python=>3.10
- request


### File Structure
This is the structure of this repository not of a project using this python-client.

```
.
├── coinmarketcapAPI
│   ├── json_files
│   │   ├── API_info.json
│   │   └── ...
│   └── src
│       ├── cmc_api
│       │   ├── cmc.py              # definition of the wrapper and function available
│       │   └── cmc_dataHandler.py  # Helper to parse the information on the API response
│       │   └── cmc_helper.py       # Emuns that hold the endpoinrs URI and args need it
│       │   └── cmc_utils.py        # Extra utility functions.
│       └── logs
│           └── *.logs
│           └── ....
├── LICENSE
├── MANIFEST.in
├── pyproject.toml
├── setup.cfg
└── README.md
```

## Community

As mentioned before the contribution guidelines are not done yet, but any report or suggestion will be appreciated 

### Contribution

 Your contributions are always welcome and appreciated. Following are the things you can do to contribute to this project.

* **Report a bug** <br>
 If you think you have encountered a bug, and I should know about it, feel free to report it 
[here](https://github.com/CubeVic/coinmarketcapAPI/issues), and I will take care of it.


 ### Branches

1. **`main`** is the production branch.
2. **`Development`** is the experimental development branch.

## Resources
If you want more information about the Coin market cap API you can visit their side [coinmarketcapAPI](https://coinmarketcap.com/api/documentation/v1/)


## License
[MIT license](https://github.com/CubeVic/coinmarketcapAPI/blob/main/LICENSE)