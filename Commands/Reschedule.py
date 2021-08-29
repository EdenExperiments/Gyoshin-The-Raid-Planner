import sqlite3
import datetime
from datetime import datetime
from Helpers import DateTimeFormatHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import RoleHelper
from Helpers import NotificationHelper

async def RescheduleRaid(message, client):

  commands = message.content.split()

  # Get Index values for commands
  try:
    DateIndex = commands.index("!DateTime")
    NewDateIndex = commands.index("!NewDateTime")
  except ValueError:
    await message.channel.send(f"!DateTime or !NewDateTime not defined.")

  # Assign values to variables 
  try:
    OldDate = commands[DateIndex + 1]
    OldTime = commands[DateIndex + 2]
    NewDate = commands[NewDateIndex +1]
    NewTime = commands[NewDateIndex +2]
    OldDate = OldDate +" "+ OldTime
    NewDate = NewDate +" "+ NewTime
  except:
    await message.channel.send(f"Unable to assign variables, please specify values to your commands.")

  # Sent datetime to function to format for SQLite and validation
  try:
    current_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M")    
    sqliteolddate = await DateTimeFormatHelper.LocalToSqlite(message, OldDate)
    sqlitenewdate = await DateTimeFormatHelper.LocalToSqlite(message, NewDate)

    if not sqliteolddate or not sqlitenewdate:
      await message.channel.send(f"Unable to convert dates")

    if sqliteolddate < current_date:
      await message.channel.send(f"You cannot reschedule runs with a date in the past")

    if sqlitenewdate < current_date:
      await message.channel.send(f"You cannot reschedule a run to a date in the past")
  except:
    await message.channel.send(f"Something went wrong converting the date values")

  # Generate raidname
  MinIndexOfCommands = min(DateIndex, NewDateIndex)

  try:
    RaidName = " ".join(commands[1:MinIndexOfCommands])
  except:
    await message.channel.send(f"Error collecting name of the run")

  # Get Discord server id
  Origin = await OriginHelper.GetOrigin(message)

  if not Origin:
    await message.channel.send(f"An error occurred trying to resolve the server ID")

  # Get user ID of the person who entered the commands
  Creator = message.author.id

  if not Creator:
    await message.channel.send(f"Something went wrong retrieving the user ID")

  # Get server display name of creator
  UserName = await UserHelper.GetDisplayName(message, Creator, client)

  if not UserName:
    await message.channel.send(f"Something went wrong resolving the users' display name")

  # Search if raid exists
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    c.execute(f"SELECT ID FROM Raids WHERE Name = (?) AND Origin = (?) AND OrganizerUserID = (?) AND Date = (?) AND NOT Status = 'Cancelled'", (RaidName, Origin, Creator, sqliteolddate))
    row = c.fetchone()
    RaidID = row[0]
  except:
    await message.channel.send(f"Run not found")
    conn.close()
    return

  if RaidID:
    try:
      # Check if there are members signed up besides the organizer
      try:
        c.execute(f"SELECT UserID FROM RaidMembers WHERE RaidID = (?) AND Origin = (?) AND UserID != (?)", (RaidID, Origin, Creator,))
        UserIDs = c.fetchall()
      except:
        await message.channel.send(f"Something went wrong retrieving users")
        conn.close()
        return

      try:
        if UserIDs:
          c.execute(f"SELECT group_concat(UserID) FROM RaidMembers WHERE RaidID = (?) AND UserID != (?)", (RaidID, Creator,))
          RaidMembers = c.fetchone()
          
          if RaidMembers:
            await NotificationHelper.NotifyRaidMembers(message, RaidMembers)
      except:
        await message.channel.send(f"Something went wrong retrieving raid members")
        conn.close()
        return

      # Delete all raidmembers that are not the creator of the raid
      try:
        c.execute(f"DELETE FROM RaidMembers WHERE RaidID = (?) AND UserID != (?) AND Origin = (?)", (RaidID, Creator, Origin,))        
      except:
        conn.close()
        return
      
      # Get role of the Creator
      try:
        c.execute(f"SELECT RoleID FROM RaidMembers WHERE RaidID = (?) AND UserID = (?) AND Origin = (?)", (RaidID, Creator, Origin,))
        row = c.fetchone()        
      except:
        conn.close()
        return

      if not row:
        await message.channel.send("Unable to find role of the creator of this run")
        conn.close()

      RoleID = row[0]

      if not RoleID:
        await message.channel.send("Unable to retrieve role id")
        conn.close()
        return

      RoleName = await RoleHelper.GetRoleName(RoleID)

      if not RoleName:
        await message.channel.send("Unable to resolve role name")
        conn.close()
        return

      # Update Raids table
      if RoleName == 'Tank':
        try:
          c.execute(f"Update Raids SET Date = (?), NrOfPlayersSignedUp = (?), NrOfTanksSignedUp = (?), NrOfDpsSignedUp = (?), NrOfHealersSignedUp = (?), Status = 'Forming' WHERE ID = (?)", (sqlitenewdate, 1, 1, 0, 0, RaidID,))
          conn.commit()
          conn.close()
        except:
          conn.close()
          return
      
      if RoleName == 'Dps':
        try:
          c.execute(f"Update Raids SET Date = (?), NrOfPlayersSignedUp = (?), NrOfTanksSignedUp = (?), NrOfDpsSignedUp = (?), NrOfHealersSignedUp = (?), Status = 'Forming' WHERE ID = (?)", (sqlitenewdate, 1, 0, 1, 0, RaidID,))
          conn.commit()
          conn.close()
        except:
          conn.close()
          return

      if RoleName == 'Healer':
        try:
          c.execute(f"Update Raids SET Date = (?), NrOfPlayersSignedUp = (?), NrOfTanksSignedUp = (?), NrOfDpsSignedUp = (?), NrOfHealersSignedUp = (?), Status = 'Forming' WHERE ID = (?)", (sqlitenewdate, 1, 0, 0, 1, RaidID,))
          conn.commit()
          conn.close()
        except:
          conn.close()
          return      

    except:
      await message.channel.send(f"Something went wrong updating the run")
      conn.close()
      return
  
  else:
    await message.channel.send(f"Run not found or you are not the creator of this raid, only the creator is allowed to reschedule")
    conn.close()
    return

  await message.channel.send(f"{UserName} has rescheduled the run {RaidName} from {OldDate} to {NewDate}, if you were signed up to this run you have to sign up again on the new date")
  conn.close()