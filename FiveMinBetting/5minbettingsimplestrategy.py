import csv
import matplotlib.pyplot as plt

def read_csv_file(file_name):
    close_prices = []
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            close_prices.append(float(row[4]))
    return close_prices

def calculate_profit_or_loss(close_prices, bet_amount, strategy):
    profit_or_loss = [0]
    for i in range(1, len(close_prices)):
        if strategy == "same_direction":
            condition = (close_prices[i] > close_prices[i-1] and close_prices[i-1] > close_prices[i-2]) or \
                        (close_prices[i] < close_prices[i-1] and close_prices[i-1] < close_prices[i-2])
        elif strategy == "opposite_direction":
            condition = (close_prices[i] > close_prices[i-1] and close_prices[i-1] < close_prices[i-2]) or \
                        (close_prices[i] < close_prices[i-1] and close_prices[i-1] > close_prices[i-2])
        elif strategy == "always_up":
            condition = close_prices[i] > close_prices[i-1]
        else:  # always_down
            condition = close_prices[i] < close_prices[i-1]
        
        if condition:
            profit_or_loss.append(profit_or_loss[-1] + bet_amount)
        else:
            profit_or_loss.append(profit_or_loss[-1] - bet_amount)
    return profit_or_loss

file_name = 'crypto\MATIC_price_data.csv'
bet_amount = 20
close_prices = read_csv_file(file_name)

# Calculate profit or loss for all strategies
profit_or_loss_same_direction = calculate_profit_or_loss(close_prices, bet_amount, strategy="same_direction")
profit_or_loss_opposite_direction = calculate_profit_or_loss(close_prices, bet_amount, strategy="opposite_direction")
profit_or_loss_always_up = calculate_profit_or_loss(close_prices, bet_amount, strategy="always_up")
profit_or_loss_always_down = calculate_profit_or_loss(close_prices, bet_amount, strategy="always_down")

# Plot the results in a 2x2 grid
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

ax1.plot(profit_or_loss_same_direction)
ax1.set_title('Same Direction Betting Strategy')
ax1.set_xlabel('Bets')
ax1.set_ylabel('Total Profit or Loss ($)')

ax2.plot(profit_or_loss_opposite_direction)
ax2.set_title('Opposite Direction Betting Strategy')
ax2.set_xlabel('Bets')
ax2.set_ylabel('Total Profit or Loss ($)')

ax3.plot(profit_or_loss_always_up)
ax3.set_title('Always Bet Up Strategy')
ax3.set_xlabel('Bets')
ax3.set_ylabel('Total Profit or Loss ($)')

ax4.plot(profit_or_loss_always_down)
ax4.set_title('Always Bet Down Strategy')
ax4.set_xlabel('Bets')
ax4.set_ylabel('Total Profit or Loss ($)')

plt.tight_layout()
plt.show()
