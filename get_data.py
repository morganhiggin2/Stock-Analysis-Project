import numpy
import pandas
import datetime
import requests
import os
import matplotlib.pyplot as plot
from mpl_toolkits.mplot3d import Axes3D
import math

read_path = "C:/Users/morga/Documents/Stock Data/data/5_min_test"
write_path = "C:/Users/morga/Documents/Stock Data/5_min"

#TINGO DATA

nasdaq_stocks_url = "https://dumbstockapi.com/stock?format=csv&exchanges=NASDAQ"
nyse_stocks_url = "https://dumbstockapi.com/stock?format=csv&exchanges=NYSE"

stock_data_location = "C:/Users/morga/Documents/Stock Data"

def update_tradable_tickers():
    nyse_tickers = pandas.read_csv(nyse_stocks_url)
    nasdaq_tickers = pandas.read_csv(nasdaq_stocks_url)

    #combine
    all_tickers = pandas.concat([nyse_tickers, nasdaq_tickers])

    #remove rows other than ticker and exchange
    all_tickers = all_tickers.drop(labels=["is_etf", "name"], axis=1)

    #remove duplicates (not needed)
    #all_tickers.drop_duplicates()

    #sort alphabetically based on ticker
    all_tickers = all_tickers.sort_values(by="ticker")

    #reset the indexes
    all_tickers = all_tickers.reset_index(drop=True)

    #write to computer
    all_tickers.to_csv(stock_data_location + "/tradable_tickers.csv", index=False)

def update_iex_tickers():
    headers = {
        'Content-Type': 'application/json'
    }
    requestResponse = requests.get("https://api.tiingo.com/iex/?token=bab507258bcd54db87fb178ad1be94a45fddf0d2", headers=headers)
    stock_listings = pandas.read_json(requestResponse.content)
    tickers = stock_listings['ticker']
    tickers.to_csv(stock_data_location + "/tickers.csv", index=False)

def get_iex_tickers():
    tickers = pandas.read_csv(stock_data_location + "/tickers.csv")
    return tickers

def get_tradable_tickers():
    #get tickers
    tickers = pandas.read_csv(stock_data_location + "/tradable_tickers.csv")["ticker"]
    iex_tickers = pandas.read_csv(stock_data_location + "/tickers.csv")["ticker"]

    #get ones from tradable tickers that are also in iex
    tradable_tickers = tickers[tickers.isin(iex_tickers)]

    #clean data
    tradable_tickers = tradable_tickers.reset_index(0)
    tradable_tickers.__delitem__("index")

    #return it
    return tradable_tickers

def get_ticker_data_5_min(ticker_symbol):
    return pandas.read_csv(stock_data_location + "/" + "5_min" + "/" + ticker_symbol + "_5min_stock_data.csv")

#retive data from tiingo
def retrieve_ticker_data_5_min(ticker_symbol):
    #date range for first data set
    enddate = numpy.busday_offset(datetime.date.today(), 0, roll="backward").astype(datetime.date)
    startdate = numpy.busday_offset(enddate, -124, roll="forward").astype(datetime.date)

    #get ticker data for the enddate and startdate
    def get_ticker_data():
        headers = {
            'Content-Type': 'application/json'
        }

        url = "https://api.tiingo.com/iex/" + ticker_symbol + "/prices?" + "resampleFreq=5min&columns=open,high,low,close,volume&token=bab507258bcd54db87fb178ad1be94a45fddf0d2&startDate=" + startdate.strftime("%Y-%m-%d") + "&endDate=" + enddate.strftime("%Y-%m-%d")
        requestResponse = requests.get(url, headers=headers)

        #because of holidays, if you request data for a holiday, it will return the data of the nearest business day. Thus, make a conditional that checks if the requested date is different than the actual date, or find a way to check for business dates instead of weekdays in the loop below

        stock_data = pandas.read_json(requestResponse.content)
        return stock_data

    #get data
    ticker_data = [get_ticker_data()]

    #set next date range
    enddate = numpy.busday_offset(startdate, -1, roll="backward").astype(datetime.date)
    startdate = numpy.busday_offset(enddate, -125, roll="forward").astype(datetime.date)

    #get data and add it to list of data
    ticker_data += [get_ticker_data()]

    #reverse data array for correct date ordering
    ticker_data.reverse()

    #join data
    ticker_data = pandas.concat(ticker_data)

    #write as csv file
    pandas.DataFrame.to_csv(ticker_data, stock_data_location + "/" + "5_min" + "/" + ticker_symbol + "_5min_stock_data.csv", index=False)

def get_tradable_ticker_data():
    tickers = get_tradable_tickers()

    start_location = tickers.index[tickers["ticker"] == "AMKR"].tolist()[0]
    tickers = tickers[tickers.index > start_location]

    for ticker in tickers["ticker"]:
        get_ticker_data_5_min(ticker)

