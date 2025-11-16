import sqlite3
import sys
import os

# Add parent directory to path
parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_path)

def get_db_path():
    return os.path.join(parent_path, 'trading_data.db')

def add_ema_columns(periods=[50, 100, 200]):
    """Add EMA columns to all existing EOD tables"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all EOD tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_EOD';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"Adding EMA columns to {table_name}")
            
            for period in periods:
                try:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN ema_{period} DECIMAL(10,2);")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"  Column ema_{period} already exists in {table_name}")
                    else:
                        raise e
        
        conn.commit()
        print("EMA columns added successfully")
        
    except Exception as e:
        print(f"Error adding EMA columns: {e}")
    finally:
        conn.close()

def get_symbols_from_db():
    """Get all symbols from database"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT symbol FROM Symbols ORDER BY id;")
        symbols = [row[0] for row in cursor.fetchall()]
        return symbols
    except Exception as e:
        print(f"Error fetching symbols: {e}")
        return []
    finally:
        conn.close()

def calculate_ema_for_symbol(symbol, periods=[50, 100, 200]):
    """Calculate EMAs for a single symbol"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        table_name = f"{symbol.replace(':', '_').replace('-', '_')}_EOD"
        
        # Fetch EOD data ordered by date
        cursor.execute(f"""
            SELECT id, close_price, time 
            FROM {table_name} 
            WHERE close_price > 0 
            ORDER BY time ASC
        """)
        
        rows = cursor.fetchall()
        if not rows:
            print(f"No valid data found for {symbol}")
            return
        
        print(f"Calculating EMAs for {symbol} ({len(rows)} records)")
        
        # Initialize EMA tracking
        ema_values = {period: None for period in periods}
        multipliers = {period: 2 / (period + 1) for period in periods}
        
        # Process each row
        for i, (row_id, close_price, date) in enumerate(rows):
            day_number = i + 1
            
            # Calculate EMAs for each period
            update_values = {}
            
            for period in periods:
                if day_number >= period:
                    if day_number == period:
                        # First EMA value = SMA of first 'period' days
                        sma_sum = sum(float(rows[j][1]) for j in range(period))
                        ema_values[period] = sma_sum / period
                    else:
                        # EMA formula for subsequent days
                        ema_values[period] = (float(close_price) * multipliers[period]) + (ema_values[period] * (1 - multipliers[period]))
                    
                    update_values[f"ema_{period}"] = round(ema_values[period], 2)
            
            # Update database if we have EMA values to update
            if update_values:
                set_clause = ", ".join([f"{col} = ?" for col in update_values.keys()])
                values = list(update_values.values()) + [row_id]
                
                cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE id = ?", values)
        
        conn.commit()
        print(f"EMAs calculated and stored for {symbol}")
        
    except Exception as e:
        print(f"Error calculating EMAs for {symbol}: {e}")
    finally:
        conn.close()

def calculate_all_emas(periods=[50, 100, 200]):
    """Calculate EMAs for all symbols"""
    print("Starting EMA calculation for all symbols...")
    
    # Add EMA columns first
    add_ema_columns(periods)
    
    # Get symbols from database
    symbols = get_symbols_from_db()
    
    if not symbols:
        print("No symbols found in database")
        return
    
    print(f"Found {len(symbols)} symbols to process")
    
    # Calculate EMAs for each symbol
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Processing {symbol}")
        calculate_ema_for_symbol(symbol, periods)
    
    print(f"\nEMA calculation completed for all {len(symbols)} symbols")

if __name__ == "__main__":
    calculate_all_emas()