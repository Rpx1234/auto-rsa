# Nelson Dane
# Script to automate RSA stock purchases

# Import libraries
import os
import sys
from datetime import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv
# Custom API libraries
from allyAPI import *
from robinhoodAPI import *
from fidelityAPI import *
# from webullAPI import *
from schwabAPI import *
from tradierAPI import *
from tastyAPI import *
from chaseAPI import *

supported_brokerages = ["all", "ally", "fidelity", 
                        "robinhood", "rh", "schwab", 
                        "tradier", "tasty", "tastytrade","chase"]

# Initialize .env file
load_dotenv()

# If first arg is "docker", run in docker mode
if len(sys.argv) > 1 and sys.argv[1] == "docker":
    docker_mode = True
    print("Running in docker mode")
else:
    docker_mode = False

# Function to convert string to boolean
async def stringToBool(string):
    true = ["true", "t", "yes", "y", "1"]
    if string.lower() in true:
        return True
    else:
        return False

# Function to get account holdings
async def get_holdings(accountName, AO=None, ctx=None):
    accountName = accountName.lower()
    if accountName in supported_brokerages:
        try:
            if accountName == "ally" or accountName == "all":
                await ally_holdings(ally_account if AO is None else AO, ctx)
        except:
            pass
        try:
            if accountName == "fidelity" or accountName == "all":
                await fidelity_holdings(fidelity_account if AO is None else AO, ctx)
        except:
                pass
        try:
            if accountName == "robinhood" or accountName == "rh" or accountName == "all":
                await robinhood_holdings(robinhood if AO is None else AO, ctx)
        except:
            pass
        try:
            if accountName == "schwab" or accountName == "all":
                await schwab_holdings(schwab if AO is None else AO, ctx)
        except:
            pass
        # if account == "webull" or account == "wb" or account == "all":
        #     await webull_holdings(webull_account, ctx)
        try:
            if accountName == "tradier" or accountName == "all":
                await tradier_holdings(tradier if AO is None else AO, ctx)
        except:
            pass
        try:
            if accountName == "tasty" or accountName == "tastytrade" or accountName == "all":
                await tastytrade_holdings(tastytrade if AO is None else AO, ctx)
        except:
            pass
    else:
        print("Error: Invalid broker")

