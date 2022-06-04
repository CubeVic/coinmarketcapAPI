# Introduction

[//]: # (![bumpver]&#40;https://img.shields.io/badge/unitest-code?style=for-the-badge&logo=python&logoColor=gray&color=ffffff&#41; )
![python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=blue&color=ffffff&labelColor=purple)
![Coin Market Cap](https://img.shields.io/badge/coinmarketcap-Code?style=for-the-badge&logo=coinmarketcap&logoColor=gray&color=ffffff)

[//]: # (![Coin Market Cap]&#40;https://img.shields.io/badge/CMC_API-{{version}}-purple?style=for-the-badge&logoColor=gray&color=ffffff&labelColor=purple&#41;)

![Version](https://img.shields.io/github/v/tag/sbcgua/abap-package-version-shield.svg?style=for-the-badge&&logoColor=gray&color=ffffff)

CMC_API is a Python-client for the Coin Market Cap API.   
This client provides support for the basic or free tier at the moment.
However, it is open for extension to anyone who has access to paid packages.  
It provides access to all the available endpoint on the API and produce a result similar to the original API with some 
minor difference. 
The most relevant difference is the addition of a list of keys available in each answer, as shown in the bellow example.

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


[//]: # (- Add your project logo.)

[//]: # (- Write a short introduction to the project.)

[//]: # (- If you are using badges, add them here.)

----------------------------------------
## :ledger: Index

- [About](#beginner-about)
  - [Why Use the Client](#Why use the Client:)
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
##  :beginner: About
The CoinMarketCap API is an API provided by the company with the same name. This API provides cryptocurrency data such as price, volume, market cap, and exchange data.

This project is a wrapper around this API that facilitates its usage for python projects.

### Why use the Client:

1. It will reduce the coding time since the code for request and parsing of the data is already done, and the user only needs to call a function. 
2. It provides the option to save the response data to save in credit calls for data that is not updated constantly.
3. It provides metadata information in the response. This metadata contains the "cost" per request in credits and a list of the keys in the data part of the response so users can retrieve information with ease.

## :zap: Usage
1. Decided with URL you will use:
   1. `BASE`:base is the real API and provide the real 
   data. `cmc_helper.Urls.BASE.value`
   2. `SANDBOX`: sandbox is for testing, and returns dummy data. `cmc_helper.Urls.SANDBOX.value`
2. Create an Object of class `Cmc()`, passing the URL to be use `cmc = Cmc(url=cmc_helper.Urls.BASE.value)`
3. use the object of type `Cmc()` to call a function. `cmc.get_cmc_id_map()`

```python
from cmc_api import cmc, cmc_helper

base_url = cmc_helper.Urls.BASE.value
cmc = cmc.Cmc(url=base_url)
cmc.get_cmc_id_map(listing_status="active", start=1, limit=1000)
```

##  :wrench: Development
Still working in this part but any contribution or suggestion is more than welcome

### :notebook: Pre-Requisites
- python=>3.10
- request

[//]: # (###  :nut_and_bolt: Development Environment)

[//]: # (Write about setting up the working environment for your project.)

[//]: # (- How to download the project...)

[//]: # (- How to install dependencies...)


###  :file_folder: File Structure
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

[//]: # ()
[//]: # (| No | File Name | Details )

[//]: # (|----|------------|-------|)

[//]: # (| 1  | index | Entry point)



## :cherry_blossom: Community

As metioned before the contribution guidelines are not done yet, but any report or suggestion will be appreciated 

 ###  :fire: Contribution

 Your contributions are always welcome and appreciated. Following are the things you can do to contribute to this project.

 1. **Report a bug** <br>
 If you think you have encountered a bug, and I should know about it, feel free to report it 
[here](https://github.com/CubeVic/coinmarketcapAPI/issues) and I will take care of it.


 ### :cactus: Branches

1. **`master`** is the main development branch.

2. **`main`** is the production branch.
3. **`Development`** is the experimental development branch.


### :exclamation: Guideline
Working on it.

[//]: # (## :question: FAQ)

[//]: # (You can optionally add a FAQ section about the project.)

##  :page_facing_up: Resources
If you want more information about the Coin market cap API you can visit their side [coinmarketcapAPI](https://coinmarketcap.com/api/documentation/v1/)

[//]: # (##  :camera: Gallery)

[//]: # (Pictures of your project.)

[//]: # (## :star2: Credit/Acknowledgment)

[//]: # (Credit the authors here.)

##  :lock: License
[MIT license]()