#frequency is number per hour
'''def get_ticker_data(ticker_symbol, frequency, number_of_datapoints):
    increment = math.floor(10000/(6.5*frequency + 1))
    data_points_left = number_of_datapoints

    #get ticker data for the enddate and startdate
    def get_ticker_data():
        headers = {
            'Content-Type': 'application/json'
        }

        url = "https://api.tiingo.com/iex/" + ticker_symbol + "/prices?" + "resampleFreq=5min&columns=open,high,low,close,volume&token=bab507258bcd54db87fb178ad1be94a45fddf0d2&startDate=" + startdate.strftime("%Y-%m-%d") + "&endDate=" + enddate.strftime("%Y-%m-%d")
        requestResponse = requests.get(url, headers=headers)

        #because of holidays, if you request data for a holiday, it will return the data of the nearest business day. Thus, make a conditional that checks if the requested date is different than the actual date, or find a way to check for business dates instead of weekdays in the loop below

        stock_data = pandas.read_json(requestResponse.content)
        return stock_data

    # date range for first data set
    enddate = numpy.busday_offset(datetime.date.today(), 0, roll="backward").astype(datetime.date)
    startdate = numpy.busday_offset(enddate, -(increment - 1), roll="forward").astype(datetime.date)

    # get data
    ticker_data = [get_ticker_data()]

    while data_points_left > 10000:
        enddate = numpy.busday_offset(startdate, -1, roll="backward").astype(datetime.date)
        startdate = numpy.busday_offset(enddate, -increment, roll="forward").astype(datetime.date)

        # get data and add it to list of data
        ticker_data += [get_ticker_data()]

        data_points_left -= 10000

    if data_points_left > 0:
        enddate = numpy.busday_offset(startdate, -1, roll="backward").astype(datetime.date)
        startdate = numpy.busday_offset(enddate, -(increment * (data_points_left / 10000)), roll="forward").astype(datetime.date)

        # get data and add it to list of data
        ticker_data += [get_ticker_data()]

    #reverse data array for correct date ordering
    ticker_data.reverse()

    #join data
    ticker_data = pandas.concat(ticker_data)

    #write as cav file
    pandas.DataFrame.to_csv(ticker_data, stock_data_location + "/" + the_frequency + "/" + ticker_symbol + the_frequency + "_stock_data.csv", index=False)'''

def get_read_tickers():
    return pandas.read_csv(stock_data_location + "/read_tickers.csv")

#Reformat Data for Statistical Analysis
def fit_day_5_min(ticker_symbol):
    ticker_data = get_ticker_data_5_min(ticker_symbol)

    def get_open_line(day_data):
        volatility = day_data[1]["high"] - day_data[1]["low"]
        change = day_data[1]["close"] - day_data[1]["open"]

    #columns
    dates = ticker_data["date"].unique()








#EOD Data

