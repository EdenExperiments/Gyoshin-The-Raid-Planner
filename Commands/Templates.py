import sqlite3
from Helpers import OriginHelper
from Helpers import RoleIconHelper

async def GetTemplates(message, client):

  # Open connection to the database
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Get role icons
  try:
    TankIcon = await RoleIconHelper.GetTankIcon(client, 'Tank')
    DpsIcon = await RoleIconHelper.GetDpsIcon(client, 'Dps')
    HealerIcon = await RoleIconHelper.GetHealerIcon(client, 'Healer')
  except:
    await message.channel.send(f"Something went wrong retrieving role icons")
  
  
  # Execute query
  try:
    Origin = await OriginHelper.GetOrigin(message)
    c.execute(f"SELECT Name, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers FROM Templates WHERE Origin = (?)", (Origin,))
  except:
    await message.channel.send(f"Something went wrong trying to retrieve templates")
    conn.close()    

  # Store query results
  rows = c.fetchall()    

  if not rows:
    await message.channel.send(f"No templates found")
    conn.close()
    
  # Send message header to channel command was called from
  AvailableTemplatesMessage = "The following templates are available: \n"
  await message.channel.send(AvailableTemplatesMessage)

  # Go through all rows found and post a message in channel for each one
  for row in rows:

    try:        
      Name = row[0]
      NrOfPlayers = row[1]
      NrOfTanks = row[2]
      NrOfDps = row[3]
      NrOfHealers = row[4]
    except:
      await message.channel.send(f"Unable to convert variables")
      conn.close()

    # Post message to channel
    await message.channel.send(f"Name: {Name}\nNumber of players: {NrOfPlayers}\n{TankIcon} {NrOfTanks} {DpsIcon} {NrOfDps} {HealerIcon} {NrOfHealers}")
    conn.close()

  # Close the connection to the database
  conn.close()
  return