import sqlite3
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
        # Create the table for saving first-level progress if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS first_level_progress (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            lives INTEGER,
                            draggable_images TEXT, -- Store as JSON or comma-separated values
                            ladder_slots TEXT      -- Store as JSON or comma-separated values
                          )''')
        conn.commit()


# Save the player's progress into the database
def save_progress(level, lives, current_time, rounds_completed):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO progress (level, lives, current_time, rounds_completed)
                          VALUES (?, ?, ?, ?)''', (level, lives, current_time, rounds_completed))
        conn.commit()

# Load the most recent progress from the database
def load_progress():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT level, lives, current_time, rounds_completed
                          FROM progress ORDER BY id DESC LIMIT 1''')
        progress = cursor.fetchone()
        return progress if progress else None

# Delete all saved progress (useful when starting a new game)
def reset_progress():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM progress')
        conn.commit()

# Example Usage:
if __name__ == "__main__":
    create_tables()

    # Save some example progress
