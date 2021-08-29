import sqlite3

async def ListRoles(message):

# Open connection to the database
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()  
    
  # Execute query
  try:
    c.execute(f"SELECT Name FROM Roles ORDER BY Name ASC")
  except:
    await message.channel.send(f"Something went wrong trying to retrieve roles")
    conn.close()

  # Store query results
  rows = c.fetchall()

  if not rows:
    await message.channel.send("No roles found")
    conn.close()
    
  # Send message header to channel command was called from
  AvailableRolesMessage = "The following roles are available: \n"
  await message.channel.send(AvailableRolesMessage)

  # Go through all rows found and post a message in channel for each one
  for row in rows:

    # Data type conversion so values can be used in message
    try:        
      Name = row[0]
      RolesMessage = (f"{Name}")

      # Post message to channel
      await message.channel.send(RolesMessage)
      conn.close()
    except:
      await message.channel.send(f"Unable to assign variables")
      conn.close()

  # Close the connection to the database
  conn.close()