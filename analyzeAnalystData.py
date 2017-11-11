import pandas as pd
import numpy as np

df0 = []
day_gainer = dict()
week1_gainer = dict()
week2_gainer = dict()
month_gainer = dict()

def load_data(type):
    global df0
    df0 = pd.read_pickle('output_' + type + '_normalized_to_nasdaq_220')
    df0.index = range(0, len(df0))

def find_gainers():
    global df0
    brokers = set(df0[2])
    print('Total number of brokers: ', len(brokers))
    global day_gainer, week1_gainer, week2_gainer, month_gainer
    num_broker_thres = 5
    day_thres = 1
    week1_thres = 1.5
    week2_thres = 2
    month_thres = 3

    while True:
        if len(brokers) == 0:
            break
        broker_name = brokers.pop()
        df = df0[:][df0[2] == broker_name]
        df.index = range(0, len(df))
        # print(broker_name + '(' + str(len(df)) + ')')
        # if len(df[3][len(df)-1]) < 12 | len(df)<:
        #     continue

        p1 = [df[4][i][0] for i in range(1,len(df))]
        p2 = [df[3][i][1] for i in range(1,len(df))]
        inc = [(p2[i]-p1[i])/p1[i]*100 for i in range(0,len(p1))]
        # print ('  overnight gain (%): ' + str(np.median(inc)))

        p1 = [df[3][i][1] for i in range(1,len(df))]
        p2 = [df[4][i][1] for i in range(1,len(df))]
        inc = [(p2[i]-p1[i])/p1[i]*100 for i in range(0,len(p1))]
        # print ('  1 day gain (%): ' + str(np.median(inc)))
        if (len(p1) > num_broker_thres) & (np.median(inc) > day_thres):
            day_gainer[broker_name] = np.median(inc)

        p1 = [df[3][i][1] for i in range(1,len(df))]
        p2 = [df[4][i][1+5] for i in range(1,len(df))]
        inc = [(p2[i]-p1[i])/p1[i]*100 for i in range(0,len(p1))]
        # print ('  1 week gain (%): ' + str(np.median(inc)))
        if (len(p1) > num_broker_thres) & (np.median(inc) > week1_thres):
            week1_gainer[broker_name] = np.median(inc)

        p1 = [df[3][i][1] for i in range(1,len(df))]
        p2 = [df[4][i][1+10] for i in range(1,len(df))]
        inc = [(p2[i]-p1[i])/p1[i]*100 for i in range(0,len(p1))]
        # print ('  2 weeks gain (%): ' + str(np.median(inc)))
        if (len(p1) > num_broker_thres) & (np.median(inc) > week2_thres):
            week2_gainer[broker_name] = np.median(inc)

        p1 = [df[3][i][1] for i in range(1,len(df))]
        p2 = [df[4][i][-1] for i in range(1,len(df))]
        inc = [(p2[i]-p1[i])/p1[i]*100 for i in range(0,len(p1))]
        # print ('  month gain (%): ' + str(np.median(inc)))
        if (len(p1) > num_broker_thres) & (np.median(inc) > month_thres):
            month_gainer[broker_name] = np.median(inc)

def print_good_brokers():
    global day_gainer, week1_gainer, week2_gainer, month_gainer
    print('< Day Gainers >')
    for key in sorted(day_gainer.keys()):
        print ("- %s:\t %s" % (key, day_gainer[key]))
    print('< 1-Week Gainers >')
    for key in sorted(week1_gainer.keys()):
        print ("- %s:\t %s" % (key, week1_gainer[key]))
    print('< 2-Week Gainers >')
    for key in sorted(week2_gainer.keys()):
        print ("- %s:\t %s" % (key, week2_gainer[key]))
    print('< Month Gainers >')
    for key in sorted(month_gainer.keys()):
        print ("- %s:\t %s" % (key, month_gainer[key]))

def print_broker_info(broker):
    global df0
    df = df0[:][df0[2] == broker]
    df.index = range(0, len(df))

    print('Total number of samples on [%s]: %d' % (broker, len(df)-1))
    if len(df) > 1:
        print_price_info(df)

def print_stock_info(stock):
    global df0
    df = df0[:][df0[1] == stock]
    df.index = range(0, len(df))

    print('Total number of samples on [%s]: %d' % (stock, len(df) - 1))
    if len(df) >1:
        print_price_info(df)

def print_price_info(df):
    p1 = [df[4][i][0] for i in range(1, len(df))]
    p2 = [df[3][i][1] for i in range(1, len(df))]
    inc = [(p2[i] - p1[i]) / p1[i] * 100 for i in range(0, len(p1))]
    print('  overnight gains (mean=%.2f, median=%.2f, std=%.2f): ' % (np.mean(inc), np.median(inc), np.std(inc)))
    print('   ', ['%.2f' % i for i in inc])

    p1 = [df[3][i][1] for i in range(1, len(df))]
    p2 = [df[4][i][1] for i in range(1, len(df))]
    inc = [(p2[i] - p1[i]) / p1[i] * 100 for i in range(0, len(p1))]
    print('  1-day gains (mean=%.2f, median=%.2f, std=%.2f): ' % (np.mean(inc), np.median(inc), np.std(inc)))
    print('   ', ['%.2f' % i for i in inc])

    p1 = [df[3][i][1] for i in range(1, len(df))]
    p2 = [df[4][i][1 + 5] for i in range(1, len(df))]
    inc = [(p2[i] - p1[i]) / p1[i] * 100 for i in range(0, len(p1))]
    print('  1-week gains (mean=%.2f, median=%.2f, std=%.2f): ' % (np.mean(inc), np.median(inc), np.std(inc)))
    print('   ', ['%.2f' % i for i in inc])

    p1 = [df[3][i][1] for i in range(1, len(df))]
    p2 = [df[4][i][1 + 10] for i in range(1, len(df))]
    inc = [(p2[i] - p1[i]) / p1[i] * 100 for i in range(0, len(p1))]
    print('  2-week gains (mean=%.2f, median=%.2f, std=%.2f): ' % (np.mean(inc), np.median(inc), np.std(inc)))
    print('   ', ['%.2f' % i for i in inc])

    p1 = [df[3][i][1] for i in range(1, len(df))]
    p2 = [df[4][i][-1] for i in range(1, len(df))]
    inc = [(p2[i] - p1[i]) / p1[i] * 100 for i in range(0, len(p1))]
    print('  month gains (mean=%.2f, median=%.2f, std=%.2f): ' % (np.mean(inc), np.median(inc), np.std(inc)))
    print('   ', ['%.2f' % i for i in inc])
