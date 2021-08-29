import sqlite3
from Helpers import OriginHelper

async def AddTemplate(message):
  commands = message.content.split()

  try:
    TemplateIndex = commands.index("!AddTemplate")
    NrOfPlayersIndex = commands.index("!NrOfPlayers")
    NrOfTanksIndex = commands.index("!NrOfTanks")
    NrOfDpsIndex = commands.index("!NrOfDps")
    NrOfHealersIndex = commands.index("!NrOfHealers")
  except ValueError:
    await message.channel.send(f"!NrOfPlayers, !NrOfTanks,!NrOfDps or !NrOfHealers not defined in command.")
    return

  try:
    TemplateName = commands[TemplateIndex + 1]
    Origin = await OriginHelper.GetOrigin(message)
    CreatorID = message.author.id
    NrOfPlayers = int(commands[NrOfPlayersIndex + 1])
    NrOfTanks = int(commands[NrOfTanksIndex + 1])
    NrOfDps = int(commands[NrOfDpsIndex + 1])
    NrOfHealers = int(commands[NrOfHealersIndex + 1])
  except:
    await message.channel.send(f"Something went wrong assigning values, please make sure your template name doesn't contain spaces")
    return

  try:
    if NrOfTanks + NrOfDps + NrOfHealers == NrOfPlayers:
      conn = sqlite3.connect('RaidPlanner.db')
      c = conn.cursor()

      try:
        c.execute(f"SELECT ID FROM Templates WHERE Name = (?) AND CreatorUserID = (?) AND Origin = (?)", (TemplateName, CreatorID, Origin,))
        row = c.fetchone()

        if row:
          await message.channel.send(f"Template already exists")
          conn.close()
          return
      except:
        await message.channel.send(f"Something went wrong checking if this template already exists")
        conn.close()
        return

      try:
        c.execute(f"INSERT INTO Templates (Name, Origin, CreatorUserID, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers) VALUES (?, ?, ?, ?, ?, ?, ?)", (TemplateName, Origin, CreatorID, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers))
        conn.commit()
        conn.close()
        await message.channel.send(f"Template {TemplateName} added")
      except:
        await message.channel.send(f"Something went wrong trying to add template")
        conn.close()
        return

  except:
    await message.channel.send(f"The total of tanks, dps and healers provided required doesn't match the provided total for the number of players")
    return