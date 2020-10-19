import alpaca_trade_api as tradeapi
import pandas as pd
import json
import math
import statistics
import time
import datetime
import argparse
from multiprocessing import Pool, Process

parser = argparse.ArgumentParser(description="Continuously process multiple symbols")
parser.add_argument('symbols', metavar='S', type = str, nargs = '+', help = 'A symbol for the process')

args = parser.parse_args()

config = open('alpaca.json', 'r')
creds = json.loads(config.read())

api = tradeapi.REST(creds['KEY_ID'], creds['SECRET_KEY'], base_url='https://paper-api.alpaca.markets') # or use ENV Vars shown below
account = api.get_account()
cash = account.cash

#The trading function
#Takes a symbol and calculates bollinger bands from the last 20 days of that symbol
def bollinger_band_trader(symbol):
    symbol = symbol.upper()    

    position = list(map(lambda bar: (bar.o + bar.c)/2 , api.get_barset(symbol, 'day', limit = 20)[symbol]))

    if(position):
        mean = statistics.mean(position)
        upper = mean + 2 * statistics.stdev(position)
        lower = mean - 2 * statistics.stdev(position)

        #Calculate number of initial shares that can be buyed
        price = api.get_last_trade(symbol).price
        symbol_percent = 1/len(args.symbols)
        buyable_shares = math.floor((symbol_percent * float(cash) * .75) / price)               

        #Must dynamically calculate how much to invest in this position from list of current symbols in args.
        #If the current price of the current position is greater than the upper limit, sell this position.
        #If the current price of the current position is less that the lower limit, buy this position.
        while(True):
            weekno = datetime.datetime.today().weekday()

            the_time = datetime.datetime.now().time()
            print(the_time)
            
            #Make sure the program runs during weekdays and between market hours 
            #opening at 9:30am and closing at 4:00pm
            if(weekno <= 4):
                price = api.get_last_trade(symbol).price
                has_position = True if api.get_position(symbol) else False
                
                print(price)
                #Check if a position already exists in the portfolio
                if price >= upper and has_position is True:
                    #Sell Sell Sell!!!
                    api.submit_order(
                        symbol= symbol,
                        qty= buyable_shares,
                        side = 'sell',
                        type = 'market',
                        time_in_force = 'day'
                    )          

                    print("Sold " + str(buyable_shares) + " shares.")          

                elif price <= lower and has_position is False:
                    #Buy Buy Buy!!!
                    api.submit_order(
                        symbol= symbol,
                        qty= buyable_shares,
                        side = 'buy',
                        type = 'market',
                        time_in_force = 'day'
                    )

                    print("Bought " + str(buyable_shares) + " shares.")

                #Moniter the current price every T amount of seconds
                T = 30
                time.sleep(T)

                #Get the next conditions for the next price check
                position = list(map(lambda bar: (bar.o + bar.c)/2 , api.get_barset(symbol, 'day', limit = 20)[symbol]))
                mean = statistics.mean(position)
                upper = mean + 2 * statistics.stdev(position)
                lower = mean - 2 * statistics.stdev(position)

            #If it is the weekend, check every hour for whether it is the weekday
            if(weekno >= 5):
                print('It is the weekend. Market is closed.')
                T = 3600
                time.sleep(T)          

    else:
        print('Invalid Symbol')


if __name__ == '__main__':
    # p = Pool(len(args.symbols))
    # p.map(bollinger_band_trader, args.symbols)
    # p.terminate()

    for sym in args.symbols:
        bollinger_band_trader(sym)

    