#!/usr/bin/env python
import sqlite3
import os

# Connect to the database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

try:
    # Delete admin migration records
    cursor.execute("DELETE FROM django_migrations WHERE app='admin'")
    print("Deleted admin migration records")
    
    # Check what migrations are left
    cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
    migrations = cursor.fetchall()
    print("Remaining migrations:")
    for app, name in migrations:
        print(f"  {app}: {name}")
    
    conn.commit()
    print("Changes committed successfully")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
    
finally:
    conn.close()
