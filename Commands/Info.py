import sqlite3
from Helpers import DateTimeFormatHelper
from Helpers import OriginHelper
from Helpers import RoleHelper
from Helpers import UserHelper
from Helpers import RoleIconHelper

async def GetRaidInfo(message, client):
  commands = message.content.split()

  # Get index values for commands
  try:
    InfoIndex = commands.index('!Info')
    DateIndex = commands.index('!DateTime')
  except:
    await message.channel.send(f"Required command !DateTime not found")
  
  # Assign values to variables
  try:
    Name = " ".join(commands[InfoIndex + 1:DateIndex])  
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
    await message.channel.send("Unable to convert date to sqlite format")

  # Get Origin
  Origin = await OriginHelper.GetOrigin(message)

  if not Origin:
    await message.channel.send("Something went wrong trying to obtain the server ID")

  # Get role icons
  try:
    TankIcon = await RoleIconHelper.GetTankIcon(client, 'Tank')
    DpsIcon = await RoleIconHelper.GetDpsIcon(client, 'Dps')
    HealerIcon = await RoleIconHelper.GetHealerIcon(client, 'Healer')
  except:
    await message.channel.send(f"Something went wrong retrieving role icons")

  # Open connection to DB
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()  

  # Execute query to retrieve raid
  try:
    c.execute(f"SELECT Name, OrganizerUserID, Status, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfhealersSignedUp, ID FROM Raids WHERE Date = (?) AND Origin = (?) AND Name = (?)", (sqlitedate, Origin, Name,))
  except:
    await message.channel.send(f"Something went wrong trying to retrieve the run")
    conn.close()

  rows = c.fetchall()

  if rows:
    for row in rows:
      # Data type conversions so variables can be used in message
      try:
        Name = row[0]
        OrganizerUserID = row[1]
        Status = row[2]
        NrOfTanksRequired = row[3]
        NrOfTanksSignedUp = row[4]
        NrOfDpsRequired = row[5]
        NrOfDpsSignedUp = row[6]
        NrOfHealersRequired = row[7]
        NrOfhealersSignedUp = row[8]
        RaidID = row[9]
        OrganizerName = await UserHelper.GetDisplayName(message, OrganizerUserID, client)

        if not OrganizerName:
          await message.channel.send(f"Something went wrong getting the display name of the organizer")
          conn.close()
      except:
        await message.channel.send(f"Unable to convert variables")
        conn.close()      

      # Post raid header info message to channel       
      await message.channel.send(f"**Organizer:** {OrganizerName}\n**Status:** {Status}\n{TankIcon} {NrOfTanksSignedUp}\/{NrOfTanksRequired} {DpsIcon} {NrOfDpsSignedUp}\/{NrOfDpsRequired} {HealerIcon} {NrOfhealersSignedUp}\/{NrOfHealersRequired}\n**Members:**\n")

      # Execute query to retrieve all raidmembers
      try:
        c.execute(f"SELECT UserID, RoleID FROM RaidMembers WHERE RaidID = (?) ORDER BY RoleID", (RaidID,))
      except:
        await message.channel.send(f"Something went wrong trying to retrieve members")
        conn.close()

      rows = c.fetchall()
      if rows:  
        for row in rows:
        # Data type conversions so variables can be used in message
          try:
            UserID = row[0]
            RoleID = row[1]
            RoleName = await RoleHelper.GetRoleName(RoleID)
            UserName = await UserHelper.GetDisplayName(message, UserID, client)

            if not RoleName:
              await message.channel.send(f"Something went wrong retrieving the role name for one of the members")
              conn.close()

            if not UserName:
              await message.channel.send(f"Something went wrong retrieving the display name for one of the members")
              conn.close()              

            if RoleName == 'Tank':
              RoleIcon = await RoleIconHelper.GetTankIcon(client, RoleName)          
            elif RoleName == 'Dps':
              RoleIcon = await RoleIconHelper.GetDpsIcon(client, RoleName)         
            elif RoleName == 'Healer':
              RoleIcon = await RoleIconHelper.GetHealerIcon(client, RoleName)

            # Post message to channel for each member
            await message.channel.send(f"{RoleIcon} - {UserName}\n")
          except:
            await message.channel.send(f"Unable to convert variables")
            conn.close()  
  else:
    if sqlitedate:
      await message.channel.send(f"Run not found")
      conn.close()
  
  # Close the connection
  conn.close()
  return