import pickle
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pandas_datareader as web
import mplfinance as mpf
import yfinance as yf
import streamlit as st


import nltk
from nltk.chat.util import Chat, reflections
import json


# Download the required NLTK data
nltk.download('punkt')
nltk.download('wordnet')

# Disable SSL certificate verification
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

portfolio = {"AAPL": 20, "TSLA": 5, "GS": 10}

# Create a new PKL
new_portfolio = {"AAPL": 20, "TSLA": 5, "GS": 10}
filename = "newportfolio.pkl"
with open(filename, "wb") as f:
    pickle.dump(new_portfolio, f)



def save_portfolio():
    with open("newportfolio.pkl", "wb") as f:
        pickle.dump(portfolio, f)

def add_portfolio():
    ticker = input("What is the ticker symbol of the stock you want to add? ")
    shares = input("Enter Shares: ")

    if ticker in portfolio.keys():
        portfolio[ticker] += int(shares)
    else:
        portfolio[ticker] = int(shares)

    save_portfolio()

def remove_portfolio():
    ticker = input("What is the ticker symbol of the stock you want to remove? ")
    amount = input("How many shares do you want to remove? ")

    if ticker in portfolio.keys():
        if int(amount) <= portfolio[ticker]:
            portfolio[ticker] -= int(amount)
            save_portfolio()
        else:
            print("You don't have enough shares to sell")
    else:
        print("You don't have enough shares to sell")

def show_portfolio():
    print("Your portfolio:")
    for ticker in portfolio.keys():
        print(f"You Own {portfolio[ticker]} shares of {ticker} stock")
        

def portfolio_worth():
    sum = 0
    for ticker in portfolio.keys():
        data = web.DataReader(ticker, 'yahoo')
        price = data['Close'].iloc[-1]
        sum += price
    print(f"Your portfolio is worth {sum} dollars")



def portfolio_gains():
    starting_date = input("Enter the starting date in YYYY-MM-DD format:")
    sum_now = 0
    sum_then = 0
    try:
        for ticker in portfolio.keys():
            data = yf.download(ticker)
            price_now = data['Close'].iloc[-1]
            price_then = data.loc[data.index == starting_date]['Close'].values[0]
            sum_now += price_now
            sum_then += price_then
        print(f"Relative Gains: {((sum_now - sum_then) / sum_then) * 100}%")
        print(f"Absolute Gains: {sum_now - sum_then} dollars")
    except IndexError:
        print("There was no trading on this day")




def plot_chart():
    ticker = input("Choose a ticker symbol to plot:")
    starting_string = input("Enter the starting date in DD/MM/YYYY format: ")
    plt.style.use('dark_background')
    start = dt.datetime.strptime(starting_string, '%d/%m/%Y')
    end = dt.datetime.now()
    data = yf.download(ticker, start=start, end=end)
    data['Date'] = data.index  # Convert the index to a column
    colors = mpf.make_marketcolors(up='g', down='r')
    mpf_style = mpf.make_mpf_style(marketcolors=colors)
    mpf.plot(data, type='candle', style=mpf_style)

def main():
    # Load intents file
    with open("intents.json") as file:
        intents = json.load(file)

    # Extract patterns and responses from intents
    patterns = []
    responses = []
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            patterns.append(pattern)
            responses.append(intent['responses'])

    # Create pairs for the Chat model
    pairs = list(zip(patterns, responses))

    # Create a custom Chat subclass for case-insensitive matching
    class CustomChat(Chat):
        def respond(self, message):
            message = message.lower()  # Convert input to lowercase for case-insensitive matching


            
            if(message == 'add portfolio'):
                return add_portfolio()

            if(message=='show portfolio'):
                return show_portfolio()
            

            if(message=='remove portfolio'):
                return remove_portfolio()
            

            if(message=='portfolio worth'):
                return portfolio_worth()
            

            if(message=='portfolio gains'):
                return portfolio_gains()
            

            if(message=='plot chart'):
                return plot_chart()
    



            return super().respond(message)





       

    # Create the chatbot using the CustomChat class
    chatbot = CustomChat(pairs, reflections)

    print("Type 'quit' to exit")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        response = chatbot.respond(user_input)
        if response is not None:
            print("Bot: " + response)
       

if __name__ == "__main__":
    main()

