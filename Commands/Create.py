import re
import sqlite3
from Helpers import DateTimeFormatHelper
from Helpers import RoleHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import RoleIconHelper

async def CreateRaid(message, client):
  commands = message.content.split()

  # Get Index values for commands
  try:
    DateIndex = commands.index("!DateTime")
    RoleIndex = commands.index("!Role")
  except ValueError:
    await message.channel.send(f"!DateTime or !Role not defined.")
    return

  # Assign values to variables 
  try:
    Date = commands[DateIndex + 1]
    Time = commands[DateIndex + 2]
    Role = commands[RoleIndex + 1]
    DateTime = Date + " " + Time
  except:
    await message.channel.send(f"Unable to assign variables, please specify values to your commands.")
    return

  #DateTime verification
  pattern = re.compile(r'((\d{2})-(\d{2})-(\d{4})) (\d{2}):(\d{2})')
  match = pattern.match(DateTime)

  if not match:
    await message.channel.send(f"Invalid DateTime, please use format dd-mm-yyyy hh:mm")
    return

  # Sent datetime to function to format for SQL
  sqldatetime = await DateTimeFormatHelper.LocalToSqlite("message", DateTime)
  
  if sqldatetime == None:
    await message.channel.send(f"Invalid datetime received, please beware you cannot use dates in the past.")
    return

  # Role verification
  try:     
    RoleID = await RoleHelper.GetRoleID(Role)
  except:
    await message.channel.send(f"Invalid role, please enter a valid role, you can call !Roles to see available roles.")
    return

  # Creating variables for number of players in role, making one for role creator has chosen
  NumberOfCurrentTanks = 0
  NumberOfCurrentDps = 0
  NumberOfCurrentHealers = 0

  if Role == "Tank":
    NumberOfCurrentTanks = 1
  elif Role == "Dps":
    NumberOfCurrentDps = 1
  elif Role == "Healer":
    NumberOfCurrentHealers = 1
  else:
    pass

  # 1 Create raid without template, 
  # 1.1 Example command !CreateRaid TestRaid !DateTime 01-08-2021 19:00 !NrOfPlayers 24 !NrOfTanks 3 !NrOfDps 15 !NrOfHealers 6 !Role Tank

  if "!Template" not in commands:

    # Check that each required command is in split message
    try: 
      NrOfPlayersIndex = commands.index("!NrOfPlayers")
      NrOfTanksIndex = commands.index("!NrOfTanks")
      NrOfDpsIndex = commands.index("!NrOfDps")
      NrOfHealersIndex = commands.index("!NrOfHealers")
    except ValueError:
      await message.channel.send(f"!NrOfPlayers, !NrOfTanks, !NrOfDps, or NrOfHealers not defined, or use of !Template missing.")
      return

    # Check a variable can be set a value for each command
    try:
      NrOfPlayers = int(commands[NrOfPlayersIndex + 1])
      NrOfTanks = int(commands[NrOfTanksIndex + 1])
      NrOfDps = int(commands[NrOfDpsIndex + 1])
      NrOfHealers = int(commands[NrOfHealersIndex + 1])
    except ValueError:
      await message.channel.send(f"Ensure !NrOfPlayers, !NrOfTanks, !NrOfDps, or NrOfHealers value is a valid integer.")
      return
    except:
      await message.channel.send(f"Unable to assign variables, please specify values to your commands.")
      return

    # Check that number of players and roles are all above 0
    if any(x < 0 for x in [NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers]):
      await message.channel.send(f"Please ensure player and role values are equal to or greater than 0.")
      return

    #Ensure the number of players equals the sum of each role
    if NrOfPlayers != NrOfTanks + NrOfDps + NrOfHealers:
      await message.channel.send(f"Please ensure the total of each role equals the total number of players required.")
      return

    #Check that name is valid, first find first command after !Create
    MinIndexOfCommands = min(DateIndex, RoleIndex, NrOfPlayersIndex, NrOfTanksIndex, NrOfDpsIndex, NrOfHealersIndex)

    #check to ensure that there is a value after !Create that isn't another command
    if MinIndexOfCommands == 1:
      await message.channel.send(f"No valid name present after !Create, please name your run after !Create.")
      return
    
    # Set name to strings between !Create and next command
    try:
      Name = " ".join(commands[1:MinIndexOfCommands])
    except:
      await message.channel.send(f"Error collecting name of the run")
      return

  # 2 Create raid with template
  # 2.1 Example command !CreateRaid TestRaid !DateTime 01-08-2021 19:00 !Template Normal !Role Tank
  # Check message for all commands and split input into the following variables, RaidName, Origin, Creator, DateTime, TemplateName, Role
  else:
    TemplateIndex = commands.index("!Template")
    Template = commands[TemplateIndex + 1]

    #Check that name is valid, first find first command after !Create
    MinIndexOfCommands = min(DateIndex, RoleIndex, TemplateIndex)

    #check to ensure that there is a value after !Create that isn't another command
    if MinIndexOfCommands == 1:
      await message.channel.send(f"No valid name present after !Create, please provide a name for your run after !Create.")
      return

    # Set name to strings between !Create and next command
    try:
      Name = " ".join(commands[1:MinIndexOfCommands])
    except:
      await message.channel.send(f"Error collecting name of the raid")
      return

    # Open connection to the database
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()

    # Find Template and store values into rows
    try:
      c.execute(f"SELECT NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers FROM Templates WHERE Name = (?)", (Template,))

      row = c.fetchone()
    except:
      await message.channel.send(f"Template {Template} not found")
      conn.close()
      return

    try:        
      NrOfPlayers = row[0]
      NrOfTanks = row[1]
      NrOfDps = row[2]
      NrOfHealers = row[3]
    except:
      await message.channel.send(f"Error obtaining player / role numbers in database. Please ensure a valid template was used.")
      conn.close()   
      return

  #obtain origin and creator, for checking database for same origin + name/datetime
  Origin = await OriginHelper.GetOrigin(message)
  Creator = await UserHelper.GetUserID(message)

  if not Origin or not Creator:
    await message.channel.send(f"Error obtaining Discord IDs.")
    return

  # Open connection to the database
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # 2.3 Check if there's already a raid with the same origin + name
  try:
    c.execute(f"SELECT Name FROM Raids WHERE Origin = (?) and Name = (?) and OrganizerUserID = (?) and Date = (?)", (Origin, Name, Creator, sqldatetime))

    row = c.fetchone()
  except:
    conn.close()
    return

  if row:
    await message.channel.send("You are already leading a party for a run of this name and time.")
    conn.close()
    return

  # 2.4 Create query to insert raid into database
  try:
    c.execute(f"INSERT INTO Raids (Name, Origin, Date, OrganizerUserID, NrOfPlayersRequired, NrOfPlayersSignedUp, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfHealersSignedUp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (Name, Origin, sqldatetime, Creator, NrOfPlayers, 1, NrOfTanks, NumberOfCurrentTanks, NrOfDps, NumberOfCurrentDps, NrOfHealers, NumberOfCurrentHealers))
  except:
    await message.channel.send(f"Something went wrong trying to create the run")
    conn.close()
    return

  # Saving unique Raid ID to insert into next table
  RaidID = c.lastrowid

  #Create joining data for raid members with join on Raid ID
  try:
    c.execute(f"INSERT INTO RaidMembers (Origin, UserID, RaidID, RoleID) VALUES (?, ?, ?, ?)", (Origin, Creator, RaidID, RoleID))
    conn.commit()
    conn.close()
  except:
    await message.channel.send("Something went wrong trying to add you as a member to this run.")
    conn.close()
    return

  # Get role icons
  try:
    TankIcon = await RoleIconHelper.GetTankIcon(client, 'Tank')
    DpsIcon = await RoleIconHelper.GetDpsIcon(client, 'Dps')
    HealerIcon = await RoleIconHelper.GetHealerIcon(client, 'Healer')
  except:
    await message.channel.send(f"Something went wrong retrieving role icons")
    conn.close()
    return

  # 3 Post message to channel saying the raid is being formed
  await message.channel.send(f"Your crew is now being recruited: \n**Name:** {Name}\n**Date:** {DateTime}\n{TankIcon} {NumberOfCurrentTanks}\/{NrOfTanks} {DpsIcon} {NumberOfCurrentDps}\/{NrOfDps} {HealerIcon} {NumberOfCurrentHealers}\/{NrOfHealers}")
  conn.close()
  return