#this should belong in the "extract statistics" file (create one)
def organize_eod_data():
    #get list of files in directory
    files = os.listdir(read_path)
    data = None

    number_of_days = len(files)

    #get and combine data
    for file in files:
        if data is not None:
            new_data = pandas.read_csv(read_path + "/" + file, header = None)
            data = pandas.concat([data, new_data])
        else:
            data = pandas.read_csv(read_path + "/" + file, header = None)

    #set the header
    data.columns = ["ticker", "timestamp", "open", "high", "low", "close", "volume"]

    #make new columns based on timestamp
    datetime_dates = pandas.DatetimeIndex([datetime.datetime.strptime(e, "%d-%b-%Y %H:%M") for e in data["timestamp"]])
    data["day"] = datetime_dates.astype(numpy.int64) // (10**9 * 3600 * 24)
    data["minute"] = (datetime_dates.hour - 9) * 60 + (datetime_dates.minute - 30)
    data["day_timestamp"] = datetime_dates.date
    data["is_weeks_first"] = datetime_dates.weekday == 0
    data["is_weeks_end"] = datetime_dates.weekday == 4

    #remove times earlier than 9:30 and later than 16:00
    data = data[numpy.logical_and(data["minute"] >= 0, data["minute"] <= 390)]

    #create dataset for daily data
    day_data = data[["ticker", "day_timestamp", "day", "is_weeks_first", "is_weeks_end"]]
    day_data = day_data.drop_duplicates()
    data.__delitem__("is_weeks_first")
    data.__delitem__("is_weeks_end")

    #make file for each day stamp and weither its weeks end or weeks first
    day_only_data = day_data[["day", "is_weeks_first", "is_weeks_end"]].drop_duplicates()
    day_only_data.to_csv(write_path + "/info/day_only_data.csv", index=False)

    #get percentage of data points for the day per how many should be there for each ticker and for each day
    missing_error_margin = data[["ticker", "day", "minute"]].groupby(["ticker", "day"]).count().reset_index()
    missing_error_margin.columns = ["ticker", "day", "count"]
    missing_error_margin["count"] = missing_error_margin["count"] * 1000 // 79 / 1000

    #put it into daily data
    day_data = pandas.merge(missing_error_margin, day_data)
    day_data["count"] = day_data["count"]

    #add open and close to day data
    day_data["open"] = data[["ticker", "day", "open"]].groupby(["ticker", "day"], as_index=False).first()["open"]
    day_data["close"] = data[["ticker", "day", "close"]].groupby(["ticker", "day"], as_index=False).last()["close"]

    #compile missing error margin data for total percent of missing data for all days per ticker
    ticker_info = missing_error_margin[["ticker", "count"]].groupby("ticker").aggregate(["count", "min", "max", "median", "mean", "std"])
    ticker_info = ticker_info["count"].reset_index()
    ticker_info["min"] = ticker_info["min"] * 1000 // 1 / 1000
    ticker_info["max"] = ticker_info["max"] * 1000 // 1 / 1000
    ticker_info["median"] = ticker_info["median"] * 1000 // 1 / 1000
    ticker_info["mean"] = ticker_info["mean"] * 1000 // 1 / 1000
    ticker_info["std"] = ticker_info["std"] * 1000 // 1 / 1000

    #get rid of ones that are out of range and do not appear all the time in every day of the data
    tickers_to_be_kept = ticker_info[numpy.logical_and(ticker_info["count"] == number_of_days, ticker_info["mean"] >= 0.974)]["ticker"]
    tickers_that_might_work = ticker_info[numpy.logical_and(ticker_info["count"] == number_of_days, numpy.logical_and(ticker_info["mean"] < 0.974, ticker_info["mean"] > 0.759))]["ticker"]
    total_tickers = pandas.concat([tickers_that_might_work, tickers_to_be_kept])
    total_tickers = total_tickers.reset_index()
    total_tickers.__delitem__("index")
    data = data[data["ticker"].isin(total_tickers["ticker"])]
    data = data.reset_index()
    data.__delitem__("index")

    #apply this to other DataFrames
    ticker_info = ticker_info[ticker_info["ticker"].isin(total_tickers["ticker"])]

    #write the data
    tickers_to_be_kept.to_csv(write_path + "/info/tickers_to_be_kept.csv", index=False)
    tickers_that_might_work.to_csv(write_path + "/info/tickers_that_might_work.csv", index=False)

    #get the starting price (the first known price in the data) for each stock (don't know what will happen if a stock does not appear in the first day of data)
    temp_data = data[["ticker", "open"]].groupby("ticker").first().reset_index(inplace = False)
    temp_data.columns = ["ticker", "starting_price"]
    ticker_info = ticker_info.merge(temp_data)

    #make array that takes starting price and expands it to "close" column length, then divide the two
    expanded_starting_price = pandas.merge(data["ticker"], ticker_info[["ticker", "starting_price"]]).reset_index()
    data = data.sort_values(["ticker", "day"]).reset_index()
    data.__delitem__("index")
    data["percent_close"] = data["close"] / expanded_starting_price["starting_price"]

    #change, the different between the closes
    data["change"] = data["close"].pct_change()
    data["change"] = data["change"].abs().pow(1 / (data["minute"].diff() / 5)) * (numpy.sign(data["change"]))
    #data["change"] / data["change"].abs()


    # volatility index (average 5 min movement)
    temp_data = data[["ticker", "day", "change"]]
    temp_data["change"] = temp_data["change"].abs()
    ticker_info["volatility_index"] = data[["ticker", "change"]].groupby("ticker").mean().reset_index(inplace=False)["change"]

    # volatility for a given day
    day_data["volatility"] = temp_data.groupby(["ticker", "day"]).mean().reset_index(inplace=False)["change"] / pandas.merge(day_data["ticker"], ticker_info[["ticker", "volatility_index"]])["volatility_index"]

    print(day_data["volatility"])

    #change first values to be close/open - 1
    temp_grouped_data = data[["ticker", "open", "close"]].groupby("ticker")["ticker"].cumcount()
    data.loc[temp_grouped_data == 0, "change"] = data.loc[temp_grouped_data == 0, "close"] / data.loc[temp_grouped_data == 0, "open"] - 1

    #take the rest of the NAN values (which were 0's) and make them 0
    data["change"] = data["change"].fillna(0)

    #volatility index (1 point = average percentage movement for a given  time interval)
    #temp_data = data[["ticker", "change"]]
    #temp_data["change"] = temp_data["change"].abs()
    #temp_data.columns = ["ticker", "movement_index"]
    #ticker_info = ticker_info.merge(temp_data.groupby("ticker").mean().reset_index(inplace=False))
    temp_data = day_data[["ticker", "open", "close"]]
    temp_data["movement_index"] = ((temp_data["close"] - temp_data["open"]) / temp_data["close"]).abs() #is the difference, but naming it movement_index so I don't have to rename it in ticker_info
    ticker_info = ticker_info.merge(temp_data[["ticker", "movement_index"]].groupby("ticker").mean().reset_index(inplace=False))

    #apply volatility to data
    data["movement_index_change"] = data["change"] / pandas.merge(data["ticker"], ticker_info[["ticker", "movement_index"]])["movement_index"]

    #volatility close (each new day has 0 as the open)
    data["movement_close"] = ((data["percent_close"] / (pandas.merge(data[["ticker", "day"]], data[["ticker", "day", "percent_close"]].groupby(["ticker", "day"]).first().reset_index(inplace=False))["percent_close"])) - 1) / pandas.merge(data["ticker"], ticker_info[["ticker", "movement_index"]])["movement_index"]

    # remove outliers from begining in data compilation
    new_data = data[["ticker", "day", "minute", "movement_close"]].groupby(["ticker", "day"], as_index=False)

    def reject_outliers(data):
        m = 2
        return data[numpy.logical_or((abs(data["movement_close"] - numpy.mean(data["movement_close"])) < m * numpy.std(data["movement_close"])), data["minute"] > 30)]

    conformed_data = pandas.DataFrame(new_data.apply(reject_outliers))
    conformed_data.reset_index(inplace=True)
    conformed_data.__delitem__("level_0")
    conformed_data.__delitem__("level_1")

    #best fit day data
    temp_grouped_data = conformed_data.groupby(["ticker", "day"], as_index=False)

    #account for day before christmas and day before thanksgiving
    #data = data[numpy.logical_and(data["day"] != )]

    def regression(dataframe):
        #in ax^2 + bx + c
        a, b, c, d = numpy.polyfit(dataframe["minute"], dataframe["movement_close"], 3)
        return [a, b, c, d]

    temp_grouped_data = pandas.DataFrame(temp_grouped_data.apply(regression))
    temp_grouped_data.reset_index(inplace=True)
    temp_grouped_data[["a", "b", "c", "d"]] = pandas.DataFrame(temp_grouped_data[0].to_list(), index=temp_grouped_data.index)
    temp_grouped_data.__delitem__(0)

    #merge data
    day_data = day_data.merge(temp_grouped_data)

    #difference between the intercept value and the open
    #day_data["open_intercept_difference"] = (day_data["c"] * pandas.merge(day_data[["ticker", "day"], ticker_info["movement_index"]]).reset_index(inplace=False)["movement_index"] * pandas.merge(day_data[["ticker", "day"], ticker_info["starting_price"]]).reset_index(inplace=False)["starting_price"]) - day_data["open"]
    #starting percentage

    #write
    day_data.to_csv(write_path + "/info/day_data.csv", index=False)
    ticker_info.to_csv(write_path + "/info/ticker_info.csv", index=False)

    for ticker in total_tickers["ticker"]:
        data[data["ticker"] == ticker].to_csv(write_path + "/" + ticker + "_5_min.csv", index=False)

    #check if best fit matches day

