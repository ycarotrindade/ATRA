import numpy as np
import logging
from . import Player
import re
import discord
from typing import Any, Tuple, Iterator
from random_number_generator import RandomNumberGenerator

def apply_dice_logic(content: str, generator: RandomNumberGenerator, ctx:discord.Message | discord.Interaction) -> Tuple[str, dict[str, Any]]:
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
    
    if isinstance(ctx, discord.Message):
        logging.debug(f'{ctx.author.display_name} rolled a dice')
    elif isinstance(ctx, discord.Interaction):
        logging.debug(f'{ctx.user.display_name} rolled a dice')
    
    values, arguments = generator.generate_random_numbers(content)
    
    return_value = format_numbers(values, arguments)
        
    if isinstance(ctx, discord.Message):
        return_value = f'{ctx.author.mention}\n{return_value}'
    elif isinstance(ctx, discord.Interaction):
        return_value = f'{ctx.user.mention}\n{return_value}'

    return return_value, arguments, values
    

def format_numbers(matrix:list,arguments:list):
    '''Format numbers to send on discord
    
    # Args
        matrix: `list`
            The original values
        
        arguments: `list`
            The arguments used in dyce syntax
    
    # Return
        The string formated
    
    '''
    return_string = ''
    matrix_formated = list(zip(*matrix))
    for u_matrix in matrix_formated:
        
        string_part = ''
        for index, values in enumerate(u_matrix):
            if not isinstance(arguments[index], int):
                formated_values = '['
                for value in values:
                    if value == 1 or value == arguments[index]['maximum']:
                        formated_values += f"**{value}**, "
                    else:
                        formated_values += f"{value}, "
                formated_values = formated_values.removesuffix(", ")
                formated_values += ']'
                string_part += f"{formated_values} {arguments[index]['quantity']}d{arguments[index]['maximum']} "
                string_part += f"\'{arguments[index]['phrase']}\' " if arguments[index]['phrase'] is not None else ''
                string_part += "+ "
            else:
                string_part += f"{values} + "
        sum_matrix = sum([sum(x) for x in u_matrix])
        return_string += f"`{sum_matrix}` <-- {string_part.removesuffix(" + ")}\n"
    return return_string
    
        

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