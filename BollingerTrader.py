import alpaca_trade_api as tradeapi
import os
from sys import platform
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

log = open('BollingerTrader.log', 'a')

pid = os.getpid()

log.write('-' * 20 + '\n')
log.write('PID: ' + str(pid) + '\n')
log.write(datetime.datetime.now().strftime("%Y%m%dT%H:%M:%S") + '\n')
log.write('-' * 20 + '\n')

log.close()

api = tradeapi.REST(creds['KEY_ID'], creds['SECRET_KEY'], base_url='https://paper-api.alpaca.markets') # or use ENV Vars shown below
account = api.get_account()
cash = account.cash

market_open = datetime.time(9, 0, 0)
market_close = datetime.time(16, 0, 0)

print('Begin on ' + platform + ' system')

#The trading function
#Takes a symbol and calculates bollinger bands from the last 20 days of that symbol
def bollinger_band_trader(symbol):
    symbol = symbol.upper()    
    record = '---\n'
    sellable_shares = 0

    #print(symbol)

    position = list(map(lambda bar: (bar.o + bar.c)/2 , api.get_barset(symbol, 'minute', limit = 1000)[symbol]))

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
            #print(the_time)
            
            #Make sure the program runs during weekdays and between market hours 
            #opening at 9:00am and closing at 4:00pm
            if(weekno <= 4 and the_time >= market_open and the_time <= market_close):
                price = api.get_last_trade(symbol).price
                has_position = True 

                try:
                    has_position = True 
                    owned_position = api.get_position(symbol)   
                    sellable_shares = owned_position.qty               
                except Exception:
                    has_position = False

                #print('Owns position ' + symbol + ': ' + str(has_position))

                #Check if a position already exists in the portfolio
                if price >= upper and has_position is True:
                    #Sell Sell Sell!!!
                    api.submit_order(
                        symbol= symbol,
                        qty= sellable_shares,
                        side = 'sell',
                        type = 'market',
                        time_in_force = 'day'
                    )       
                    
                    now = str(datetime.datetime.now().strftime("%Y%m%dT%H:%M:%S"))
                    log = open('BollingerTrader.log', 'a')
                    log.write( now + '\n')
                    log.write('Sold ' + str(sellable_shares) + ' of ' + symbol + ' for a total of $' + str(sellable_shares * price) + '\n')       
                    log.write('-' * 20 + '\n')       
                    log.close()

                    record += 'Sold ' + str(sellable_shares) + ' of ' + symbol + ' for a total of ' + str(sellable_shares * price) + '\n'   
   

                if price <= lower and has_position is False:
                    #Buy Buy Buy!!!
                    api.submit_order(
                        symbol= symbol,
                        qty= buyable_shares,
                        side = 'buy',
                        type = 'market',
                        time_in_force = 'day'
                    )
                    
                    now = str(datetime.datetime.now().strftime("%Y%m%dT%H:%M:%S"))
                    log = open('BollingerTrader.log', 'a')
                    log.write( now + '\n')
                    log.write('Bought ' + str(buyable_shares) + ' of ' + symbol + ' for a total of $' + str(buyable_shares * price) + '\n')       
                    log.write('-' * 20 + '\n')
                    log.close()

                    record += 'Bought ' + str(buyable_shares) + ' of ' + symbol + ' for a total of $' + str(buyable_shares * price) + '\n'


                #Moniter the current price every T amount of seconds
                T = 15
                time.sleep(T)

                #Get the next conditions for the next price check
                position = list(map(lambda bar: (bar.o + bar.c)/2 , api.get_barset(symbol, 'minute', limit = 1000)[symbol]))
                mean = statistics.mean(position)
                upper = mean + 2 * statistics.stdev(position)
                lower = mean - 2 * statistics.stdev(position)
                
                print('      Symbol: ' + symbol)
                print('        Mean: $' + str(mean))
                print('Upper Bounds: $' + str(upper))
                print('Lower Bounds: $' + str(lower))
                print(record)
                print('-' * 20)

            #If it is the weekend, check every hour for whether it is the weekday
            if(weekno >= 5):
                print('It is the weekend. Market is closed.')
                T = 3600
                time.sleep(T)     

        log.close()    
        config.close() 

    else:
        print('Invalid Symbol')


if __name__ == '__main__':
    p = Pool(len(args.symbols))
    p.map(bollinger_band_trader, args.symbols)
    p.terminate()

    # for sym in args.symbols:
    #     bollinger_band_trader(sym)


