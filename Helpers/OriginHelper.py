#Helper function to retrieve discord server ID
async def GetOrigin(message):
  if not message:
    # Throw error when no message input is received
    messagestring = 'No message input found'
    message.channel.send(messagestring)
    return
  else:
    origin = message.guild.id  
    return origin