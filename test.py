import sqlite3
import os

# Path to your database
DB_FILE = r"D:\Inventory\inventory.db"

def init_db():
    """Initialize the database and tables if they don't exist"""
    # Create folder if it doesn't exist
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

    # Connect to SQLite (will create file if not exists)
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Create inventory table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        status TEXT DEFAULT 'in_stock'
    )
    """)
    
    # Add status column if it doesn't exist (for existing databases)
    try:
        cur.execute("ALTER TABLE inventory ADD COLUMN status TEXT DEFAULT 'in_stock'")
        print("Added status column to existing inventory table")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    # Create purchase_list table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS purchase_list (
        id INTEGER,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL
    )
    """)

    # Insert sample inventory data (replace or add)
    sample_items = [
        (101, 'Item A', 5, 10.0, 'in_stock'),
        (102, 'Item B', 3, 15.0, 'in_stock'),
        (103, 'Item C', 2, 8.0, 'in_stock'),
        (104, 'Item D', 4, 15.0, 'in_stock'),
        (105, 'Item E', 6, 15.0, 'in_stock'),
        (106, 'Item F', 1, 15.0, 'in_stock'),
    ]

    # Update existing items with status and insert new ones
    for item in sample_items:
        cur.execute("""
        INSERT OR REPLACE INTO inventory (id, name, quantity, price, status)
        VALUES (?, ?, ?, ?, ?)
        """, item)
    
    # Update any existing records without status
    cur.execute("UPDATE inventory SET status = 'in_stock' WHERE status IS NULL")
    cur.execute("UPDATE inventory SET status = 'out_of_stock' WHERE quantity <= 0")

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_FILE}!")

if __name__ == "__main__":
    init_db()
