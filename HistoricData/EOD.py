import requests
import json
import sys
import os

parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(f"Adding to sys.path: {parent_path}")
sys.path.append(parent_path)

from CurrentSession import SESSION_TOKEN
from symbols import SYMBOLS
from epoch_converter import date_to_epoch
import sqlite3

def get_eod_data(symbol, from_date, to_date):
    url = "https://go.mynt.in/NorenWClientTP/EODChartData"
    
    from_epoch = date_to_epoch(from_date)
    to_epoch = date_to_epoch(to_date)
    
    data = {
        "sym": symbol,
        "from": str(from_epoch),
        "to": str(to_epoch)
    }
    
    payload = f"jData={json.dumps(data)}&jKey={SESSION_TOKEN}"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(url, headers=headers, data=payload)
    result = response.json()
    if isinstance(result, dict) and result.get('stat') == 'Not_Ok':
        print(f"API Error for {symbol}: {result.get('emsg', 'Unknown error')}")
    return result

def create_eod_tables():
    db_path = os.path.join(parent_path, 'trading_data.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for symbol in SYMBOLS:
        table_name = f"{symbol.replace(':', '_').replace('-', '_')}_EOD"
        
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id INTEGER,
                time VARCHAR(20),
                open_price DECIMAL(10,2),
                high_price DECIMAL(10,2),
                low_price DECIMAL(10,2),
                close_price DECIMAL(10,2),
                ssboe VARCHAR(20),
                volume DECIMAL(15,2),
                FOREIGN KEY (symbol_id) REFERENCES Symbols(id)
            )
        ''')
    
    conn.commit()
    conn.close()
    print("EOD tables created successfully")

def get_symbol_id(symbol):
    db_path = os.path.join(parent_path, 'trading_data.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM Symbols WHERE symbol = ?", (symbol,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def store_eod_data(symbol, eod_data):
    if not isinstance(eod_data, list):
        return
    
    db_path = os.path.join(parent_path, 'trading_data.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    symbol_id = get_symbol_id(symbol)
    if not symbol_id:
        print(f"Symbol {symbol} not found in database")
        conn.close()
        return
    
    table_name = f"{symbol.replace(':', '_').replace('-', '_')}_EOD"
    
    for record in eod_data:
        # Handle case where record might be a string (parse as JSON)
        if isinstance(record, str):
            record = json.loads(record)
        
        cursor.execute(f'''
            INSERT OR IGNORE INTO {table_name} 
            (symbol_id, time, open_price, high_price, low_price, close_price, ssboe, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol_id,
            record.get('time'),
            float(record.get('into', 0)),
            float(record.get('inth', 0)),
            float(record.get('intl', 0)),
            float(record.get('intc', 0)),
            record.get('ssboe'),
            float(record.get('intv', 0))
        ))
    
    conn.commit()
    conn.close()
    print(f"Stored {len(eod_data)} records for {symbol}")

def get_all_eod_data(from_date, to_date, store_in_db=True):
    if store_in_db:
        create_eod_tables()
    
    all_data = {}
    for symbol in SYMBOLS:
        try:
            data = get_eod_data(symbol, from_date, to_date)
            all_data[symbol] = data
            
            if isinstance(data, dict) and data.get('stat') == 'Not_Ok':
                print(f"ERROR for {symbol}: {data.get('emsg', 'Unknown error')}")
            elif isinstance(data, list) and store_in_db:
                store_eod_data(symbol, data)
                print(f"Retrieved and stored data for {symbol}")
            else:
                print(f"Retrieved data for {symbol}")
        except Exception as e:
            print(f"Error retrieving data for {symbol}: {e}")
    
    return all_data

if __name__ == "__main__":
    # Example usage
    from_date = "2023-01-01"
    to_date = "2023-12-31"
    
    eod_data = get_all_eod_data(from_date, to_date)
    print(f"Retrieved EOD data for {len(eod_data)} symbols")
    # Print first symbol's data to see structure
    if eod_data:
        first_symbol = list(eod_data.keys())[0]
        print(f"Sample data structure for {first_symbol}:")
        print(type(eod_data[first_symbol]))
        if isinstance(eod_data[first_symbol], list) and len(eod_data[first_symbol]) > 0:
            print(f"First item: {eod_data[first_symbol][0]}")
        else:
            print(eod_data[first_symbol])