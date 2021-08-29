import re
import sqlite3
from datetime import datetime
from datetime import timedelta
from Helpers import DateTimeFormatHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import NotificationHelper

async def Rally(message, client):
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
    await message.channel.send(f"Something went wrong with name of the party after !Rally.")
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
    c.execute(f"SELECT ID, Date FROM Raids WHERE Name = (?) and Origin = (?) and Date = (?)", (Name, Origin, sqldatetime))
    row = c.fetchone()
    RaidID = row[0]
    DateTime = row[1]
  except:
    await message.channel.send(f"Party {Name} not found.")
    conn.close()
    return

  # Check to see if user is a member of party.
  try:
    c.execute(f"SELECT ID FROM RaidMembers WHERE RaidID = (?) and UserID = (?)", (RaidID, UserID))
    row = c.fetchone()
  except:
    await message.channel.send(f"Only members of {Name} can rally the crew.")
    conn.close()
    return

  #check that the set time is within the next hour
  now = datetime.utcnow()
  DateTime = datetime.strptime(DateTime, "%Y-%m-%d %H:%M")
  TimeDifference = DateTime - now
  if TimeDifference > timedelta(0) and TimeDifference < timedelta(hours = 2):
    #Complete Notifications
    try:
      c.execute(f"SELECT group_concat(UserID) FROM RaidMembers WHERE RaidID = (?) AND UserID != (?)", (RaidID, UserID))
      RaidMembers = c.fetchone()

      if RaidMembers[0] == None:
          conn.close()
          await message.channel.send(f"No one else in the crew to rally.")
      elif RaidMembers:
        await NotificationHelper.NotifyRaidMembers(message, RaidMembers)
        TimeTillRun = TimeDifference.seconds // 60
        await message.channel.send(f"Get ready crew! Only {TimeTillRun} minutes left until you assemble for {Name}!")
        conn.close()
      else:
        await message.channel.send(f"Something went wrong resolving members of crew.")
        conn.close()
        return
    except:
      await message.channel.send(f"Something went wrong with gathering the names of the crew.")
      conn.close()
      return
  else:
    await message.channel.send(f"You can only rally the crew within an hour of the set time.")
    conn.close()
    return
  

