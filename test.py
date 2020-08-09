
user_id = '1'
user_name = 'Tom Smit'

dbase = sqlite3.connect('new.db')
dbase.execute(''' CREATE TABLE IF NOT EXISTS records(
ID INT PRIMARY KEY NOT NULL,
NAME TEXT,
BANK INT) ''')
dbase.commit()

dbase.execute('''INSERT OR IGNORE INTO records (ID, NAME, BANK) VALUES(?,?,?)''',(user_id, user_name, '100'))
d = dbase.execute(''' SELECT TOP 1 BANK FROM records WHERE ID = ?''', (user_id,))
print(d)
dbase.close()
