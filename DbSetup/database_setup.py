import sqlite3
import os
import sys

parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(f"Adding to sys.path: {parent_path}")
sys.path.append(parent_path)

def create_database():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'trading_data.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Symbols table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Symbols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol VARCHAR(50) NOT NULL UNIQUE,
            exchange_type VARCHAR(10) NOT NULL,
            symbol_abbreviation VARCHAR(20) NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database created at: {db_path}")
    return db_path

def insert_symbols():
    from symbols import SYMBOLS
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'trading_data.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for symbol in SYMBOLS:
        # Parse symbol format: NSE:RELIANCE-EQ or BSE:SYMBOL-EQ
        parts = symbol.split(':')
        exchange = parts[0]  # NSE or BSE
        symbol_part = parts[1].replace('-EQ', '')  # Remove -EQ suffix
        
        cursor.execute('''
            INSERT OR IGNORE INTO Symbols (symbol, exchange_type, symbol_abbreviation)
            VALUES (?, ?, ?)
        ''', (symbol, exchange, symbol_part))
    
    conn.commit()
    conn.close()
    print(f"Inserted {len(SYMBOLS)} symbols into database")

if __name__ == "__main__":
    create_database()
    insert_symbols()