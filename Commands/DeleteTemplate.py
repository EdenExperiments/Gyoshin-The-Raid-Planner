import sqlite3
from Helpers import OriginHelper

async def DeleteTemplate(message):
  commands = message.content.split()
  TemplateIndex = commands.index("!DeleteTemplate")

  try:
    TemplateName = commands[TemplateIndex + 1]
    Origin = await OriginHelper.GetOrigin(message)
    CreatorID = message.author.id
  except:
    await message.channel.send(f"Something went wrong assigning values, please make sure your template name doesn't contain spaces")
    return

  try:
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()

    c.execute(f"SELECT ID FROM Templates WHERE Name = (?) AND CreatorUserID = (?) AND Origin = (?)", (TemplateName, CreatorID, Origin,))
    row = c.fetchone()

    if not row:
      await message.channel.send(f"Template not found please beware that only the creator of the template is allowed to update the template")
      conn.close()
      return
  except:
        await message.channel.send(f"Something went wrong checking if this template already exists")
        conn.close()
        return

  try:
    TemplateID = row[0]
    c.execute(f"DELETE FROM Templates WHERE ID = (?)", (TemplateID,))
    conn.commit()
    conn.close()
    await message.channel.send(f"Template {TemplateName} deleted")
    return
  except:
    await message.channel.send(f"Something went wrong trying to delete the template")
    conn.close()
    return