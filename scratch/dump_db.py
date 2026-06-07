import sqlite3
import json

conn = sqlite3.connect("data/gill_vedio.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- LAST 10 IDEAS ---")
cursor.execute("SELECT * FROM ideas ORDER BY id DESC LIMIT 10")
for row in cursor.fetchall():
    print(dict(row))

print("\n--- LAST 10 VIDEOS ---")
cursor.execute("SELECT * FROM videos ORDER BY id DESC LIMIT 10")
for row in cursor.fetchall():
    print(dict(row))

conn.close()
