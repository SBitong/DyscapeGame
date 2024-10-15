import sqlite3
import json
import os

# Define the path to the database file
db_path = os.path.join('data', 'game_progress.db')

# Ensure the directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)


# Create a new database connection
def connect():
    return sqlite3.connect(db_path)


# Initialize the database
def create_tables():
    with connect() as conn:
        cursor = conn.cursor()
        # Create the table for saving first-level progress
        cursor.execute('''CREATE TABLE IF NOT EXISTS first_level_progress (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            profile_id INTEGER,
                            lives INTEGER,
                            draggable_images TEXT,
                            ladder_slots TEXT,
                            FOREIGN KEY(profile_id) REFERENCES profiles(id)
                          )''')

        # Create the table for profiles
        cursor.execute('''CREATE TABLE IF NOT EXISTS profiles (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE
                          )''')
        conn.commit()


# Save progress function (for the first level)
def save_progress(profile_id, level, lives, draggable_images, ladder_slots):
    draggable_images_json = json.dumps(draggable_images)  # Convert to JSON string
    ladder_slots_json = json.dumps(ladder_slots)  # Convert to JSON string

    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO first_level_progress (profile_id, lives, draggable_images, ladder_slots)
                          VALUES (?, ?, ?, ?)''', (profile_id, lives, draggable_images_json, ladder_slots_json))
        conn.commit()


# Load the most recent progress for the first level
def load_progress(profile_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT lives, draggable_images, ladder_slots
                          FROM first_level_progress
                          WHERE profile_id = ?
                          ORDER BY id DESC LIMIT 1''', (profile_id,))
        progress = cursor.fetchone()
        if progress:
            return {
                'lives': progress[0],
                'draggable_images': json.loads(progress[1]),
                'ladder_slots': json.loads(progress[2])
            }
        return None


# Create a new profile
def create_profile(name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO profiles (name) VALUES (?)', (name,))
        conn.commit()


# Load all profiles
def load_profiles():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM profiles')
        return cursor.fetchall()


# Reset progress for a profile
def reset_progress(profile_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM first_level_progress WHERE profile_id = ?', (profile_id,))
        conn.commit()
