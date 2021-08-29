import re
import sqlite3
from Helpers import DateTimeFormatHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import NotificationHelper

async def CancelRaid(message, client):
  commands = message.content.split()

  # Get Index values for commands
  try:
    DateIndex = commands.index("!DateTime")
  except ValueError:
    await message.channel.send(f"!DateTime not defined.")
    return

  #check to ensure that there is a value after !Cancel that isn't another command
  if DateIndex == 1:
    await message.channel.send(f"No valid name present after !Cancel, please enter name of the party you're canceling after !Cancel.")
    return

  # Assign values to variables 
  try:
    Date = commands[DateIndex + 1]
    Time = commands[DateIndex + 2]
    DateTime = Date + " " + Time
  except:
    await message.channel.send(f"Unable to assign variables, please specify values after !DateTime")
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
    
  # Set name to strings between !Create and next command
  try:
    Name = " ".join(commands[1:DateIndex])
  except:
    await message.channel.send(f"Error collecting name of the run")
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

  # Find party through name and date for discord channel
  try:
    c.execute(f"SELECT ID, OrganizerUserID FROM Raids WHERE Name = (?) and Origin = (?) and Date = (?)", (Name, Origin, sqldatetime))
    row = c.fetchone()
    RaidID = row[0]
    Creator = row[1]
  except:
    await message.channel.send(f"Party {Name} not found.")
    conn.close()
    return

 # Check that the user attempting to cancel the party is the party leader
  if UserID != Creator:
    await message.channel.send(f"Only the party leader can cancel this raid.")
    conn.close()
    return

  # See if there are other members other than the leader, and send notifications to all
  if RaidID:
    try:
      c.execute(f"SELECT UserID FROM RaidMembers WHERE RaidID = (?) AND Origin = (?) AND UserID != (?)", (RaidID, Origin, Creator))
      UserIDs = c.fetchall()
    except:
      await message.channel.send(f"Something went wrong retrieving users")
      conn.close()
      return

    try:
      if UserIDs:
        c.execute(f"SELECT group_concat(UserID) FROM RaidMembers WHERE RaidID = (?) AND UserID != (?)", (RaidID, Creator))
        RaidMembers = c.fetchone()

        if RaidMembers:
          await NotificationHelper.NotifyRaidMembers(message, RaidMembers)
    except:
      await message.channel.send(f"Something went wrong retrieving raid members")
      conn.close()
      return  
  
  c.execute(f"DELETE FROM Raids WHERE ID = (?)", (RaidID,))
  c.execute(f"DELETE FROM RaidMembers WHERE RaidID = (?)", (RaidID,))
  conn.commit()
  conn.close()

  OrganizerDisplayName = await UserHelper.GetDisplayName(message, Creator, client)
  await message.channel.send(f"{OrganizerDisplayName} has cancelled the run {Name} on {DateTime}.")
