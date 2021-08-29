import sqlite3

async def MakeDatabase(message):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor() 

  try:
    CREATE_RAIDS_TABLE = """CREATE TABLE IF NOT EXISTS Raids (
      ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      Name TEXT NOT NULL,
      Origin INTEGER CHECK (Origin >= 0) NOT NULL,
      Date TEXT NOT NULL,
      OrganizerUserID INTEGER CHECK (OrganizerUserID >= 0) NOT NULL,
      NrOfPlayersRequired INTEGER CHECK (NrOfPlayersRequired >= 0) NOT NULL,
      NrOfPlayersSignedUp INTEGER CHECK (NrOfPlayersSignedUp >= 0) NOT NULL,
      NrOfTanksRequired INTEGER CHECK (NrOfTanksRequired >= 0) NOT NULL,
      NrOfTanksSignedUp INTEGER CHECK (NrOfTanksSignedUp >= 0) NOT NULL DEFAULT 0, 
      NrOfDpsRequired INTEGER CHECK (NrOfDpsRequired >= 0) NOT NULL,
      NrOfDpsSignedUp INTEGER CHECK (NrOfDpsSignedUp >= 0) NOT NULL DEFAULT 0,
      NrOfHealersRequired INTEGER CHECK (NrOfHealersRequired >= 0) NOT NULL,
      NrOfHealersSignedUp INTEGER CHECK (NrOfHealersSignedUp >= 0) NOT NULL DEFAULT 0,
      Status TEXT CHECK( Status IN ('Forming','Formed','Cancelled')) NOT NULL DEFAULT 'Forming',
      UNIQUE (Name, Origin, Date, OrganizerUserID)
    );"""

    c.execute(CREATE_RAIDS_TABLE)
    c.execute(f"CREATE INDEX idx_Raids ON Raids (Origin, Date, Name, Status, OrganizerUserID)")

    CREATE_ROLES_TABLE = """CREATE TABLE IF NOT EXISTS Roles (
      ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      Name TEXT NOT NULL,
      UNIQUE (Name)
    );"""

    c.execute(CREATE_ROLES_TABLE)
    c.execute(f"CREATE INDEX idx_Roles ON Roles (Name)")

    CREATE_RAIDMEMBERS_TABLE = """CREATE TABLE IF NOT EXISTS RaidMembers (
      ID INTEGER PRIMARY KEY AUTOINCREMENT,
      UserID INTEGER CHECK (UserID >= 0) NOT NULL,
      Origin INTEGER CHECK (Origin >= 0) NOT NULL,
      RaidID INTEGER NOT NULL,
      RoleID INTEGER NOT NULL,
      UNIQUE (UserID, Origin, RaidID),
      FOREIGN KEY(RoleID) REFERENCES Roles(ID),
      FOREIGN KEY(RaidID) REFERENCES Raids(ID) ON DELETE CASCADE
    );"""

    c.execute(CREATE_RAIDMEMBERS_TABLE)
    c.execute(f"CREATE INDEX idx_RaidMembers ON RaidMembers (Origin, RaidID, RoleID, UserID)")

    CREATE_TEMPLATES_TABLE = """CREATE TABLE IF NOT EXISTS Templates (
      ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      Name TEXT CHECK (Name NOT LIKE '% %') NOT NULL,
      Origin INTEGER CHECK (Origin >= 0) NOT NULL,
      CreatorUserID INTEGER CHECK (CreatorUserID >= 0),
      NrOfPlayers INTEGER CHECK (NrOfPlayers >= 0) NOT NULL,
      NrOfTanks INTEGER CHECK (NrOfTanks >= 0) NOT NULL,
      NrOfDps INTEGER CHECK (NrOfDps >= 0) NOT NULL,
      NrOfHealers INTEGER	CHECK (NrOfHealers >= 0) NOT NULL,
      UNIQUE (Name, Origin)
    );"""

    c.execute(CREATE_TEMPLATES_TABLE)
    c.execute(f"CREATE INDEX idx_TemplateName ON Templates (Origin, Name, CreatorUserID)")
    c.execute(f"CREATE INDEX idx_NrOfPlayers ON Templates (NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers)")

    conn.commit()
    conn.close()
    await message.channel.send(f"Database succesfully created")
  except:
    await message.channel.send(f"Something went wrong trying to create the database")
    conn.close()