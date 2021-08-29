import sqlite3
from Helpers import DateTimeFormatHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import RoleHelper

async def DismissMember(message, client):

  commands = message.content.split()

  # Get Index values for commands
  try:
    DateIndex = commands.index("!DateTime")
    UserIndex = commands.index("!User")
    Date = commands[DateIndex + 1]
    Time = commands[DateIndex +2]
    DateTime = Date +" "+ Time
    UserID = message.mentions[0].id
  except ValueError:
    await message.channel.send(f"!DateTime or !User not defined or you tried to dismiss multiple members at once.")
    return

  # Sent datetime to function to format for SQLite and validation
  try:
    sqlitedate = await DateTimeFormatHelper.LocalToSqlite(message, DateTime)
  except:
    await message.channel.send(f"Something went wrong converting the date values")
    return
  
   # Generate raidname
  MinIndexOfCommands = min(DateIndex, UserIndex)

  try:
    RaidName = " ".join(commands[1:MinIndexOfCommands])
  except:
    await message.channel.send(f"Error collecting name of the run")
    return

  # Get Discord server id
  Origin = await OriginHelper.GetOrigin(message)

  if not Origin:
    await message.channel.send(f"An error occurred trying to resolve the server ID")
    return

  # Get user ID of the person who entered the commands
  Creator = message.author.id
  CreatorDisplayName = await UserHelper.GetDisplayName(message, Creator, client)

  if not Creator:
    await message.channel.send(f"Something went wrong retrieving the user ID")
    return

  # Get server display name of user
  UserName = await UserHelper.GetDisplayName(message, UserID, client)

  if not UserName:
    await message.channel.send(f"Something went wrong resolving the users' display name")
    return

  # Search if raid exists and user who entered the commands is the organizer
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    c.execute(f"SELECT ID FROM Raids WHERE Name = (?) AND Origin = (?) AND OrganizerUserID = (?) AND Date = (?)", (RaidName, Origin, Creator, sqlitedate))
    row = c.fetchone()
    RaidID = row[0]
  except:
    await message.channel.send(f"Run not found or you are not the organizer of this run")
    conn.close()
    return

  if RaidID:
    # Check if the user is part of this run and the creator is not trying to remove themself
    try:
      c.execute(f"SELECT ID, RoleID FROM RaidMembers WHERE RaidID = (?) AND Origin = (?) AND UserID = (?) AND UserID != (?)", (RaidID, Origin, UserID, Creator,))
      row = c.fetchone()

      RaidMemberID = row[0]
      RoleID = row[1]
      RoleName = await RoleHelper.GetRoleName(RoleID)
    except:
      await message.channel.send(f"Something went wrong checking if the provided member is part of this run or you're the organizer of this run trying to dismiss yourself'")
      conn.close()
      return

    if RaidMemberID:
      try:        
        c.execute(f"DELETE FROM RaidMembers WHERE ID = (?) AND Origin = (?)", (RaidMemberID, Origin,))
        conn.commit()
      except:
        await message.channel.send(f"Something went wrong removing this member from the run")
        conn.close()
        return

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
        
  try:
    conn.commit()
    await message.channel.send(f"{CreatorDisplayName} has dismissed {UserName} from the run {RaidName} on {Date}")
  except:
    await message.channel.send(f"Something went wrong updating the members")
    conn.close()
    return