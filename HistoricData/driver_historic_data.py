from EOD import get_all_eod_data

def main():
    print("Historic Data Fetcher")
    print("-" * 30)
    
    start_date = "2023-01-01"
    end_date = "2023-12-31"

    # start_date = input("Enter start date (YYYY-MM-DD): ")
    # end_date = input("Enter end date (YYYY-MM-DD): ")
    
    print(f"\nFetching EOD data from {start_date} to {end_date}...")
    
    try:
        eod_data = get_all_eod_data(start_date, end_date)
        print(f"\nCompleted! Retrieved EOD data for {len(eod_data)} symbols")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()