# Function to place orders
async def place_order(wanted_action, wanted_amount, wanted_stock, single_broker, AO=None, DRY=True, ctx=None):
    # Only market day orders are supported, with limits as backups on selected brokerages
    wanted_time = "day"
    wanted_price = "market"
    try:
        # Input validation
        wanted_action = wanted_action.lower()
        if wanted_amount != "all":
            wanted_amount = int(wanted_amount)
        wanted_stock = wanted_stock.upper()
        single_broker = single_broker.lower()
        # Shut up, grammar is important smh
        if wanted_amount != "all":
            if wanted_amount > 1:
                grammar = "shares"
            else:
                grammar = "share"
        else:
            grammar = "share"
        print("==========================================================")
        print(f"Order: {wanted_action} {wanted_amount} {grammar} of {wanted_stock} on {single_broker}")
        print("==========================================================")
        print()
        # Buy/Sell stock on each account if "all"
        if single_broker == "all":
            # Ally
            await ally_transaction(ally_account if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
            # Fidelity
            await fidelity_transaction(fidelity_account if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
            # Robinhood
            await robinhood_transaction(robinhood if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
            # Schwab
            await schwab_transaction(schwab if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
            # Webull
            # await webull_transaction(webull_account, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
            # Tradier
            await tradier_transaction(tradier if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
            # Tastytrade
            await tastytrade_transaction(tastytrade if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
            # Chase
            await chase_transaction(tradier if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)

        elif single_broker == "ally":
            # Ally
            await ally_transaction(ally_account if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
        elif single_broker == "fidelity":
            # Fidelity
            await fidelity_transaction(fidelity_account if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
        elif single_broker == "robinhood" or single_broker == "rh":
            # Robinhood
            await robinhood_transaction(robinhood if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
        elif single_broker == "schwab":
            # Schwab
            await schwab_transaction(schwab if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
        # elif single_broker == "webull" or single_broker == "wb":
        #     # Webull
        #     await webull_transaction(webull_account, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
        elif single_broker == "tradier":
            # Tradier
            await tradier_transaction(tradier if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
        elif single_broker in ('tastytrade', 'tasty'):
            # Tastytrade
            await tastytrade_transaction(tastytrade if AO is None else AO, wanted_action, wanted_stock, wanted_amount, wanted_price, wanted_time, DRY, ctx)
        elif single_broker == "chase":
            # Chase
            await chase_transaction(tastytrade if AO is None else AO, wanted_action, wanted_stock, wanted_amount,
                                         wanted_price, wanted_time, DRY, ctx)
        else:
            # Invalid broker
            print("Error: Invalid broker")
            if ctx:
                await ctx.send("Error: Invalid broker")
    except Exception as e:
        print(traceback.format_exc())
        print(f"Error placing order: {e}")  
        if ctx:
            await ctx.send(f"Error placing order: {e}")

if __name__ == "__main__":
    # Get discord token and channel from .env file, setting channel to None if not found
    if not os.environ["DISCORD_TOKEN"]:
        raise Exception("DISCORD_TOKEN not found in .env file, please add it")
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    DISCORD_CHANNEL = os.getenv("DISCORD_CHANNEL", None)
    if DISCORD_CHANNEL:
        DISCORD_CHANNEL = int(DISCORD_CHANNEL)

    # Initialize Accounts
    print("==========================================================")
    print("Initializing Accounts...")
    print("==========================================================")
    print()
    ally_account = ally_init()
    print()
    fidelity_account = fidelity_init(DOCKER=True if docker_mode else False)
    print()
    try:
        robinhood = robinhood_init()
    except:
        print("Robinhood failed, retrying...")
        sleep(5)
        robinhood = robinhood_init()
    print()
    schwab = schwab_init()
    print()
    # webull_account = webull_init()
    # print()
    tradier = tradier_init()
    print()
    tastytrade = tastytrade_init()
    print()
    chase_account = chase_init(DOCKER=True if docker_mode else False)
    print()

    print("Waiting for Discord commands...")
    print()

    # Initialize discord bot
    # Bot intents
    intents = discord.Intents.all()
    # Discord bot command prefix
    bot = commands.Bot(command_prefix='!', intents=intents)
    bot.remove_command('help')
    print()
    print('Discord bot is started...')
    print()

    # Bot event when bot is ready
    if DISCORD_CHANNEL:
        @bot.event
        async def on_ready():
            channel = bot.get_channel(DISCORD_CHANNEL)
            await channel.send('Discord bot is started...')

    # Bot ping-pong
    @bot.command(name='ping')
    async def ping(ctx):
        print('ponged')
        await ctx.send('pong')

    # Help command
    @bot.command()
    async def help(ctx):
        await ctx.send('Available commands:')
        await ctx.send('!ping')
        await ctx.send('!help')
        await ctx.send('!holdings [all|ally|robinhood/rh|schwab|tradier]')
        await ctx.send('!rsa [buy|sell] [amount] [stock] [all|ally|robinhood/rh|schwab|tradier|chase] [DRY/true/false]')
        await ctx.send('!restart')
        
    # Main RSA command
    @bot.command(name='rsa')
    async def rsa(ctx, wanted_action, wanted_amount, wanted_stock, wanted_account, DRY):
        # Convert string to boolean
        DRY = await stringToBool(DRY)
        print(DRY)
        try:
            await place_order(wanted_action=wanted_action, wanted_amount=wanted_amount, wanted_stock=wanted_stock, single_broker=wanted_account, DRY=DRY, ctx=ctx)
        except discord.ext.commands.errors.MissingRequiredArgument:
            # Missing required argument
            print("Error: Missing required argument")
            await ctx.send("Error: Missing required argument")
        except Exception as e:
            # All other errors
            print(f"Error placing order: {e}")
            await ctx.send(f"Error placing order: {e}")
        print()
        print("Waiting for Discord commands...")
        print()
        
    # Holdings command
    @bot.command(name='holdings')
    async def holdings(ctx, broker):
        try:
            await get_holdings(accountName=broker, ctx=ctx)
        except Exception as e:
            print(f"Error getting holdings: {e}")
            await ctx.send(f"Error getting holdings: {e}")
        print()
        print("Waiting for Discord commands...")
        print()

    # Restart command
    @bot.command(name='restart')
    async def restart(ctx):
        print("Restarting...")
        print()
        await ctx.send("Restarting...")
        await bot.close()
        os._exit(0)

    # Run Discord bot
    bot.run(DISCORD_TOKEN)
    print('Discord bot is running...')
