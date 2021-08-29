import sqlite3
import re
from datetime import datetime
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import RoleIconHelper

async def ListRaidsOnDate(message, client):

  # Open connection to DB
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Get Origin
  Origin = await OriginHelper.GetOrigin(message)

  if not Origin:
    await message.channel.send("Something went wrong trying to obtain the server ID")
    conn.close()

  # split message input
  splitmessage = str.split(message.content, ' ')
  date = splitmessage[1]

  # Check if date provided matches dd-mm-yyyy format
  pattern = re.compile(r'(\d{2})-(\d{2})-(\d{4})')
  match = pattern.match(date)

  # Convert to sqlite date format
  if match:
    splitdate = str.split(date, '-')
    day = splitdate[0]
    month = splitdate[1]
    year = splitdate[2]
    sqlitedate = f"{year}-{month}-{day}"

    # Check if date is not in the past
    try:
      # Get current date
      current_date = datetime.today().strftime('%Y-%m-%d')
      current_date = datetime.today().strptime(current_date, '%Y-%m-%d')

      if (date < sqlitedate):    
        await message.channel.send("Date cannot be in the past")
        conn.close()
    except:
      await message.channel.send("Unable to convert date from local to sqlite format")
      conn.close()

    try:
      TankIcon = await RoleIconHelper.GetTankIcon(client, 'Tank')
      DpsIcon = await RoleIconHelper.GetDpsIcon(client, 'Dps')
      HealerIcon = await RoleIconHelper.GetHealerIcon(client, 'Healer')
    except:
      await message.channel.send(f"Something went wrong retrieving role icons")

    # Execute query
    try:
      c.execute(f"SELECT Name, OrganizerUserID, Status, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfhealersSignedUp, Date FROM Raids WHERE Date like (?) AND Origin = (?) AND Status != 'Cancelled' ORDER BY Date ASC, ID ASC", (sqlitedate+'%', Origin,))
    except:
      await message.channel.send(f"Run not found")
      conn.close()

    rows = c.fetchall()

    if rows:
      # Header message
      await message.channel.send(f"The following runs are planned on {date}:\n")

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
          Date = row[9]
          SplitDate = str.split(Date, ' ')
          Time = SplitDate[1]

          try:
            OrganizerName = await UserHelper.GetDisplayName(message, OrganizerUserID, client)
          except:
            await message.channel.send(f"Something went wrong getting the display name of the organizer")
            conn.close()
            
        except:
          await message.channel.send(f"Unable to convert variables")
          conn.close()       

        # Post message to channel       
        await message.channel.send(f"**Name:** {Name}\n**Organizer:** {OrganizerName}\n**Time:** {Time}\n**Status:** {Status}\n{TankIcon} {NrOfTanksSignedUp}\/{NrOfTanksRequired} {DpsIcon} {NrOfDpsSignedUp}\/{NrOfDpsRequired} {HealerIcon} {NrOfhealersSignedUp}\/{NrOfHealersRequired}\n---------------------------------------------------")
    
    else:
       await message.channel.send(f"No runs found on this date")
       conn.close()

  else:
    await message.channel.send(f"Invalid date, please provide the date in the dd-mm-yyyy format")
    conn.close()
  
  # Close the connection
  conn.close()  
  return