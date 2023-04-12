import requests
import time
import pandas as pd
from datetime import datetime, timedelta

base_url = "https://api.cryptowat.ch"
pair = "maticusdt"  # MATIC-USDT trading pair
exchange = "binance"  # Fetch data from Binance exchange

# Get historical OHLC data
def get_historical_data():
    interval_days = 30  # Fetch data for 30-day intervals
    candle_duration = 300  # 5-minute intervals (in seconds)
    now = datetime.now()
    start_date = datetime(2019, 4, 26)

    all_data = []

    while start_date < now:
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int((start_date + timedelta(days=interval_days)).timestamp())
        url = f"{base_url}/markets/{exchange}/{pair}/ohlc?after={start_timestamp}&before={end_timestamp}&periods={candle_duration}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'result' in data and f'{candle_duration}' in data['result']:
                all_data.extend(data['result'][f'{candle_duration}'])
            else:
                print("Error: Unable to find historical data in the API response")
                return None
        else:
            print(f"Error: Cryptowatch API returned status code {response.status_code}")
            return None

        start_date += timedelta(days=interval_days)
        time.sleep(5)  # Add a delay to avoid hitting rate limits

    return all_data

def main():
    historical_data = get_historical_data()
    if historical_data is None:
        print("Error: Unable to fetch historical data")
        return

    # Convert the historical data to a DataFrame
    data_frame = pd.DataFrame(historical_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Trades'])
    data_frame['Timestamp'] = pd.to_datetime(data_frame['Timestamp'], unit='s')

    # Save data to CSV
    data_frame.to_csv('MATIC_price_data.csv', index=False)
    print("MATIC_price_data.csv has been saved to the current directory.")

if __name__ == '__main__':
    main()
