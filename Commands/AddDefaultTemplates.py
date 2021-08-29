import sqlite3
from Helpers import OriginHelper

async def AddDefaultTemplates(message):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    Origin = await OriginHelper.GetOrigin(message)
    CreatorID = message.author.id
    c.execute(f"INSERT INTO Templates (Name, Origin, CreatorUserID, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers) VALUES ('AllianceRaid', {Origin}, {CreatorID}, 24, 3, 15, 6)")

    c.execute(f"INSERT INTO Templates (Name, Origin, CreatorUserID, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers) VALUES ('Raid', {Origin}, {CreatorID}, 8, 2, 4, 2)")

    c.execute(f"INSERT INTO Templates (Name, Origin, CreatorUserID, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers) VALUES ('Dungeon', {Origin}, {CreatorID}, 4, 1, 2, 1)")

    c.execute(f"INSERT INTO Templates (Name, Origin, CreatorUserID, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers) VALUES ('TreasureMaps', {Origin}, {CreatorID}, 8, 1, 6, 1)")

    conn.commit()
    conn.close()
    await message.channel.send(f"Default templates added")
  except:
    await message.channel.send("Something went wrong trying to insert default templates")
    conn.close()