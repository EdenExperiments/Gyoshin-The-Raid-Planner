from Helpers import OriginHelper

# Helper function to get discord user name of the poster
async def GetDisplayName(message, userid, client):

  # Get server ID
  Origin = await OriginHelper.GetOrigin(message)
  guild = client.get_guild(Origin)

  if not Origin:
    message.channel.send(f"Something went wrong retrieving the server ID")
  
  # Get member object by discord user id
  member_obj = await guild.fetch_member(userid) 
  display_name = member_obj.display_name

  if not display_name:
    message.channel.send(f"Something went wrong retrieving the users' display name")
  return display_name 

async def GetUserID(message):
  userid = message.author.id

  if not userid:
    await message.channel.send(f"Something went wrong retrieving the user id")
  return userid