def plot_day_data(ticker, day, derivative = False):
    data = pandas.read_csv(write_path + "/" + ticker + "_5_min.csv")
    day_data = pandas.read_csv(write_path + "/info/day_data.csv")
    new_day_data = day_data[numpy.logical_and(day_data["ticker"] == ticker, day_data["day"] == day)].reset_index()
    new_data = data[numpy.logical_and(data["ticker"] == ticker, data["day"] == day)]
    figure = plot.figure()
    #print(new_day_data["a"].loc[0], " ", new_day_data["b"].loc[0], " ", new_day_data["c"].loc[0], " ", new_day_data["d"].loc[0])
    x_equation = numpy.linspace(0, 390, 79)
    y_equation = x_equation*x_equation*x_equation*new_day_data["a"].loc[0] + x_equation*x_equation*new_day_data["b"].loc[0] + x_equation*new_day_data["c"].loc[0] + new_day_data["d"].loc[0]

    if derivative:
        plot.subplot(1, 2, 1)
    plot.plot(new_data["minute"], new_data["movement_close"], 'o', color="black")
    plot.plot(x_equation, y_equation, color="blue")
    plot.title(ticker + " day " + str(day))

    def intercept_points(a, b, c):
        # is it possible for there to be errors here in determining the values. for example, a aprox 0 but did not meet the cutoff earlier?
        intercept_one_ = None
        intercept_two_ = None
        if ((2 * b) ** 2 - 4 * (3 * a) * c) >= 0:
            intercept_one = (-(2 * b) - math.sqrt((2 * b) ** 2 - 4 * (3 * a) * c)) / (2 * (3 * a))
            intercept_two = (-(2 * b) + math.sqrt((2 * b) ** 2 - 4 * (3 * a) * c)) / (2 * (3 * a))
            intercept_one_ = min(intercept_one, intercept_two)
            intercept_two_ = max(intercept_one, intercept_two)
        return [intercept_one_, intercept_two_]

    intercept_one, intercept_two = intercept_points(new_day_data["a"].loc[0], new_day_data["b"].loc[0],
                                                    new_day_data["c"].loc[0])  # new_day_data["c"].loc[0]
    # print(intercept_one, " ", intercept_two)

    if derivative:
        y_equation_prime = 3 * x_equation * x_equation * new_day_data["a"].loc[0] + 2 * x_equation * \
                           new_day_data["b"].loc[0] + new_day_data["c"].loc[0]
        plot.subplot(1, 2, 2)
        plot.plot(x_equation, y_equation_prime, color="blue")
        plot.ylim(-0.04, 0.04)
        plot.plot(x_equation, numpy.full(79, 0), color="black")

    plot.show()

def plot_equation(a, b, c, d):
    x_equation = numpy.linspace(0, 390, 79)
    y_equation = x_equation * x_equation * x_equation * a + x_equation * x_equation * b + x_equation * c + d
    plot.plot(x_equation, y_equation, color="blue")
    plot.title("an equation")
    plot.show()

