import discord
import os
import dotenv
from dotenv import load_dotenv
from discord.ext import commands
from Commands import Templates
from Commands import AddDefaultTemplates
from Commands import AddTemplate
from Commands import UpdateTemplate
from Commands import DeleteTemplate
from Commands import Create
from Commands import Join
from Commands import Withdraw
from Commands import Cancel
from Commands import Info
from Commands import Runs
from Commands import Reschedule
from Commands import ChangeRole
from Commands import Commands
from Commands import Roles
from Commands import Rally
from Commands import Dismiss
from Helpers import DeleteOldRaidDataHelper
from Scripts import MakeDatabase
from Scripts import InsertMasterData

# Enable privileged gateway intents as described on 
# https://discordpy.readthedocs.io/en/latest/intents.html 
# so we can access member objects to retrieve display names
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

#Initialize Discord client
client = discord.Client()
@client.event

# Do nothing if the message is from the bot
async def on_message(message):
  if message.author == client.user:
    return

  # Check if message only contains !Templates command
  if message.content == ('!Templates'):

    # Call GetTemplates command function and wait for function to finish
    await Templates.GetTemplates(message, client)
    return

  # Check if message starts with !Create command
  if message.content.startswith('!Create'):

    # Call CreateRaid function and wait for it to finish
    await Create.CreateRaid(message, client)
    return

  # Check if message starts with !Join command
  if message.content.startswith('!Join'):

    # Call join raid function and wait for it to finish
    await Join.JoinRaid(message, client)
    return

  # Check if message starts with !Withdraw command
  if message.content.startswith('!Withdraw'):

    # Call withdraw from raid function and wait for it to finish
    await Withdraw.WithdrawFromRaid(message, client)
    return

  # Check if message starts with !Cancel command
  if message.content.startswith('!Cancel'):

    # Call cancel raid function and wait for it to finish
    await Cancel.CancelRaid(message, client)
    return

  # Check if message starts with !Info command
  if message.content.startswith('!Info'):

    # Call get raid info function and wait for it to finish
    await Info.GetRaidInfo(message, client)
    return

  # Check if message starts with !Runs command
  if message.content.startswith('!Runs'):

    # Call list raids on specific date function and wait for it to finish
    await Runs.ListRunsOnDate(message, client)
    return

  # Check if message starts with !Reschedule command
  if message.content.startswith('!Reschedule'):

    # Call reschedule raid function and wait for it to finish
    await Reschedule.RescheduleRaid(message, client)
    return

  # Check if message starts with !ChangeRole command
  if message.content.startswith('!ChangeRole'):

    # Call change role function and wait for it to finish
    await ChangeRole.ChangeRole(message, client)
    return

  # Check if message only contains !Commands command
  if message.content == ('!Commands'):

    # Call commands function and wait for it to finish
    await Commands.ListCommands(message)
    return

  # Check if message only contains !Roles command
  if message.content == ('!Roles'):

    # Call list roles function and wait for it to finish
    await Roles.ListRoles(message)
    return

  # Command to add default templates
  if message.content == ('!AddDefaultTemplates'):
    await AddDefaultTemplates.AddDefaultTemplates(message)
    return

  # Command to add custom template
  if message.content.startswith('!AddTemplate'):
    await AddTemplate.AddTemplate(message)
    return

  # Command to update template
  if message.content.startswith('!UpdateTemplate'):
    await UpdateTemplate.UpdateTemplate(message)
    return

  # Command to delete template
  if message.content.startswith('!DeleteTemplate'):
    await DeleteTemplate.DeleteTemplate(message)
    return

  # Command to rally raid members
  if message.content.startswith('!Rally'):
    await Rally.Rally(message, client)
    return
  
  # Command to dismiss raid member
  if message.content.startswith('!Dismiss'):
    await Dismiss.DismissMember(message, client)
    return

  # Command to create database
  if message.content == ('!MakeDatabase'):
    await MakeDatabase.MakeDatabase(message)    

  # Command to insert master data
  if message.content == ('!InsertMasterData'):
    await InsertMasterData.InsertMasterData(message)

  # Command to delete old data
  if message.content == ('!DeleteOldData'):
    await DeleteOldRaidDataHelper.DeleteOldRaidData()

# Get bot token and run on server
load_dotenv()
client.run(os.getenv('Token'))