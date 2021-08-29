# Helper function to post messages
async def PostMessage(message, messagestring):
 # Throw error when no messagestring input is received
 if not messagestring:
   messagestring = 'No messagestring input found'
 # Throw error when no message input is received
 elif not message:
   message = 'No message input found'
 await message.channel.send(messagestring)
 return