import sqlite3
from datetime import datetime
from datetime import timedelta

# Helper function to automatically delete old raid data in order to keep database size limited
async def DeleteOldRaidData():

  # Open connection to the database
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Get current date and time
  try:
    current_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    current_date = datetime.utcnow().strptime(current_date, "%Y-%m-%d %H:%M")
    yesterday = current_date - timedelta(days=1)
    yesterday = datetime.strftime(yesterday, "%Y-%m-%d %H:%M")
  except:
    return
    
  # Store query results
  try:
    c.execute(f"SELECT ID FROM Raids WHERE Date <= (?)", (yesterday,))
  except:
    return

  rows = c.fetchall()

  # Check if there are results
  if not rows:
      return
  else:
    for row in rows:      
      try: 
        ID = row[0]
        c.execute(f"DELETE FROM RaidMembers WHERE RaidID = (?)", (ID,))
        conn.commit()
      except:
        conn.close()
        return
      try:
        c.execute(f"DELETE FROM Raids WHERE ID = (?)", (ID,))
        conn.commit()
      except:
        conn.close()
        return
  conn.close()
  return