from yahoo_finance import Share
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time

symbol = 'MSFT'
sh = Share(symbol)
db=sh.get_historical('2012-02-23', '2017-02-23')
firstDay = datetime.datetime.strptime(db[-1]['Date'], "%Y-%m-%d").weekday()
print('first day: ', firstDay)  # 0:Monday, 6:Sunday

ts = [time.mktime(datetime.datetime.strptime(ls['Date'], "%Y-%m-%d").timetuple()) for ls in db]
days = [int(float((t - ts[-1])/(24*60*60))) for t in ts]  # normalize
numDays = int(days[0] - days[-1] + 1)
close = [float(ls['Adj_Close']) for ls in db]
volume = [float(ls['Volume']) for ls in db]
print('Keys: ', db[0].keys())

# reverse array
days = days[::-1]
close = close[::-1]
volume = volume[::-1]

# fill in the gaps (holidays + weekends)
close2 = np.zeros(numDays)
close2[0] = close[0]
count = 1
for i in range(1, numDays):
    if days[count] == i:
        close2[i] = close[count]
        count += 1
    else:
        close2[i] = close2[i-1]
days2 = range(0, days[-1]+1)
numDays2 = int(days2[-1] - days2[0] + 1)

m2, m1, b = np.polyfit(days2, close2, 2)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(days2, close2)
ax.set_title('Close Price')

close_fft = np.abs(np.fft.fft([close2[i] - (m2*i*i+m1*i+b) for i in range(0, numDays2)]))
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(close_fft)
ax.set_title('FFT [Close Price]')

print('monday ave: ', np.mean(close2[0+7-firstDay : 0+7-firstDay + 7 * int(np.floor(numDays2/7)-2) : 7]))
print('tuesday ave: ', np.mean(close2[1+7-firstDay : 1+7-firstDay + 7 * int(np.floor(numDays2/7)-2) : 7]))
print('wednesday ave: ', np.mean(close2[2+7-firstDay : 2+7-firstDay + 7 * int(np.floor(numDays2/7)-2) : 7]))
print('thursday ave: ', np.mean(close2[3+7-firstDay : 3+7-firstDay + 7 * int(np.floor(numDays2/7)-2) : 7]))
print('friday ave: ', np.mean(close2[4+7-firstDay : 4+7-firstDay + 7 * int(np.floor(numDays2/7)-2) : 7]))

plt.show()