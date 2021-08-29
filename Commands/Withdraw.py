import sqlite3
from Helpers import DateTimeFormatHelper
from Helpers import OriginHelper
from Helpers import RoleHelper
from Helpers import UserHelper

async def WithdrawFromRaid(message, client):

  commands = message.content.split()

  # Get index values for commands
  try:
    WithdrawIndex = commands.index('!Withdraw')
    DateIndex = commands.index('!DateTime')
  except:
    await message.channel.send(f"Required command !DateTime not found")
  
  # Assign values to variables
  try:
    Name = " ".join(commands[WithdrawIndex + 1:DateIndex])  
    Date = commands[DateIndex + 1]
    Time = commands[DateIndex + 2]
  except:
    await message.channel.send(f"Unable to assign variables, please specify values to your commands")

  # Check if inputs provided start with !, throw error when they do
  if Name.startswith('!'):
    await message.channel.send(f"Invalid name provided, please make sure your name does not start with !")

  if Date.startswith('!'):
    await message.channel.send(f"Invalid date provided, please make sure your date does not start with !")
  
  if Time.startswith('!'):
    await message.channel.send(f"Invalid time provided, please make sure your time does not start with !")

  # Add date and time back together in 1 value
  datetime = f"{Date} {Time}"  

  # Convert to sqlite date format
  sqlitedate = await DateTimeFormatHelper.LocalToSqlite(message, datetime)

  if not sqlitedate:
    await message.channel.send("Something went wrong converting the date and time")

  # Get Origin
  Origin = await OriginHelper.GetOrigin(message)

  if not Origin:
    await message.channel.send("Something went wrong retrieving the server ID")

  UserID = await UserHelper.GetUserID(message)

  if not UserID:
    await message.channel.send("Something went wrong retrieving your user ID")

  # Open connection to DB
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Execute query to see if user is already signed up to raid
  try:
    c.execute(f"SELECT R.ID as RaidID, R.Name, RM.ID as RaidMemberID, RM.UserID, RM.RoleID, R.NrOfPlayersSignedUp, R.NrOfTanksSignedUp, R.NrOfDpsSignedUp, R.NrOfHealersSignedUp FROM Raids R JOIN RaidMembers RM ON R.ID = RM.RaidID WHERE R.Date = (?) AND R.Origin = (?) AND R.Name = (?) AND RM.UserID = (?)", (sqlitedate, Origin, Name, UserID,))
  except:
    await message.channel.send(f"Something went wrong checking if you're already signed up to this run")
    conn.close()
    
  row = c.fetchone()

  if row:
    RaidID = row[0]
    RaidName = row[1]
    RaidMemberID = row[2]
    UserID = row[3]
    RoleID = row[4]
    UserName = await UserHelper.GetDisplayName(message, UserID, client)

    if not UserName:
      await message.channel.send("Something went wrong retrieving the display name of a raid member")
      conn.close()

    # Get role name
    RoleName = await RoleHelper.GetRoleName(RoleID)

    # Update Raids table based on role retrieved
    if RoleName == 'Tank':
      try:        
        c.execute(f"Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, NrOfTanksSignedUp = NrOfTanksSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
        conn.commit()     
      except:
        await message.channel.send("An error occured updating the number of signed up players and tanks")
        conn.close()
        return
    elif RoleName == 'Dps':
      try:
        c.execute(f"Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, NrOfDpsSignedUp = NrOfDpsSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
        conn.commit()
      except:
        await message.channel.send("An error occured updating the number of signed up players and dps")
        conn.close()
        return
    elif RoleName == 'Healer':
      try:
        c.execute(f"Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, NrOfHealersSignedUp = NrOfHealersSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
        conn.commit()
      except:
        await message.channel.send("An error occured updating the number of signed up players and healers")
        conn.close()
        return
    else:
      await message.channel.send("An error occured trying to retrieve the role")
      conn.close()
      return

    # Delete RaidMembers child record
    try:
      c.execute(f"DELETE FROM RaidMembers WHERE ID = (?)", (RaidMemberID,))
      conn.commit()
    except:
      await message.channel.send("An error occured trying to remove you from this run")
      conn.close()
      return

    # Check if there are still members signed up
    try:
      c.execute(f"SELECT UserID FROM RaidMembers WHERE RaidID = (?)", (RaidID,))
      rows = c.fetchall()

      # Delete the raid if there is nobody signed up anymore
      if not rows:
        
        c.execute(f"DELETE FROM Raids WHERE ID = (?)", (RaidID,))
        conn.commit()
        await message.channel.send(f"{UserName} has withdrawn from the run {RaidName} on {datetime} as you were the only person signed up for this the run has been cancelled")
      else:
        await message.channel.send(f"{UserName} has withdrawn from the run {RaidName} on {datetime}")
    except:
      await message.channel.send(f"Something went wrong trying to withdraw")
    
  else:
    await message.channel.send(f"Unable to withdraw because you are not a member of this run")
    conn.close()
  
  conn.close()
  return