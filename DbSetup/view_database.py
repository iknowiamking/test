import sqlite3
import os

def view_database():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'trading_data.db')
    
    if not os.path.exists(db_path):
        print("Database not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Database: {db_path}")
    print(f"Tables found: {len(tables)}")
    print("-" * 50)
    
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        
        # Get table structure
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        # Get first 5 rows
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        rows = cursor.fetchall()
        
        if rows:
            # Print in SQL table format
            headers = [col[1] for col in columns]
            
            # Calculate column widths
            widths = [len(str(header)) for header in headers]
            for row in rows:
                for i, value in enumerate(row):
                    widths[i] = max(widths[i], len(str(value)))
            
            # Print header
            header_line = "| " + " | ".join(f"{header:<{widths[i]}}" for i, header in enumerate(headers)) + " |"
            separator = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
            
            print(separator)
            print(header_line)
            print(separator)
            
            # Print rows
            for row in rows:
                row_line = "| " + " | ".join(f"{str(value):<{widths[i]}}" for i, value in enumerate(row)) + " |"
                print(row_line)
            print(separator)
        else:
            print("No data found")
        
        print("-" * 50)
    
    conn.close()

if __name__ == "__main__":
    view_database()