def organize_by_type_of_day(day_data):
    #gonna have to add the .loc to everything
    #adapt to allow for approximatly 0
    '''def procedure(equation):
        if equation["a"] == 0:
            #other stuff
            if -0.000005 <= equation["b"] <= 0.000005:
                #straight line, mx+b
            if -0.0005 <= equation["c"] <= 0.0005:
                #b is not 0, so just a up facing quadradic
            #just c and b can be a dip
            #if c is positive and b is negitive
                #if the maxiumum (or intercept) is close to the middle
                    #its a upsidedown u
                # if the maxiumum (or intercept) is close to the end
                    # its a half upsidedown u
            # if c is negitive and b is positive
                # if the maxiumum (or intercept) is close to the middle
                    # its a full u
                # if the maxiumum (or intercept) is close to the end
                    # its a half u
        if equation["b"] == 0:
            if equation["c"] == 0:
                #everything but a is 0,
                #if a is > 0
                    #its a strong upward facing loop (could be grouped with the strong upward b too)
                #if a is < 0
                    # its a strong downward facing loop (could be grouped with the strong downward b too)

            #just c and a is a dip, but being its more a than c, this suggests there is more of a tailing at the end or a slow buildup at the beginning. a and c must be differet signs
            #look into if a is too strong
        if equation["c"] == 0:
            #a and b are not 0, very interesting senario here. Depending on where the peak is, it represent either more of a straight line or a falling-line
            #if the peak point is before ___(probably around an 1/8th, just have to see how much it can fall off at certain points)th from the end, its a falling line
            #else, its a straight line
        #sin wave aprox, can subcategorize from here as up trending wave or what not.
        if numpy.sign(equation["a"]) != numpy.sign(equation["b"]) and numpy.sign(equation["a"]) == numpy.sign(equation["c"]):
            #depending on where the intercepts are, it determines what sub category it is. As long as the derivitive is a full, symmetric quadtratic (requireing properly apposing signs).
            def intercept_points(a, b, c):
                #is it possible for there to be errors here in determining the values. for example, a aprox 0 but did not meet the cutoff earlier?
                intercept_one = (-(2*b) - math.sqrt((2*b)**2 - 4*(3*a)*c))/(2*(3*a))
                intercept_two = (-(2*b) + math.sqrt((2*b)**2 - 4*(3*a)*c))/(2*(3*a))
                return [intercept_one, intercept_two]
            #if intercept is somewhere around 1/3 1/3 1/3 range
                #its a regular sin wave
            #if intercept is more towards the ends (or far away from eachother, this allows for the center of the wave to be off center by a margin)
                #its a downward going wave
            #if intercept is more towards the center (or close to eachother, this allows for the center of the wave to be off center by a margin)
                #its a upward going wave'''

        #DONT FORGET ABOUT D

        #less than a differential of __% than the maxiumum change in value (remove d for this calculation) (for most, it will be at 390)
        #first step, identify the waves and remove those from the data set
    def wave_procedure(ticker, day, a, b, c, d):
        if a != 0 and numpy.sign(a) != numpy.sign(b) and numpy.sign(a) == numpy.sign(c) and (2*b)**2 - 4*(3*a)*c >= 0:
            #depending on where the intercepts are, it determines what sub category it is. As long as the derivitive is a full, symmetric quadtratic (requireing properly apposing signs).
            def within_range(value, percent, expected_value):
                return (abs(expected_value - value) / expected_value) <= percent

            def value_at_a_point(x):
                return a*x**3 + b*x**2 + c*x + d

            def intercept_points():
                #is it possible for there to be errors here in determining the values. for example, a aprox 0 but did not meet the cutoff earlier?
                intercept_one = (-(2*b) - math.sqrt((2*b)**2 - 4*(3*a)*c))/(2*(3*a))
                intercept_two = (-(2*b) + math.sqrt((2*b)**2 - 4*(3*a)*c))/(2*(3*a))
                intercept_one_ = min(intercept_one, intercept_two)
                intercept_two_ = max(intercept_one, intercept_two)
                return [intercept_one_, intercept_two_]
            intercept_one, intercept_two = intercept_points()

            def max_min_difference(intercept_one, intercept_two):
                value_at_end = value_at_a_point(390)
                value_at_beginning = value_at_a_point(0)
                min_ = min(value_at_end, intercept_one, intercept_two, value_at_beginning)
                max_ = max(value_at_end, intercept_one, intercept_two, value_at_beginning)
                return max_ - min_

            #if intercept is somewhere around 1/4 1/2 1/4, withing +- 5% of that

            if max_min_difference(intercept_one, intercept_two) < 0.5:
                # plot_day_data(ticker, day)
                # flat, change 0.5 to a working number
                return True

            if intercept_one >= 0 and intercept_two <= 390:
                #plot_day_data(ticker, day)
                if within_range(intercept_one, 0.15, 97.5) and within_range(intercept_two, 0.15, 292.5): #or intercept_one > 50 and intercept 2 < 3__ and the values at the beginging and end are pretty equal
                    #it's a sin wave
                    #print("1 ", ticker, " ", day)
                    #plot_day_data(ticker, day)
                    return True

                    #its a regular sin wave
                #if intercept is more towards the ends (or far away from eachother, this allows for the center of the wave to be off center by a margin)
                #if the points are equally away from the ends and more towards the end
                #if within_range(intercept_one, 0.15, 390 - intercept_two):
                if abs(intercept_one - (390 - intercept_two)) < 35: #and if the intercepts are not to close to the edges
                    if intercept_one > 50: #and intercept_two > xxx
                        if (numpy.sign(c) == 1 and intercept_one > 1.15 * 97.5) or (numpy.sign(c) == -1 and intercept_one < 0.85 * 97.5):
                            print("2 ", ticker, " ", day, " intercept_one:", intercept_one, " intercept_two:", intercept_two)
                            #plot_day_data(ticker, day)
                            #its a upward going wave
                            #print("2 ", ticker, " ", day)
                            #this seems to work well, make a minumum away from 0 it can be
                            return True

                        if (numpy.sign(c) == -1 and intercept_one > 1.15 * 97.5) or (numpy.sign(c) == 1 and intercept_one < 0.85 * 97.5):
                            # its a downward going wave
                            print("3 ", ticker, " ", day, " intercept_one:", intercept_one, " intercept_two:", intercept_two)
                            #plot_day_data(ticker, day)
                            return True
                    else:
                        #more of a straight line
                        print("4 ", ticker, " ", day)
                        #plot_day_data(ticker, day)
                        #if the slope is more closley flat, its a flat line (if the overall change of the day is not sufficient)
                            #flat line
                            #add elif to the bottom
                        if max_min_difference(intercept_one, intercept_two) < 0.5:
                            #plot_day_data(ticker, day)
                            #flat, change 0.5 to a working number
                            return True
                        if (numpy.sign(b) == -1):
                            #downward wave
                            return True
                        elif (numpy.sign(b) == 1):
                            return True
                        else:
                            #flat line
                            return True
                #if (within_range(intercept_one, 0.1 ,165) and intercept_two >= 360) or (within_range(intercept_two, 0.1 ,225) and intercept_one <= 30):
                    #quadratic alike
                #    print("5 ", ticker, " ", day)
                    #plot_day_data(ticker, day)
                 #   return True
                #left shifted quadratic, right shifted quadratic
                plot_day_data(ticker, day)
                #work on indentifying quadtratics
                #identify quadratics with flat endings
                #identify starting flat and upward trend
            #if intercept is more towards the center (or close to eachother, this allows for the center of the wave to be off center by a margin)
                #its a upward going wave

            #what about the over waves that are more lopsided
        return False
        #if a and b are the same sign, then it acts as ___

    #eliminate ones that more of a straight line than an actual wave

    clean_day_data = day_data[["ticker", "day", "a", "b", "c", "d"]]
    #return clean_day_data.apply(wave_procedure)
    return pandas.DataFrame([wave_procedure(*r) for r in clean_day_data.values])

