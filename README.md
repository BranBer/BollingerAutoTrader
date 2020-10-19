# BollingerAutoTrader

### To download the required libraries on linux:
<br>
pip3 install -r requirements.txt

### To download the required windows on linux:
<br/>
pip3 install -r requirements.txt

### To run on the command prompt on linux:
<br/>
python3 BollingerTrader.py """STOCK SYMBOLS HERE"""
<br/>
<br/>
Example: 
<br/>
python3 BollingerTrader.py S F AAPL MSFT T
      
### To run on the command prompt on windows:
<br/>
python BollingerTrader.py """STOCK SYMBOLS HERE"""
<br/>
<br/>
Example:
<br/>
python BollingerTrader.py S F AAPL MSFT T

### Use this with Crontabs on linux 
On a linux machine, type:
<br/>
sudo cron -e
<br/>
<br/>
Then paste:
<br/>
0 9 * * 1-5 """Absolute Path of Python Environment""" """Absolute Path of BollingerTrader.py""" aapl f t >> ~/cron.log 2>&1
<br/>
0 16 * * 1-5 /usr/bin/pkill -f 'python.*BollingerTrader.py'
<br/>
This will make the program run at 9:00am when the market opens on weekdays only, and terminate it on weekdays when the market closes at 4:00pm.


