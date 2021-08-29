import re
import sqlite3
from Helpers import DateTimeFormatHelper
from Helpers import RoleHelper
from Helpers import OriginHelper
from Helpers import UserHelper

# !ChangeRole TestRaid !DateTime 01-08-2021 19:00 !Role Tank

async def ChangeRole(message, client):
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
    UserID = message.author.id
  except:
    await message.channel.send(f"Unable to assign variables, please specify values to your commands.")
    return

  # DateTime verification
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

  # Get discord server ID
  Origin = await OriginHelper.GetOrigin(message)

  #Check that name is valid, first find first command after !Create
  MinIndexOfCommands = min(DateIndex, RoleIndex)

  #check to ensure that there is a value after !Create that isn't another command
  if MinIndexOfCommands == 1:
      await message.channel.send(f"No valid name present after !ChangeRole, please provide a name for your run after !ChangeRole.")
      return
    
  # Set name to strings between !Create and next command
  try:
    Name = " ".join(commands[1:MinIndexOfCommands])
  except:
    await message.channel.send(f"Error collecting name of the raid")
    return

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    c.execute(f"SELECT RM.RoleID, RM.ID, R.ID, R.NrOfTanksRequired, R.NrOfTanksSignedUp, R.NrOfDpsRequired, R.NrOfDpsSignedUp, R.NrOfHealersRequired, R.NrOfHealersSignedUp FROM RaidMembers RM JOIN Raids R ON R.ID = RM.RaidID WHERE RM.Origin = (?) AND R.Name = (?) AND R.Date = (?) AND RM.UserID = (?)", (Origin, Name, sqldatetime, UserID))

    row = c.fetchone()

    OldRoleID = row[0]
    RaidMemberID = row[1]
    RaidID = row[2]
    NrOfTanksRequired = row[3]
    NrOfTanksSignedUp = row[4]
    NrOfDpsRequired = row[5]
    NrOfDpsSignedUp = row[6]
    NrOfHealersRequired = row[5]
    NrOfHealersSignedUp = row[6]

    OldRoleName = await RoleHelper.GetRoleName(OldRoleID)
    NewRoleID = await RoleHelper.GetRoleID(Role)
    NewRoleName = str(Role)
    
    UserID = message.author.id
    DisplayName = await UserHelper.GetDisplayName(message, UserID, client)
  except:
    await message.channel.send(f"Run or role not found")
    conn.close()

  if (OldRoleID != NewRoleID):
    try:
      c.execute(f"UPDATE RaidMembers set RoleID = (?) WHERE ID = (?) AND Origin = (?)", (NewRoleID, RaidMemberID, Origin,))

      # Change roles
      # Change from tank to dps
      if OldRoleName == 'Tank' and NewRoleName == 'Dps' and NrOfDpsSignedUp < NrOfDpsRequired:
        c.execute(f"UPDATE Raids set NrOfTanksSignedUp = NrOfTanksSignedUp - 1, NrOfDpsSignedUp = NrOfDpsSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        conn.commit()
        conn.close()

      # Change from tank to healer
      elif OldRoleName == 'Tank' and NewRoleName == 'Healer' and NrOfHealersSignedUp < NrOfHealersRequired:
        c.execute(f"UPDATE Raids set NrOfTanksSignedUp = NrOfTanksSignedUp - 1, NrOfHealersSignedUp = NrOfHealersSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        conn.commit()
        conn.close()

      # Change from dps to tank
      elif OldRoleName == 'Dps' and NewRoleName == 'Tank' and NrOfTanksSignedUp < NrOfTanksRequired:
        c.execute(f"UPDATE Raids set NrOfDpsSignedUp = NrOfDpsSignedUp - 1, NrOfTanksSignedUp = NrOfTanksSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        conn.commit()
        conn.close()

      # Change from dps to healer
      elif OldRoleName == 'Dps' and NewRoleName == 'Healer' and NrOfHealersSignedUp < NrOfHealersRequired:
        c.execute(f"UPDATE Raids set NrOfDpsSignedUp = NrOfDpsSignedUp - 1, NrOfHealersSignedUp = NrOfHealersSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        conn.commit()
        conn.close()
        
      # Change from healer to tank
      elif OldRoleName == 'Healer' and NewRoleName == 'Tank' and NrOfTanksSignedUp < NrOfTanksRequired:
        c.execute(f"UPDATE Raids set NrOfHealersSignedUp = NrOfHealersSignedUp - 1, NrOfTanksSignedUp = NrOfTanksSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        conn.commit()
        conn.close()

      # Change from healer to dps
      elif OldRoleName == 'Healer' and NewRoleName == 'Dps' and NrOfDpsSignedUp < NrOfDpsRequired:
        c.execute(f"UPDATE Raids set NrOfHealersSignedUp = NrOfHealersSignedUp - 1, NrOfDpsSignedUp = NrOfDpsSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        conn.commit()
        conn.close()

      await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {NewRoleName} for {Name} on {DateTime}")
     
    except:
      await message.channel.send(f"Something went wrong changing your role")
      conn.close()
  else:
    await message.channel.send(f"You cannot change to the same role you already signed up as")
    conn.close()
  return