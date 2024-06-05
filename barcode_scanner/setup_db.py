import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create tables
c.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        barcode TEXT UNIQUE,
        name TEXT,
        price_usd REAL
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS rate (
        id INTEGER PRIMARY KEY,
        rate_usd_to_lbp REAL
    )
''')

# Insert default exchange rate
c.execute('INSERT INTO rate (rate_usd_to_lbp) VALUES (?)', (1500,))

conn.commit()
conn.close()
