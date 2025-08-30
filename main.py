import discord
from discord import app_commands
import os
from datetime import datetime
import logging
import dotenv
import traceback
from utils import *

dotenv.load_dotenv(override=True)

RANDOM_ALG:str

LOG_BASE_PATH = os.getenv('LOG_BASE_PATH')
os.makedirs(LOG_BASE_PATH,exist_ok=True)

LOG_FILE = os.path.join(LOG_BASE_PATH,f'log_{datetime.strftime(datetime.now(),'%d_%m_%Y')}.log')
logging.basicConfig(level=logging.DEBUG,encoding='utf-8',datefmt='(%H:%M:%S)',format='%(asctime)s - %(levelname)s - %(message)s',handlers=[logging.FileHandler(LOG_FILE),logging.StreamHandler()])

is_recording = False
use_channel_messages = True
user_recorder:discord.Member | discord.User = None
player_dict:dict[str,Player] = {}

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

@bot.event
async def on_message(message:discord.Message):
    global player_dict
    if message.author.bot:
        return
    try:
        return_value, arguments, values = apply_dice_logic(message.content, RANDOM_ALG, message)
        
        if is_recording:
            player_name = message.author.display_name
            if player_name not in player_dict:
                player_dict[player_name] = Player(player_name)
            values = np.array(values).reshape((1,-1)).flatten().tolist()
            player_dict[player_name].add_or_update_dices(arguments['max'],values)
        
        await message.reply(return_value)
    except:
        error_handler(logging.getLogger(),traceback.format_exc())

@bot.event
async def on_ready():
    global RANDOM_ALG
    logging.debug('Syncing commands')
    await tree.sync()
    logging.info(f'Bot connected {bot.user}')   
    RANDOM_ALG = 'python'
    logging.info(f'RANDOM_ALG = {RANDOM_ALG}')

@tree.command(name='roll',description='Roll a dice')
@app_commands.describe(
    dice = "The dice syntax"
)
async def roll(interaction:discord.Interaction,dice:str):
    global player_dict
    try:
        
        return_value, arguments, values = apply_dice_logic(dice, RANDOM_ALG, interaction)
        
        if is_recording:
            player_name = interaction.user.display_name
            if player_name not in player_dict:
                player_dict[player_name] = Player(player_name)
            values = np.array(values).reshape((1,-1)).flatten().tolist()
            player_dict[player_name].add_or_update_dices(arguments['max'],values)
                
        
    except Exception as e:
        error_handler(logging.getLogger(),traceback.format_exc())
        return_value = 'Sorry, an error ocurred, please try again later'
    finally:
        await interaction.response.send_message(return_value)
    
    

@tree.command(name='start_recorder',description='Start recording for statistics command')
async def start_recorder(interaction:discord.Interaction):
    global is_recording, user_recorder
    response = ''
    if not is_recording:
        is_recording = True
        user_recorder = interaction.user
        response = f'Recorder started by {user_recorder.mention}'
    else:
        response = f'Recorder already started by {user_recorder.mention}'
    logging.debug(f'is_recording = {is_recording} | user_recorder = {user_recorder}')
    await interaction.response.send_message(response)

@tree.command(name='stop_recorder',description='Stop recording for statistics command')
async def stop_recorder(interaction:discord.Interaction):
    global is_recording, user_recorder, player_dict
    try:
        if is_recording:
            is_recording = False
            user_recorder = None
            response = generate_stats(player_dict) + f'Recorder stoped by {interaction.user.mention}'
            player_dict = {}
        else:
            response = f'No active recorder'
        logging.debug(f'is_recording = {is_recording} | user_recorder = {user_recorder}')
    except:
        error_handler(logging.getLogger(),traceback.format_exc())
        response = 'Sorry, an error ocurred, please try again later'
    finally:
        await interaction.response.send_message(response)

@tree.command(name='change_alg',description='Changes the random algorithm used by ATRA to generate values')
@app_commands.describe(
    alg = 'The algorithm used by ATRA'
)
@app_commands.choices(
    alg = [
        app_commands.Choice(name='Python',value='python'),
        app_commands.Choice(name='RANDOM.ORG',value='random.org')
    ]
)
async def change_alg(interaction:discord.Interaction,alg:app_commands.Choice[str]):
    global RANDOM_ALG
    RANDOM_ALG = alg.value
    await interaction.response.send_message(f'Random Algorithm changed to {RANDOM_ALG}')

bot.run(os.getenv('DISCORD_API_KEY'))