## This program collects broker's (analysts) reports and their stock data
## 4. 9. 2017. by Heeyoon Lee

# import libraries
import requests
import htmlTableParser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from yahoo_finance import Share
import datetime
import holidays

today = datetime.date(2016, 4, 18)  # starting date
us_holidays = holidays.UnitedStates()
numDates = 220   # number of analyst data (including weekends and holidays)
nDaysToAnalyze = 30   # number of days to analyze since the release of analyst reports
count = 0

while True:
    try:
        # handling weekends and holidays
        if today.weekday() == 5:
            today = today + datetime.timedelta(days=2)
            continue
        elif today.weekday() == 6:
            today = today + datetime.timedelta(days=1)
            continue
        elif today in us_holidays:
            today = today + datetime.timedelta(days=1)
            continue

        # parse html table from the web
        dateStrUrl = today.strftime('%Y/%m/%d/')
        # url = 'https://www.briefing.com/Investor/Calendars/Upgrades-Downgrades/Upgrades/' + dateStrUrl
        url = 'https://www.briefing.com/Investor/Calendars/Upgrades-Downgrades/Initiated/' + dateStrUrl
        response = requests.get(url)
        hp = htmlTableParser.HTMLTableParser()
        table = hp.parse_url(url)
        df0 = table[2]  # select the right table

        print(today)
        # clean up the table
        idx = np.int_()
        for i in range(0, len(df0.index)):
            str = df0[3][i]
            if str[-3:] == 'Buy' or str[-10:] == 'Outperform' or str[-11:] == 'Over-Weight' or \
                    str[-12:] == 'Moderate Buy' or str[-3:] == 'Add' or str[-8:] == 'Positive' or str[-10:] == 'Accumulate':
                idx = np.append([idx], [i])
        # skip if there's no 'Buy' report
        if np.size(idx) == 1:
            today = today + datetime.timedelta(days=1)
            continue
        df = df0.iloc[idx, 0:3]
        df = df.reset_index(drop=True)
        df[3] = None
        df[4] = None
        df[5] = None
        df[6] = None
        df[7] = None
        df[3][0] = 'Open'
        df[4][0] = 'Close'
        df[5][0] = 'Volume'
        df[6][0] = 'NASDAQ_Open'
        df[7][0] = 'NASDAQ_Close'

        # collect stock data
        weekday = today.weekday()
        if weekday == 0:
            yest_date = today + datetime.timedelta(days=-3)
        else:
            yest_date = today + datetime.timedelta(days=-1)
        next_date = today + datetime.timedelta(days=nDaysToAnalyze - 1)

        sh_norm = Share('NDAQ')
        db_norm = sh_norm.get_historical(yest_date.isoformat(), next_date.isoformat())

        for i in range(1, len(df.index)):
            ticker = df[1][i]
            if '.' not in ticker:
                sh = Share(df[1][i])
                try:
                    db = sh.get_historical(yest_date.isoformat(), next_date.isoformat())
                except:
                    continue
                df[3][i] = [float(db[-1 - j]['Open']) for j in range(len(db))]
                df[4][i] = [float(db[-1 - j]['Close']) for j in range(len(db))]
                df[5][i] = [float(db[-1 - j]['Volume']) for j in range(len(db))]
                df[6][i] = [float(db_norm[-1 - j]['Open']) for j in range(len(db_norm))]
                df[7][i] = [float(db_norm[-1 - j]['Close']) for j in range(len(db_norm))]

        # append dataframe
        if count == 0:
            df_res = df
        else:
            df_res = pd.concat([df_res, df.loc[1:len(df)][:]], ignore_index = True)

        # increase count
        today = today + datetime.timedelta(days = 1)
        count = count + 1
        if count == numDates:
            break
    except:
        print('Error..')
        today = today + datetime.timedelta(days=1)
        continue

# delete rows with null values
df_res = df_res[df_res[3].notnull()]
df_res.reset_index()
df_res.index = range(0, len(df_res))

# print and output to files
print(df_res)
# df_res.to_pickle('output_initiated_all_220')
# df_res.to_csv('output.csv')