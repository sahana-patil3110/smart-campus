import sqlite3

connection = sqlite3.connect("smart_campus.db")
cursor = connection.cursor()

# Add new columns if they don't already exist
columns_to_add = [
    ("department", "TEXT"),
    ("problem_type", "TEXT"),
    ("location", "TEXT"),
    ("priority", "TEXT")
]

for column_name, column_type in columns_to_add:
    try:
        cursor.execute(
            f"ALTER TABLE complaints ADD COLUMN {column_name} {column_type}"
        )
        print(f"Added column: {column_name}")
    except sqlite3.OperationalError:
        print(f"Column already exists: {column_name}")

connection.commit()

# Show the current table structure
cursor.execute("PRAGMA table_info(complaints)")
columns = cursor.fetchall()

print("\nCurrent complaints table columns:")

for column in columns:
    print(column)

connection.close()
