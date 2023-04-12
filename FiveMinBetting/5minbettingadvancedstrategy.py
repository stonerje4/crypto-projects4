import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def read_csv_file(file_name):
    data = pd.read_csv(file_name, index_col=0, parse_dates=True)
    return data

def calculate_profit_or_loss(data, bet_amount, strategy):
    close_prices = data['Close']
    profit_or_loss = [0]

    if strategy == "moving_averages":
        short_ma = close_prices.rolling(window=5).mean()
        long_ma = close_prices.rolling(window=20).mean()
    elif strategy == "rsi":
        delta = close_prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    elif strategy == "bollinger_bands":
        sma = close_prices.rolling(window=20).mean()
        std = close_prices.rolling(window=20).std()
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)
    elif strategy == "fibonacci":
        fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]

    for i in range(2, len(close_prices)):
        if strategy == "moving_averages":
            condition = short_ma[i] > long_ma[i]
        elif strategy == "rsi":
            condition = rsi[i] < 30
        elif strategy == "bollinger_bands":
            condition = close_prices[i] < lower_band[i]
        elif strategy == "fibonacci":
            max_price = max(close_prices[:i])
            min_price = min(close_prices[:i])
            price_range = max_price - min_price
            retracements = [max_price - level * price_range for level in fib_levels]
            condition = any([min_price <= close_prices[i] <= level for level in retracements])

        if condition:
            if close_prices[i] > close_prices[i - 1]:
                profit_or_loss.append(profit_or_loss[-1] + bet_amount)
            else:
                profit_or_loss.append(profit_or_loss[-1] - bet_amount)
        else:
            if close_prices[i] < close_prices[i - 1]:
                profit_or_loss.append(profit_or_loss[-1] + bet_amount)
            else:
                profit_or_loss.append(profit_or_loss[-1] - bet_amount)

    return profit_or_loss


file_name = 'crypto\MATIC_price_data.csv'
bet_amount = 20
data = read_csv_file(file_name)

# Calculate profit or loss for all strategies
profit_or_loss_moving_averages = calculate_profit_or_loss(data, bet_amount, strategy="moving_averages")
profit_or_loss_rsi = calculate_profit_or_loss(data, bet_amount, strategy="rsi")
profit_or_loss_bollinger_bands = calculate_profit_or_loss(data, bet_amount, strategy="bollinger_bands")
profit_or_loss_fibonacci = calculate_profit_or_loss(data, bet_amount, strategy="fibonacci")

# Plot the profit or loss for each strategy
plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plt.plot(profit_or_loss_moving_averages, label="Moving Averages")
plt.xlabel('Index')
plt.ylabel('Profit/Loss')
plt.legend()

plt.subplot(2, 2, 2)
plt.plot(profit_or_loss_rsi, label="RSI")
plt.xlabel('Index')
plt.ylabel('Profit/Loss')
plt.legend()

plt.subplot(2, 2, 3)
plt.plot(profit_or_loss_bollinger_bands, label="Bollinger Bands")
plt.xlabel('Index')
plt.ylabel('Profit/Loss')
plt.legend()

plt.subplot(2, 2, 4)
plt.plot(profit_or_loss_fibonacci, label="Fibonacci")
plt.xlabel('Index')
plt.ylabel('Profit/Loss')
plt.legend()

plt.tight_layout()
plt.show()