points = []

def organize_by_type_of_day_two(day_data):
    def wave_procedure(ticker, day, a, b, c, d):
        def within_range(value, percent, expected_value):
            return (abs(expected_value - value) / expected_value) <= percent

        def value_at_a_point(x):
            return a*x**3 + b*x**2 + c*x + d

        def value_at_a_point_prime(x, with_c = False):
            if x is None:
                return None
            elif with_c:
                return 3*a*x**2 + 2*b*x + c*x
            return 3*a*(x**2) + 2*b*x

        def get_change_point():
            if a == 0:
                return None

            point = -2*b / (6*a)

            return point
            #if 0 < point < 390:
            #    return point
            #return None

        def intercept_points_prime(with_c = False):
            #is it possible for there to be errors here in determining the values. for example, a aprox 0 but did not meet the cutoff earlier?
            intercept_one_ = float("-inf")
            intercept_two_ = float("inf")

            if a == 0:
                return [intercept_one_, intercept_two_]

            if with_c:
                if ((2*b)**2 - 4*(3*a)*c) >= 0:
                    intercept_one = (-(2*b) - math.sqrt((2*b)**2 - 4*(3*a)*c))/(2*(3*a))
                    intercept_two = (-(2*b) + math.sqrt((2*b)**2 - 4*(3*a)*c))/(2*(3*a))
                    intercept_one_ = numpy.min([intercept_one, intercept_two])
                    intercept_two_ = numpy.max([intercept_one, intercept_two])
                return [intercept_one_, intercept_two_]

            intercept_one = (-(2 * b) - math.sqrt((2 * b) ** 2)) / (2 * (3 * a))
            intercept_two = (-(2 * b) + math.sqrt((2 * b) ** 2)) / (2 * (3 * a))
            intercept_one_ = numpy.min([intercept_one, intercept_two])
            intercept_two_ = numpy.max([intercept_one, intercept_two])
            return [intercept_one_, intercept_two_]

        def intercept_points():
            #is it possible for there to be errors here in determining the values. for example, a aprox 0 but did not meet the cutoff earlier?
            intercept_one_ = None
            intercept_two_ = None

            intercept_one = (-(b) - math.sqrt((b)**2 - 4*(a)*c))/(2*(a))
            intercept_two = (-(b) + math.sqrt((b)**2 - 4*(a)*c))/(2*(a))
            intercept_one_ = numpy.min([intercept_one, intercept_two])
            intercept_two_ = numpy.max([intercept_one, intercept_two])
            return [intercept_one_, intercept_two_]

        intercept_one, intercept_two = intercept_points_prime(with_c = True)

        def max_min_difference_prime():
            value_at_end = value_at_a_point_prime(390)
            value_at_beginning = value_at_a_point_prime(0)
            change_point_ = change_point()

            if change_point_ is None or  change_point_ <= 0 or change_point_ >= 390:
                min_ = min(value_at_end, value_at_beginning)
                max_ = max(value_at_end, value_at_beginning)
                return max_ - min_

            min_ = min(value_at_end, value_at_a_point_prime(change_point_), value_at_beginning)
            max_ = max(value_at_end, value_at_a_point_prime(change_point_), value_at_beginning)
            return max_ - min_

        def max_min_difference():
            value_at_end = value_at_a_point(390)
            value_at_beginning = value_at_a_point(0)
            value_at_intercept_one = value_at_a_point(intercept_one)
            value_at_intercept_two = value_at_a_point(intercept_two)

            if intercept_one < 0 or intercept_one > 390:
                value_at_intercept_one = value_at_beginning

            if intercept_two < 0 or intercept_two > 390:
                value_at_intercept_two = value_at_end

            min_ = min(value_at_end, value_at_intercept_one, value_at_intercept_two, value_at_beginning)
            max_ = max(value_at_end, value_at_intercept_one, value_at_intercept_two, value_at_beginning)
            return max_ - min_

        #E's are a measure of possible error, small e's indicate a low chance of error

        #1) get rid of flat lines/very small changes
        difference = max_min_difference()

        if difference < 0.2:
            #plot_day_data(ticker, day, True)
            return True

        #2) get rid of any intensly changing equations


        #3) group/seperate by number of intercepts
        #intercepts without c:
        intercept_one_, intercept_two_ = intercept_points_prime()

        number_of_intercepts = 2

        if intercept_one <= 0 or intercept_one >= 390:
            number_of_intercepts -= 1

        if intercept_two <= 0 or intercept_two >= 390:
            number_of_intercepts -= 1

        #print(intercept_one, intercept_two, end = ", ")

        # for waves, if the min value (or max if under 0) in a u is close enough to zero, it clasifies as having an intercept at that point, and set the intercept to ___ and number_of_intercepts++ if the min point is not 0 or 390 (must be between) and the min point is close and there is a big enough differenc ebetwen the min and max value.
        if number_of_intercepts == 0 :#and if a is significant
            possible_intercept = -1 * b / (2 * a)
            min_or_max_value = value_at_a_point_prime(possible_intercept)

            if 0 <= possible_intercept <= 390 and numpy.abs(min_or_max_value) < 5:
                number_of_intercepts += 1
                intercept_one = possible_intercept

        #change point?
        change_point = get_change_point()
        start = value_at_a_point(0)
        end = value_at_a_point(390)

        #4) start analyzing

        if number_of_intercepts == 0:
            #plot_day_data(ticker, day, True)

            if 0 < intercept_one < 390 and 0 < intercept_two < 390:

            #if a is near 0: #PICK NUMBEr
                if -2e-5 <= 2*b <= 2e-5: #analyize more if it should be +-2e-5 or less
                    #the slope is not significant
                    if (c > 0): #b or c?
                        #positive line
                        return True
                    else:
                        #negitive line
                        return True

        #4a) classify all waves using change_point
        if change_point != None:
            #plot_equation(a, b, c, d)
            print(change_point)
            plot_day_data(ticker, day, True)
        if change_point != None:
            if number_of_intercepts == 1:
                if 125 < change_point < 255: #CHANGE NUMBERS

                    if change_point < 160:
                        plot_equation(a, b, c, d)

                    global points
                    points += [change_point]
                    #a full u, analize intercepts to see difference between tailing/lipped u's and full symmetrical u's are
                    if c > 0:
                        #upsidedown u
                        return True
                    else:
                        #upright u
                        return True
                elif change_point > -25 or change_point < 415:#else if change_point is near the boundaries, then half a u
                    is_upright = False
                    is_right = False
                    if value_at_a_point(change_point) < end:
                        is_upright = True
                    if 190 - change_point > 0:
                        is_right = True

                    if is_upright and is_right:
                        # upward facing right u
                        return True
                    elif is_upright and not is_right:
                        # high starting, decreasing asmytotal slope.
                        return True
                    elif not is_upright and is_right:
                        # right upsidedown u
                        return True
                    else:
                        # low starting rising asymtotal slope.
                        return True
            #work on seperating rising u's, normal u's, and dracstically decreasing u's. Same goes for half u's

        '''if number_of_intercepts == 0:
            #plot_day_data(ticker, day, True)

            if 0 < intercept_one < 390 and 0 < intercept_two < 390:

            #if a is near 0: #PICK NUMBEr
                #already got rid of lines
                    #we got rid of the flat lines in part 1), so no need to look for c aprox. 0
                    #E possible point for breakthough if part 1 does not get all the flat lines
                else:
                    #the slope is significant, now dealing with bx+c
                    if b > 0:
                        #positive quadratic increase (half a u)
                        return True
                    else:
                        #negitive quadratic increase (half a upsidedown u)
                        return True
                    return True

            #else, a is significant

            #print(2*b, end = ", ")

        return False'''
    #eliminate ones that more of a straight line than an actual wave

    clean_day_data = day_data[["ticker", "day", "a", "b", "c", "d"]]

    #return clean_day_data.apply(wave_procedure)
    return pandas.DataFrame([wave_procedure(*r) for r in clean_day_data.values])

