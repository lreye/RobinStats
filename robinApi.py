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

import os 
import pyotp 
import robin_stocks as r
import pandas as pd
from dotenv import load_dotenv   #for python-dotenv method
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

positionsDF = pd.DataFrame(r.get_all_positions())

print(positionsDF.head())
#r.export_completed_stock_orders(".")


my_stock_history = pd.read_csv("stock_orders_Oct-27-2020.csv")
print(my_stock_history.head())