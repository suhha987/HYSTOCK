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
import sys
from itertools import groupby
import os

# global variables
urlBase = 'https://www.briefing.com/Investor/Calendars/Upgrades-Downgrades'
urlLevel = 'Upgrades'  # Upgrades/Downgrades/Coverage Initiated/Coverage Initiated/CoverageResumed/Coverage Reit/Price Tgt Changed
rateChangeColName = 'Ratings Change'
brokerColName = 'Brokerage Firm'
ratingNamesOutputFile = 'RatingNames.csv'
brokerFreqOutputFile = 'BrokerFreq.csv'
dataOutputFile = 'data.csv'
workDir = '/Users/hayoung/Desktop/HYSTOCK/status/dataprocess'

def main() :
    numDates = 365  # number of dates to look at (including holidays/weekends)
    # today = datetime.date(2017, 7, 1)  # starting date
    enddate = datetime.datetime.now().date()  # today's date
    # tmp
    # enddate = enddate - datetime.timedelta(days=6)
    # startdate = enddate.replace(year = enddate.year-1) # starting date
    # startdate = startdate + datetime.timedelta(days = 1)
    startdate = enddate - datetime.timedelta(days=numDates)

    us_holidays = holidays.UnitedStates()
    # count = 0
    df_all = pd.DataFrame()

    # get the latest date processed data
    folderList = [x for x in os.listdir(workDir) if x != '.DS_Store']
    succeed = [(os.path.exists("%s/%s/success.txt" % (workDir, x))) for x in folderList]
    processedList = [datetime.datetime.strptime(x, '%Y-%m-%d').date() for x in np.array(folderList)[succeed]]
    if (len(processedList) > 0):
        latestDate = max(processedList)
        datelist = pd.date_range(max(startdate, (latestDate + datetime.timedelta(days=1))),
                                 enddate).tolist()  # dates to get the broker's data
        df_all = pd.read_csv("%s/%s/%s" % (workDir, latestDate, dataOutputFile))
    else:
        datelist = pd.date_range(startdate, enddate).tolist()  # dates to get the broker's data

    for today in datelist:

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
        dateStrUrl = today.strftime('%Y/%m/%d')
        print(dateStrUrl)

        url = "%s/%s/%s" % (urlBase, urlLevel, dateStrUrl)
        response = requests.get(url)
        hp = htmlTableParser.HTMLTableParser()
        table = hp.parse_url(url)

        df = table[2]  # select the right table
        # get 1st row as header of the table
        header = df.iloc[0]
        df = df[1:]
        df.columns = header
        df = df.reset_index(drop=True)

        if (len(df) == 0):
            today = today + datetime.timedelta(days=1)
            continue

        df['Date'] = dateStrUrl
        # divide RatingChange column into before/after
        for i in range(0, len(df.index)):
            rateChange = df[rateChangeColName][i]
            # if str[-3:] == 'Buy' or str[-10:] == 'Outperform' or str[-11:] == 'Over-Weight' or \
            #        str[-12:] == 'Moderate Buy' or str[-3:] == 'Add' or str[-8:] == 'Positive' or str[-10:] == 'Accumulate':
            #    idx = np.append([idx], [i])
            df['Rating Before'] = [x.split("»")[0].strip() for x in df[rateChangeColName]]
            df['Rating After'] = [x.split("»")[1].strip() for x in df[rateChangeColName]]

        cols = ['Date'] + [col for col in df if col != 'Date']
        df = df[cols]
        ### TODO : add information from NDAQ to df ###

        # append dataframe
        if (len(df_all) == 0):
            df_all = df
        else:
            # df_all = pd.concat([df_all, df.loc[1:len(df)][:]], ignore_index = True)
            df_all = pd.concat([df_all, df], ignore_index=True)

        # update today
        today = today + datetime.timedelta(days=1)

    getAllPossibleRatingNames(df_all, ratingNamesOutputFile)
    cols = ['Date'] + [col for col in df_all if col != 'Date']
    df_all = df_all[cols]
    # save dataframe

    # broker frequency
    getBrokerFreq(df_all, brokerFreqOutputFile)
    saveData(df_all, enddate, dataOutputFile)

# get each rating name and its frequency
def getAllPossibleRatingNames(df, outputFile) :
    allRatingNames = np.append(np.array(df['Rating Before'].values), np.array(df['Rating After'].values))
    unique, counts = np.unique(allRatingNames, return_counts=True)
    nameFreq = np.asarray((unique, counts)).T
    freqDf = pd.DataFrame(nameFreq)
    freqDf.columns = ['Rating Name', 'Frequency']
    freqDf = freqDf.sort_values('Frequency', ascending=False)
    freqDf.to_csv(outputFile, index = False)

# get broker/its frequency in df
def getBrokerFreq(df, outputFile) :
    allBrokerNames = np.array(df[brokerColName])
    unique, counts = np.unique(allBrokerNames, return_counts=True)
    brokerFreq = np.asarray((unique, counts)).T
    freqDf = pd.DataFrame(brokerFreq)
    freqDf.columns = ['Broker Name', 'Frequency']
    freqDf = freqDf.sort_values('Frequency', ascending=False)
    freqDf.to_csv(outputFile, index = False)

def saveData(df_all, date, outputFile) :
    outputDir = "%s/%s" % (workDir,date)
    if ((os.path.exists(outputDir))==False) :
        os.makedirs(outputDir)
    outputPath = "%s/%s" % (outputDir, outputFile)
    df_all.to_csv(outputPath, index = False)
    # save success file
    with open("%s/%s/%s" % (workDir,date,"success.txt"), "w") as txtfile :
        txtfile.write("all done")



if __name__ == '__main__':
    main()
"""
import io
def google_stocks(symbol, startdate=(1, 1, 2005), enddate=(1, 1, 2006)):
    startdate = str(startdate[0]) + '+' + str(startdate[1]) + '+' + str(startdate[2])
    # startdate = startdate[0] + '+' + startdate[1] + '+' + str(startdate[2])
    # if not enddate:
    # enddate = time.strftime("%m+%d+%Y")
    #    enddate = datetime.datetime.strftime("%m+%d+%Y")
    # else:
    enddate = str(enddate[0]) + '+' + str(enddate[1]) + '+' + str(enddate[2])

    stock_url = "http://www.google.com/finance/historical?q=" + symbol + \
                "&startdate=" + startdate + "&enddate=" + enddate + "&output=csv"
    print(stock_url)
    raw_response = requests.get(stock_url).content

    stock_data = pd.read_csv(io.StringIO(raw_response.decode('utf-8')))

    return stock_data


if __name__ == '__main__':
    apple_data = google_stocks('AAPL')
    print(apple_data)

    apple_truncated = google_stocks('AAPL', startdate=(1, 1, 2017), enddate=(11, 10, 2017))
    print(apple_truncated)
"""