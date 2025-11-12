from app.support.warehouse.schemas import WarehouseRead
from app.support.customer.schemas import CustomerCreate
from app.support.item.schemas import ItemCreateRelation as schema

data = {
    "drink": {
        "image_path": "BQUlmkRvCzLmjqfWxCkZ",
        "subcategory": {
            "category": {
                "name": "suTRZglsBsTBNveMCnWC",
                "description": "XIHAnlLIbxRyQfxoqnsH",
                "description_ru": "deonOSYyUjPFGaEpHRHg",
                "description_fr": "yUqWciMlePpssXbqPEdT",
                "name_ru": None,
                "name_fr": None
            },
            "name": "AwuvZNcvdpfipeGbMoiU",
            "description": None,
            "description_ru": "bRfOvqReyRoNomLvQBYP",
            "description_fr": None,
            "name_ru": "acqjHAEBMBzBVpwzuwLD",
            "name_fr": "CaBjpMHeRkgNcIkxKetx"
        },
        "sweetness": None,
        "subregion": {
            "region": {
                "country": {
                    "name": "bjIyjnqaHBBqUABZJCXw",
                    "description": "oNVewJrnATaYdWJTPqeN",
                    "description_ru": None,
                    "description_fr": "bIdlDJTZuUIFNKsefzXj",
                    "name_ru": None,
                    "name_fr": None
                },
                "name": "pzcsUKjhVSdUOxQKKMSA",
                "description": None,
                "description_ru": None,
                "description_fr": None,
                "name_ru": None,
                "name_fr": None
            },
            "name": "THYaArUjRTywFDsHsOGB",
            "description": None,
            "description_ru": None,
            "description_fr": "KXVtGXZknAXHGZycyotK",
            "name_ru": "ESbEsxZPJltaQiYSxbGh",
            "name_fr": None
        },
        "title": "tBvZVphGicbrrzTxBQFp",
        "title_native": None,
        "subtitle_native": "JIimInbllbhxRTYpSzUm",
        "subtitle": "EoZdYOtwTqwfvhMwtCYJ",
        "alc": 0.8349344714803325,
        "sugar": 0.3105787959025933,
        "aging": None,
        "sparkling": True,
        "foods": [
            {
                "name": "RNAEsNpkOvREsUNbyZKf",
                "description": "gPeRQmyPPFcRTeOhZolL",
                "description_ru": "iYWPUSzwtQQhQcLgpQwR",
                "description_fr": "TONqNGqJBodPxvwEQLwo",
                "name_ru": None,
                "name_fr": None
            }
        ],
        "varietals": [
            {
                "varietal": {
                    "name": "koHrHYufeCMnEGKIoUnF",
                    "description": "uNdosxBXYBkyqPquGjwX",
                    "description_ru": None,
                    "description_fr": "eyUrRaefxMgdsmyVmJMF",
                    "name_ru": "JHGNTTAXjqbrNRscktYQ",
                    "name_fr": "ijWWcWXLnpMbOmYwdpga"
                },
                "percentage": None
            }
        ],
        "description": "FpSsqzwlbxbvTQWIHVsc",
        "description_ru": None,
        "description_fr": None
    },
    "warehouse": {
        "customer": {
            "login": "iWSRhjiMTGaFkkBvkdkR",
            "firstname": None,
            "lastname": None,
            "account": None
        },
        "name": "hQetDJqHksPsSwJzfKZd",
        "description": "zQCzzJodaONlizmKMwPf",
        "description_ru": None,
        "description_fr": "xeFtaBboPqjbMjrmvKYt",
        "name_ru": None,
        "name_fr": None
    },
    "volume": 0.30007054811384803,
    "price": 0.23660640740607253,
    "count": 9
}


try:
    _ = schema(**data)
except Exception as e:
    print(f'{e}')
