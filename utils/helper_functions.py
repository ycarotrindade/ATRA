import random
import numpy as np
import logging
from . import Player
from services import *
import re
import discord
from typing import Any, Tuple

def check_if_atra_syntax(message:str) -> bool:
    '''Check if the discord message is in the ATRA syntax
    # Args
        message: `str`
            Message from discord
    
    # Return
        A bool var if the message is in ATRA format
    '''
    atra_regex_syntax = r'^(?P<times>\d+#)?(?P<quantity>\d+d)(?P<max>\d+)?(?P<plus>\+\d+)?\s?(?P<phrase>.+)?$'
    results = re.match(atra_regex_syntax, message.replace(' ', ''))
    if results is None:
        return False
    else:
        return True
    

def apply_dice_logic(content: str, alg:str, ctx:discord.Message | discord.Interaction) -> Tuple[str, dict[str, Any]]:
    '''Apply all the roll dice logic 
    # Args
        content: `str`
            Message from discord
        
        alg: `str`
            The random algorithm used to generate values
        
        ctx: `discord.Message | discord.Interaction`
            The discord object to reply.
    
    # Return
        The string return_value to display, the arguments used and the dice values
    '''
    
    return_value = ''
    arguments = split_args(content)
    plus = 0
    if 'plus' in arguments:
        plus = int(arguments['plus'])
        arguments.pop('plus')
    
    phrase = ''
    if 'phrase' in arguments:
        phrase = '\''+ arguments['phrase'] + '\','
        arguments.pop('phrase')
    
    arguments['alg'] = alg
    values = generate_random_numbers(**arguments)
    
    if isinstance(ctx, discord.Message):
        logging.debug(f'{ctx.author.display_name} rolled a dice')
    elif isinstance(ctx, discord.Interaction):
        logging.debug(f'{ctx.user.display_name} rolled a dice')
    
    for matrix in values:
        formated_values = format_numbers(matrix,arguments['max'])
        string_part = phrase + f'`{sum(matrix)+plus}` ⟵ {formated_values}'
        string_part += f' + {plus}' if plus > 0 else ''
        return_value += f'{string_part}\n'

    if isinstance(ctx, discord.Message):
        return_value = f'{ctx.author.mention}\n{return_value}'
    elif isinstance(ctx, discord.Interaction):
        return_value = f'{ctx.user.mention}\n{return_value}'

    return return_value, arguments, values


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
        regex = r'^(?P<times>\d+#)?(?P<quantity>\d+d)(?P<max>\d+)?(?P<plus>\+\d+)?\s?(?P<phrase>[^\s]+)?$'
        arguments = re.match(regex,syntax).groupdict()
        arguments = {key:value for key, value in arguments.items() if value is not None}
        for key, value in arguments.items():
            match key:
                case 'times':
                    arguments[key] = value.removesuffix('#')
                case 'quantity':
                    arguments[key] = value.removesuffix('d')
                case 'plus':
                    arguments[key] = value.removeprefix('+')
        arguments = {key:int(value) for key,value in arguments.items()}
        if arguments == {}:
            raise Exception('No matches')
        
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
        quantity = int(quantity)
        times = int(times)
        max = int(max)
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