#"https://query1.finance.yahoo.com/v7/finance/download/" + ticker + "?period1=1564617600&period2=1588809600&interval=1d&events=history"

def organize_by_type_of_day_three(day_data):
    def wave_procedure(ticker, day, a, b, c, d):
        def within_range(value, percent, expected_value):
            return (abs(expected_value - value) / expected_value) <= percent

        def value_at_a_point(x):
            return a*x**3 + b*x**2 + c*x + d

        def value_at_a_point_prime(x, with_c = False):
            if x is None:
                return None
            elif with_c:
                return 3*a*x**2 + 2*b*x + c*x
            return 3*a*(x**2) + 2*b*x

        def get_change_point():
            if a == 0:
                return None

            point = -2*b / (6*a)

            return point
            #if 0 < point < 390:
            #    return point
            #return None

        def intercept_points_prime(with_c = False):
            #is it possible for there to be errors here in determining the values. for example, a aprox 0 but did not meet the cutoff earlier?
            intercept_one_ = None
            intercept_two_ = None

            if a == 0:
                intercept_one_ = (-1 * b) / (2 * a)
                return [intercept_one_, intercept_two_]

            if with_c:
                if ((2*b)**2 - 4*(3*a)*c) >= 0:
                    intercept_one = (-(2*b) - math.sqrt((2*b)**2 - 4*(3*a)*c))/(2*(3*a))
                    intercept_two = (-(2*b) + math.sqrt((2*b)**2 - 4*(3*a)*c))/(2*(3*a))
                    intercept_one_ = numpy.min([intercept_one, intercept_two])
                    intercept_two_ = numpy.max([intercept_one, intercept_two])
                return [intercept_one_, intercept_two_]

            intercept_one = (-(2 * b) - math.sqrt((2 * b) ** 2)) / (2 * (3 * a))
            intercept_two = (-(2 * b) + math.sqrt((2 * b) ** 2)) / (2 * (3 * a))
            intercept_one_ = numpy.min([intercept_one, intercept_two])
            intercept_two_ = numpy.max([intercept_one, intercept_two])
            return [intercept_one_, intercept_two_]

        def intercept_points():
            #is it possible for there to be errors here in determining the values. for example, a aprox 0 but did not meet the cutoff earlier?
            intercept_one_ = None
            intercept_two_ = None

            intercept_one = (-(b) - math.sqrt((b)**2 - 4*(a)*c))/(2*(a))
            intercept_two = (-(b) + math.sqrt((b)**2 - 4*(a)*c))/(2*(a))
            intercept_one_ = numpy.min([intercept_one, intercept_two])
            intercept_two_ = numpy.max([intercept_one, intercept_two])
            return [intercept_one_, intercept_two_]

        intercept_one, intercept_two = intercept_points_prime(with_c = True)

        def max_min_difference_prime():
            value_at_end = value_at_a_point_prime(390)
            value_at_beginning = value_at_a_point_prime(0)
            change_point_ = get_change_point()

            if change_point_ is None or  change_point_ <= 0 or change_point_ >= 390:
                min_ = min(value_at_end, value_at_beginning)
                max_ = max(value_at_end, value_at_beginning)
                return max_ - min_

            min_ = min(value_at_end, value_at_a_point_prime(change_point_), value_at_beginning)
            max_ = max(value_at_end, value_at_a_point_prime(change_point_), value_at_beginning)
            return max_ - min_

        def max_min_difference():
            value_at_end = value_at_a_point(390)
            value_at_beginning = value_at_a_point(0)
            value_at_intercept_one = value_at_a_point(intercept_one)
            value_at_intercept_two = value_at_a_point(intercept_two)

            if intercept_one < 0 or intercept_one > 390:
                value_at_intercept_one = value_at_beginning

            if intercept_two < 0 or intercept_two > 390:
                value_at_intercept_two = value_at_end

            min_ = min(value_at_end, value_at_intercept_one, value_at_intercept_two, value_at_beginning)
            max_ = max(value_at_end, value_at_intercept_one, value_at_intercept_two, value_at_beginning)
            return max_ - min_

        #consider eliminating points and put that towards an open.

        #in the range of 0 to 390, what is the start, min, max, and end value
        start = value_at_a_point(0)
        end = value_at_a_point(390)

        def plot_data(highlighted_points):
            x_equation = numpy.linspace(0, 390, 79)
            y_equation = x_equation * x_equation * x_equation * a + x_equation * x_equation * b + x_equation * c + d
            plot.plot(x_equation, y_equation, color="black")

            x_points = [0, 390]
            for e in highlighted_points:
                if e != None:
                    x_points += [e]

            x_points = numpy.array(x_points)
            y_points = numpy.array([value_at_a_point(e) for e in x_points])
            plot.plot(x_points, y_points, 'o', color="blue")

            plot.title("an equation")
            plot.show()

        def get_min_and_max():
            #a line, no min or max value
            if intercept_one == None:
                if intercept_two == None:
                    return[None, None]
                return[intercept_two, None]

            if intercept_two == None:
                value_at_intercept_one = value_at_a_point(intercept_one)
                if value_at_intercept_one == start or value_at_intercept_one == end:
                    return [None, None]
                return [value_at_intercept_one, None]

            value_at_intercept_one = value_at_a_point(intercept_one)
            value_at_intercept_two = value_at_a_point(intercept_two)

            if value_at_intercept_one == start or value_at_intercept_one == end or intercept_one < 0 or intercept_one > 390:
                value_at_intercept_one = None
            if value_at_intercept_two == start or value_at_intercept_two == end or intercept_two < 0 or intercept_two > 390:
                value_at_intercept_two = None

            if value_at_intercept_one != None and value_at_intercept_two != None:
                if value_at_intercept_one < value_at_intercept_two:
                    return [intercept_one, intercept_two]
                return [intercept_two, intercept_one]
            elif value_at_intercept_one == None and value_at_intercept_two != None:
                return [intercept_two, None]
            elif value_at_intercept_one != None and value_at_intercept_two == None:
                return [intercept_one, None]
            elif value_at_intercept_one == None and value_at_intercept_two == None:
                return [None, None]

        min, max = get_min_and_max()
        value_at_min = None
        value_at_max = None

        if min is not None:
            value_at_min = value_at_a_point(min)
        if max is not None:
            value_at_max = value_at_a_point(max)

        #we can know if it goes back down after the end (or back up, just a change in movement again) if there is an intercept after the end), the same goes for the start

        #what if the intercept is wayyyy out, and that wouldn't really make a difference

        #plot_data([min, max])

        return [ticker, day, intercept_one, intercept_two, value_at_min, value_at_max, start, min, max, end]

    clean_day_data = day_data[["ticker", "day", "a", "b", "c", "d"]]

    # return clean_day_data.apply(wave_procedure)
    return pandas.DataFrame([wave_procedure(*r) for r in clean_day_data.values])

def graph_points(title = "some points"):
    x = numpy.full(len(points), 0)
    y = numpy.array(points)
    plot.plot(y, x, 'o', color="blue")
    plot.title(title)
    plot.show()

#Run
#organize_eod_data()
#plot_day_data("AAON", 18116)

#add confidince index (approximation / std / accuracy) for each "best day fit", names preferibly volatility index (or develop volatility index, and the conficence index is the inverse of it)

#should movement index be difference between high and low? (obviously dividec by the low)

#what if we rounded off each of the a, b, and c's into groups, and looked for the most common one's?

#rerun the eod data and check the volatility column in the day_data towards the bottom