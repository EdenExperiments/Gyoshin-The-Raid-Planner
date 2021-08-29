import sqlite3

async def InsertMasterData(message):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    c.execute("INSERT INTO Roles VALUES (1, 'Tank')")
    c.execute("INSERT INTO Roles VALUES (2, 'Dps')")
    c.execute("INSERT INTO Roles VALUES (3, 'Healer')")

    conn.commit()
    conn.close()
    await message.channel.send(f"Masterdata succesfully added")
  except:
    await message.channel.send("Something went wrong trying to insert masterdata")
    conn.close()