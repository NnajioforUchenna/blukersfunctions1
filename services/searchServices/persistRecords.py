import sqlite3

DB_FILENAME = 'hash_records.db'


# Initialize the SQLite database and create the table if it doesn't exist.
def initialize_db():
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS hash_records (hash_value TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()


# Check if a record with the given hash value has already been written.
def is_record_written(hash_value):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM hash_records WHERE hash_value=?", (hash_value,))
    result = cursor.fetchone()
    conn.close()
    return True if result else False


# Write the hash value of a record to the database.
def write_record(hash_value):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO hash_records (hash_value) VALUES (?)", (hash_value,))
        conn.commit()
    except sqlite3.IntegrityError:  # Hash value already exists
        pass
    conn.close()

def clear_all_records():
    """Delete all hash values from the database."""
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM hash_records")
    conn.commit()
    conn.close()


initialize_db()
