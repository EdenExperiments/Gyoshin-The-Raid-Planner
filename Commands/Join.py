import re
import sqlite3
from Helpers import DateTimeFormatHelper
from Helpers import RoleHelper
from Helpers import UserHelper
from Helpers import NotificationHelper
from Helpers import OriginHelper

async def JoinRaid(message, client):
  commands = message.content.split()

  # Get Index values for commands
  try:
    DateIndex = commands.index("!DateTime")
  except ValueError:
    await message.channel.send(f"!DateTime not defined.")
    return

  try:
    RoleIndex = commands.index("!Role")
  except ValueError:
    await message.channel.send(f"!Role not defined.")
    return

  # Assign values to variables 
  try:
    Date = commands[DateIndex + 1]
    Time = commands[DateIndex + 2]
    Role = commands[RoleIndex + 1]
    DateTime = Date + " " + Time
  except:
    await message.channel.send(f"Please specify values after !DateTime or !Role")
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

  # Obtaining next index of first command, to know size of name after !Join
  MinIndexOfCommands = min(DateIndex, RoleIndex)

  #check to ensure that there is a value after !Join that isn't another command
  if MinIndexOfCommands == 1:
    await message.channel.send(f"No valid name present after !Join, please enter name of the run you're joining after !Join.")
    return
    
  # Set name to strings between !Create and next command
  try:
    Name = " ".join(commands[1:MinIndexOfCommands])
  except:
    await message.channel.send(f"Something went wrong collecting the run name after !Join.")
    return

  #obtain origin and userID, for inputs to database
  Origin = await OriginHelper.GetOrigin(message)
  UserID = await UserHelper.GetUserID(message)

  if not Origin or not UserID:
    await message.channel.send(f"Something went wrong resolving IDs.")
    return

  # Open database connection
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  #Collect required information from raid, number of players and roles, and if already formed or cancelled. 
  try:
    c.execute(f"SELECT ID, Origin, OrganizerUserID, NrOfPlayersRequired, NrOfPlayersSignedUp, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfHealersSignedUp, Status FROM Raids WHERE Name = (?) and Date = (?) and Origin = (?)", (Name, sqldatetime, Origin))
  except:
    await message.channel.send(f"Something went wrong organising party database.")
    conn.close()
    return

  try:
    row = c.fetchone()
  except:
    await message.channel.send(f"Unable to find party of name: {Name} for this Discord Channel.")
    conn.close()
    return

  try:
    RaidID = row[0]
    Origin = row[1]
    Organizer = row[2]
    NrOfPlayersRequired = row[3]
    NrOfPlayersSignedUp = row[4]
    NrOfTanksRequired = row[5]
    NrOfTanksSignedUp = row[6]
    NrOfDpsRequired = row[7]
    NrOfDpsSignedUp = row[8]
    NrOfHealersRequired = row[9]
    NrOfHealersSignedUp = row[10]  
    Status = row[11]
  except:
    await message.channel.send(f"Something went wrong collecting party information.")
    conn.close()
    return

  if Status != "Forming":
    await message.channel.send(f"Party is currently not forming, please ensure you're not joining an already formed or cancelled party.")  
    conn.close()
    return

  # Ensure that the user is not trying to join a raid they have already joined
  c.execute(f"SELECT ID FROM RaidMembers WHERE RaidID = (?) and UserID = (?)", (RaidID, UserID))

  usercheck = c.fetchone()

  if usercheck:
    await message.channel.send(f"You have already joined party {Name}.")
    conn.close()
    return

  # Update Raids table based on role retrieved
  if Role == 'Tank':
    if NrOfTanksSignedUp == NrOfTanksRequired:
      await message.channel.send(f"Party already has the required number of Tanks, please join with a different class.")
      conn.close()
      return
    else:
      try:        
        c.execute(f"Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp + 1, NrOfTanksSignedUp = NrOfTanksSignedUp + 1 WHERE Name = (?) and Date = (?) and Origin = (?)", (Name, sqldatetime, Origin))
        conn.commit()     
      except:
        await message.channel.send("An error occured updating the number of signed up players and tanks")
        conn.close()
        return
  elif Role == 'Dps':
    if NrOfDpsSignedUp == NrOfDpsRequired:
      await message.channel.send(f"Party already has the required number of DPS, please join with a different class.")
      conn.close()
      return
    else:
      try:
        c.execute(f"Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp + 1, NrOfDpsSignedUp = NrOfDpsSignedUp + 1 WHERE Name = (?) and Date = (?) and Origin = (?)", (Name, sqldatetime, Origin))
        conn.commit()
      except:
        await message.channel.send("An error occured updating the number of signed up players and dps")
        conn.close()
        return
  elif Role == 'Healer':
    if NrOfHealersSignedUp == NrOfHealersRequired:
      await message.channel.send(f"Party already has the required number of Healers, please join with a different class.")
      conn.close()
      return
    else:
      try:
        c.execute(f"Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp + 1, NrOfHealersSignedUp = NrOfHealersSignedUp + 1 WHERE Name = (?) and Date = (?) and Origin = (?)", (Name, sqldatetime, Origin))
        conn.commit()
      except:
        await message.channel.send("Something went wrong updating the number of signed up players and healers")
        conn.close()
        return
  else:
    await message.channel.send("An error occured trying to retrieve the role")
    conn.close()
    return

  # Insert user into raid members for raidID 
  c.execute(f"INSERT INTO RaidMembers (Origin, UserID, RaidID, RoleID) VALUES (?, ?, ?, ?)", (Origin, UserID, RaidID, RoleID))
  conn.commit()

  JoinedUserDisplayName = await UserHelper.GetDisplayName(message, UserID, client)
  await message.channel.send(f"{JoinedUserDisplayName} has joined party {Name} on {DateTime} as a {Role}!")

  # Check if party is now full and can be set to "Formed"
  if NrOfPlayersRequired == NrOfPlayersSignedUp + 1:
    try:  
      c.execute(f"UPDATE Raids SET Status = 'Formed' WHERE ID = (?) and Origin = (?)", (RaidID, Origin))
      conn.commit()
      await NotificationHelper.NotifyUser(message, Organizer)
      await message.channel.send(f"Your crew for {Name} on {DateTime}, has been assembled!")
    except:
      await message.channel.send(f"Something went wrong updating party status to formed.")

  conn.close()