import requests
import random
import os
import numpy as np
import logging
from . import Player

def split_args(syntax:str):
    '''Split dice syntax into a dict
    # Args
        syntax: `str`
            The original dice syntax
    
    # Return
        A `dict` with arguments as keys
    '''
    try:
        arguments = {}
        
        syntax = syntax.replace(' ','')
        
        if '+' in syntax:
            arguments['plus'] = int(syntax.split('+',maxsplit=1)[1])
            syntax = syntax.replace("+" + syntax.split('+',maxsplit=1)[1],'',1)
            
        if '#' in syntax:
            arguments['times'] = int(syntax.split('#',maxsplit=1)[0])
            syntax = syntax.replace(syntax.split('#',maxsplit=1)[0] + "#",'',1)
        
        arguments['quantity'] = int(syntax[:syntax.find('d')])
        arguments['max'] = int(syntax[syntax.find('d') + 1:])
    except Exception as e:
        raise e
    finally:
        return arguments
    

def format_numbers(matrix:list,max:int):
    '''Format numbers to send on discord
    
    # Args
        matrix: `list`
            The original values
        
        max: `int`
            The max value used to outline the text
    
    # Return
        The string formated
    
    '''
    string_return = '['
    for value in matrix:
        string_return += f'**{value}**, ' if value == max else f'{value}, '
    string_return = string_return.removesuffix(', ')
    string_return +=']'
    return string_return

def generate_random_numbers(quantity=1,times=1,max=20) -> list:
    '''Generate random numbers, if ISTEST env variable is True, this function will use python built-in function else will use RANDOM.ORG API
    
    # Args
        quantity: `int`
            The number of times the dice will be used uniquely
            
        max: `int`
            The max value for the dice
            
        dices: `int`
            The number of times the dice will be used in a result
    
    # Return
        A matrix with the random values
    
    '''
    if not eval(os.getenv('ISTEST')):
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
        response = requests.post(url,json=body)
        json_dict:dict = response.json()
        if 'error' in json_dict.keys():
            raise Exception(f'{json_dict['error']['code']} - {json_dict['error']['message']}')
        else:
            matrix = response.json()['result']['random']['data']
            matrix = np.reshape(matrix,(times,quantity)).tolist()
            return matrix
    else:
        values = []
        for _ in range(times):
            values.append([random.randint(1,max) for x in range(quantity)])
        return values

def generate_stats(players:dict[str,Player]):
    '''Generate the stats texto for discord\n

    # Args
        players: `dict[str,Player]`
            The list of players
    
    # Return
        The stats string
    '''
    
    
    titles:dict[str,dict[str,str|int]] = {
        'mvp':{
            'player':'Anywone :(',
            'value': 0,
            'desc':'more critics'
        },
        'jinxed':{
            'player':'Anywone :(',
            'value': 0,
            'desc':'more critical failures'
        },
        'gambler':{
            'player':'Anywone :(',
            'value':0,
            'desc':'more dice rolled'
        },
        'abstinent':{
            'player':'Anywone :(',
            'value':0,
            'desc':'less dice rolled'
        }
    }
    
    for player in players.values():
        critics = player.n_critics()
        if critics > titles['mvp']['value']:
            titles['mvp']['value'] = critics
            titles['mvp']['player'] = player.name
        elif critics == titles['mvp']['value'] and titles['mvp']['value'] > 0:
            titles['mvp']['player'] += f', {player.name}'
            
        failures = player.n_critical_failures()
        if failures > titles['jinxed']['value']:
            titles['jinxed']['value'] = failures
            titles['jinxed']['player'] = player.name
        elif failures == titles['jinxed']['value'] and titles['jinxed']['value'] > 0:
            titles['mvp']['player'] = f', {player.name}'
        
        dices = player.total_dices_rolled()
        if dices > titles['gambler']['value']:
            titles['gambler']['player'] = player.name
            titles['gambler']['value'] = dices
        
        if dices < titles['abstinent']['value'] or titles['abstinent']['value'] == 0:
            titles['abstinent']['player'] = player.name
            titles['abstinent']['value'] = dices
        
    
    return_value = ''
    for title, values in titles.items():
        return_value += f'# {title.upper()}: {values['desc']}\n`{values['player']}` ({values['value']})\n\n'
    return return_value
        
def error_handler(logger:logging.Logger,traceback_string:str):
    '''Formats traceback string and log
    
    # Args
    traceback_string: `str`
        The original traceback string
    
    logger: `Logger`
        The logger used in the project
    
    '''
    traceback_list = traceback_string.splitlines()
    list(map(lambda msg:logger.error(msg),traceback_list))