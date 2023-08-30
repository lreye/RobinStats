import os 
import pyotp 
import robin_stocks as r
import pandas as pd
from dotenv import load_dotenv   #for python-dotenv method
import os, errno
#TODO: Create api to get the full stock ticker for a certain ticker kind of what I am doing
#with mydictionary
#TODO: Create metric to calculate percent return per year.
#TODO: Add Database

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

def getGains(profileData, allTransactions, cardTransactions):
    deposits = sum(float(x['amount']) for x in allTransactions if (x['direction'] == 'deposit') and (x['state'] == 'completed'))
    withdrawals = sum(float(x['amount']) for x in allTransactions if (x['direction'] == 'withdraw') and (x['state'] == 'completed'))
    debits = sum(float(x['amount']['amount']) for x in cardTransactions if (x['direction'] == 'debit' and (x['transaction_type'] == 'settled')))
    reversal_fees = sum(float(x['fees']) for x in allTransactions if (x['direction'] == 'deposit') and (x['state'] == 'reversed'))

    money_invested = deposits + reversal_fees - (withdrawals - debits)
    dividends = r.get_total_dividends()
    percentDividend = dividends/money_invested*100

    equity = float(profileData['extended_hours_equity'])
    totalGainMinusDividends = equity - dividends - money_invested
    percentGain = totalGainMinusDividends/money_invested*100

    print("The total money invested is {:.2f}".format(money_invested))
    print("The total equity is {:.2f}".format(equity))
    print("The net worth has increased {:0.2}% due to dividends that amount to {:0.2f}".format(percentDividend, dividends))
    print("The net worth has increased {:0.3}% due to other gains that amount to {:0.2f}".format(percentGain, totalGainMinusDividends))


load_dotenv()                    #for python-dotenv method

user = os.environ.get('USER_ROBINHOOD')
password = os.environ.get('PASSWORD_ROBINHOOD')
secret =  os.environ.get('SECRET_ROBINHOOD')

totp = pyotp.TOTP(secret).now() 
print("Current OTP:", totp)
login = r.login(user, password, mfa_code=totp)

my_stocks = r.build_holdings()

profileD = r.load_portfolio_profile()
allTranns = r.get_bank_transfers()
cardTrans= r.get_card_transactions()
getGains(profileD, allTranns, cardTrans)
print()

# transDF = pd.DataFrame(allTranns)
# holdingsDF = pd.DataFrame(r.build_holdings())

# print(holdingsDF.head())
# print
#stocks_to_stocks_exchange_dic = {"":""}
positionsDF = pd.DataFrame(r.get_all_positions())

#print(positionsDF.head())
silentremove("stock_history.csv")
r.export_completed_stock_orders("StockHistory", file_name="stock_history")

my_stock_history = pd.read_csv("stock_history.csv")
print(my_stock_history.head())
columnsDic = {'symbol': 'Ticker Symbol', 'date': 'Date (mm/dd/yyyy)', 'quantity': 'Shares', 
            'average_price':'Price', 'side':'Type'}
columns_list = ['Ticker Symbol', 'Date (mm/dd/yyyy)', 'Shares', 'Price', 'Type']
my_stock_history = my_stock_history.drop(['fees', 'order_type'], 1)
my_stock_history = my_stock_history.rename(columns=columnsDic)
my_stock_history = my_stock_history[columns_list]
my_stock_history['Cost'] = my_stock_history.apply(lambda row: row.Shares * row.Price, axis=1)
my_stock_history['Type'] = my_stock_history['Type'].apply(lambda x: x.capitalize()) 
my_stock_history = my_stock_history.round({'Shares': 2, 'Price': 2, 'Cost':2})
#my_stock_history['Shares'] = my_stock_history['Shares'].astype(int)
my_stock_history['Date (mm/dd/yyyy)'] = pd.to_datetime(my_stock_history['Date (mm/dd/yyyy)']).dt.strftime('%m/%d/%Y')
my_stock_history = my_stock_history[my_stock_history['Ticker Symbol'] != 'TVPT']

print(my_stock_history.head())
#stock_symbols = ['HEXO' 'QD' 'DBX' 'ARKK' 'T' 'VTV' 'CRBP' 'AAL' 'TMUS' 'DAL' 'BAC' 'VZ'
# 'NVDA' 'DIS' 'BK' 'AMD' 'ROKU' 'GE' 'SNAP' 'TWTR']


stock_symbols_to_exchanges_dic = {'HEXO': 'NYSE:HEXO', 'QD':'NYSE:QD', 'DBX':'NasdaqGS:DBX', 
 'ARKK': 'ARCA:ARKK', 'T': 'NYSE:T', 'VTV':'ARCA:VTV', 'CRBP':'NasdaqGM:CRBP', 'AAL':'NasdaqGS:AAL', 
 'TMUS':'NasdaqGS:TMUS', 'DAL':'NYSE:DAL', 'BAC':'NYSE:BAC','VZ':'NYSE:VZ', 'NVDA':'NasdaqGS:NVDA', 
 'DIS':'NYSE:DIS', 'BK':'NYSE:BK', 'AMD':'NasdaqGS:AMD', 'ROKU':'NasdaqGS:ROKU', 'GE':'NYSE:GE', 
 'SNAP':'NYSE:SNAP','TWTR':'NYSE:TWTR', 'QYLD':'NasdaqGM:QYLD'}
 #we can get stock exchanges with yahoo api will implement an api in future to do this

my_stock_history = my_stock_history.replace({'Ticker Symbol': stock_symbols_to_exchanges_dic})
pd.set_option("display.max_rows", None, "display.max_columns", None)
silentremove("Stocks_for_SimplyWallSt.csv")
my_stock_history.to_csv("Stocks_for_SimplyWallSt.csv", encoding='utf-8', index=False)