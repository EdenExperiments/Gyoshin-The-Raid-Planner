# Helper function to tag a list of users
async def NotifyRaidMembers(message, raidmembers):
  # Strip leading spaces in received list
  Message = ''

  for member in raidmembers:
    RaidMember = f"<@!{member}> "
    Message += RaidMember
  await message.channel.send(f"{Message}")
  return

# Helper function to tag a single user
async def NotifyUser(message, userid):
  await message.channel.send(f"<@!{userid}>")
  return