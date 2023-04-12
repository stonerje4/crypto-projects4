import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from tkinter import Tk, Label, Entry, Button, Text, Scrollbar, END, Frame, Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import json
import time



API_KEY_FILE = 'api_key.json'

def save_api_key(api_key):
    with open(API_KEY_FILE, 'w') as f:
        json.dump({'api_key': api_key}, f)

def load_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r') as f:
            data = json.load(f)
            return data['api_key']
    return None

def get_holders_data(api_key, token_address):
    url_base = f'https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={token_address}&startblock=0&endblock=999999999&sort=asc&apikey={api_key}'
    page = 1
    offset = 10000   # fetch 10000 records per API call
    max_records = 200 # limit the number of records returned per API call
    all_results = []
    
    # Get the current date
    today = datetime.today().date()

    while True:
        url = f'{url_base}&page={page}&offset={offset}&max={max_records}'
        response = requests.get(url)
        data = response.json()
        result = data['result']

        # If there's no result or the latest result has a date greater than or equal to today, break the loop
        if not result or (result and pd.to_datetime(result[-1]['timeStamp'], unit='s').date() >= today):
            break

        all_results.extend(result)
        page += 1

        # Add a delay between API calls to respect the rate limit (5 calls per second)
        time.sleep(1 / 5)  # sleep for 0.2 seconds (1/5th of a second)

    return all_results



def process_holders_data(holders_data):
    df = pd.DataFrame(holders_data)
    df['timestamp'] = pd.to_datetime(df['timeStamp'], unit='s')
    df['date'] = df['timestamp'].dt.date
    df['is_burn'] = df['to'] == '0x0000000000000000000000000000000000000000'
    df['is_mint'] = df['from'] == '0x0000000000000000000000000000000000000000'
    daily_holders = df.groupby('date').agg({'from': pd.Series.nunique, 'to': pd.Series.nunique, 'is_burn': sum, 'is_mint': sum})
    daily_holders['net_holders'] = daily_holders['to'] - daily_holders['from'] + daily_holders['is_mint'] - daily_holders['is_burn']
    daily_holders['cumulative_holders'] = daily_holders['net_holders'].cumsum()
    daily_holders['holder_increase'] = daily_holders['cumulative_holders'].diff()
    daily_holders['percent_change'] = daily_holders['cumulative_holders'].pct_change() * 100

    return daily_holders

def create_graph(daily_holders):
    fig, ax = plt.subplots()
    
    # Identify the first date with a positive holder increase
    launch_date = daily_holders[daily_holders['holder_increase'] > 0].index.min()

    # Filter daily_holders data starting from launch_date
    daily_holders_filtered = daily_holders[daily_holders.index >= launch_date]

    daily_holders_filtered['cumulative_holders'].plot(ax=ax)
    ax.set_xlabel('Date')
    ax.set_ylabel('Holders')
    ax.set_title('ERC20 Token Holders Over Time')

    # Set the font size and angle of x-axis date labels
    plt.xticks(fontsize=8, rotation=30)

    return fig


def submit_form(token_entry, api_key_entry, root):
    token_address = token_entry.get()
    api_key = api_key_entry.get()
    save_api_key(api_key)
    root.destroy()

    holders_data = get_holders_data(api_key, token_address)
    if not holders_data:
        print('No holders data found for this token address.')
        return

    daily_holders = process_holders_data(holders_data)
    fig = create_graph(daily_holders)
    
    result_window = Toplevel()
    result_window.title('Token Holders Over Time')
    canvas = FigureCanvasTkAgg(fig, master=result_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

    text_widget = Text(result_window, wrap='none', height=20)
    text_widget.pack(side='top', fill='both', expand=True, pady=(100, 100)) # Added padding to the top side
    scroll_y = Scrollbar(result_window, orient='vertical', command=text_widget.yview)
    scroll_y.pack(side='right', fill='y')
    daily_holders['holder_increase'] = daily_holders['holder_increase'].fillna(0).astype(int)
    daily_holders['percent_change'] = daily_holders['percent_change'].apply(lambda x: f'{x:.2f}%')
    daily_holders_reset = daily_holders.reset_index()
    selected_columns = daily_holders_reset[['date', 'cumulative_holders', 'holder_increase', 'percent_change']]
    text_widget.insert(END, str(selected_columns))

    result_window.mainloop()


def main():
    root = Tk()
    root.withdraw()
    
    prompt_window = Toplevel(root)
    prompt_window.title("Stoner4Life")
    
    Label(prompt_window, text="Stoner4Life", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=(10, 5))
    Label(prompt_window, text="Enter the ERC20 token address:").grid(row=1, column=0, padx=(10, 0), pady=(10, 5), sticky='e')
    Label(prompt_window, text="Enter your Etherscan API key:").grid(row=2, column=0, padx=(10, 0), pady=5, sticky='e')

    token_entry = Entry(prompt_window)
    token_entry.grid(row=1, column=1, padx=(0, 10), pady=(10, 5))
    api_key_entry = Entry(prompt_window)
    api_key_entry.grid(row=2, column=1, padx=(0, 10), pady=5)

    api_key = load_api_key()
    if api_key:
        api_key_entry.insert(0, api_key)

    Button(prompt_window, text="Submit", command=lambda: submit_form(token_entry, api_key_entry, root)).grid(row=3, column=0, columnspan=2, pady=(5, 10))

    root.mainloop()

if __name__ == '__main__':
    main()