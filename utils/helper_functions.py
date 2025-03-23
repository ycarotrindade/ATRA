import requests
import random
import os
import numpy as np
import logging
from . import Player
from services import *

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

def generate_random_numbers(alg:str,quantity=1,times=1,max=20) -> list:
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
    try:
        match alg:
            case 'python':
                values = []
                for _ in range(times):
                    values.append([random.randint(1,max) for _ in range(quantity)])
                return values
            case 'random.org':
                return random_org_api.request_random_integers(quantity=quantity,times=times,max=max)
            case _:
                raise Exception('Alg not found')
    except Exception as e:
        raise e
        

def generate_stats(players:dict[str,Player]):
    '''Generate the stats texto for discord\n

    # Args
        players: `dict[str,Player]`
            The list of players
    
    # Return
        The stats string
    '''
    
    
    functions:dict[str,function] = {
        'mvp':mvp_function,
        'svp':svp_function,
        'jinxed':jinxed_function,
        'gambler':gambler_function,
        'abstinent':abstinent_function
    }
    
    titles:dict[str,dict[str,str|int]] = {
        'mvp':{
            'player':'Anywone :(',
            'value': 0,
            'desc':'more critics'
        },
        'svp':{
          'player':'Anywone :(',
          'value':0,
          'desc':'second more critics'
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
    
    for title in titles.keys():
        titles[title]['player'], titles[title]['value'] = functions[title](players)



    return_value = ''
    for title, values in titles.items():
        return_value += f'# {title.upper()}: {values['desc']}\n`{values['player']}` ({values['value']})\n\n'
    return return_value

def svp_function(players:dict[str,Player]):
    critics = []
    critics = [(player.n_critics()) for player in players.values()]
    unique_vals = np.unique(critics)
    
    second_value = 0
    if len(unique_vals) > 1:
        second_value = unique_vals[len(unique_vals)-2]
        if second_value > 0:
            indices = np.where(critics == second_value)[0]
            names = ', '.join(np.array(list(players.keys()))[indices])
        else:
            names = 'Anywone :('
    else:
        names = 'Anywone :('
    
    return names, second_value

def abstinent_function(players:dict[str,Player]):
    total = np.array([player.total_dices_rolled() for player in players.values()])
    max_value = np.min(total)
    indices = np.where(total == max_value)[0]
    names = ', '.join(np.array(list(players.keys()))[indices])
    return names, max_value

def gambler_function(players:dict[str,Player]):
    total = np.array([player.total_dices_rolled() for player in players.values()])
    max_value = np.max(total)
    indices = np.where(total == max_value)[0]
    names = ', '.join(np.array(list(players.keys()))[indices])
    return names, max_value

def jinxed_function(players:dict[str,Player]):
    critical_failures = []
    critical_failures = np.array([player.n_critical_failures() for player in players.values()])
    max_value = np.max(critical_failures)
    indices = np.where(critical_failures == max_value)[0]
    names = ', '.join(np.array(list(players.keys()))[indices])
    return names, max_value
    

def mvp_function(players:dict[str,Player]):
    critics = []
    critics = [player.n_critics() for player in players.values()]
    max_value = np.max(critics)
    indices = np.where(critics == max_value)[0]
    names = ', '.join(np.array(list(players.keys()))[indices])
    return names, max_value

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