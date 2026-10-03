import sqlite3

connection = sqlite3.connect("smart_campus.db")
cursor = connection.cursor()

# Create complaints table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT UNIQUE,
        student_name TEXT,
        department TEXT,
        problem_type TEXT,
        location TEXT,
        complaint_text TEXT,
        priority TEXT,
        status TEXT
    )
""")

connection.commit()
connection.close()

print("Database and complaints table are ready.")
