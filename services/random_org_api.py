import requests
import os
import numpy as np

def request_random_integers(quantity=1,times=1,max=20) -> list:
    values = quantity * times
    url = 'https://api.random.org/json-rpc/4/invoke'
    body = {
        "jsonrpc": "2.0",
        "method": "generateIntegers",
        "params": {
            "apiKey": os.getenv('RANDOM_ORG_API_KEY'),
            "n": values,  
            "min": 1,  
            "max": max,
            "replacement": True  
        },
        "id": 42
    }
    response = requests.post(url=url, json=body)
    json_dict:dict = response.json()
    response.raise_for_status()
    if 'error' in json_dict.keys():
        raise Exception(f'{json_dict['error']['code']} - {json_dict['error']['message']}')
    else:
        matrix = response.json()['result']['random']['data']
        matrix = np.reshape(matrix,(times,quantity)).tolist()
        return matrix