import numpy
import pandas
import matplotlib.pyplot as plot

read_path = "C:/Users/morga/Documents/Stock Data/data/5_min_test"
write_path = "C:/Users/morga/Documents/Stock Data/5_min"

def analyze_intercepts(num_of_intercepts, difference_distance):
    new_day_data = pandas.read_csv(write_path + "/info/new_day_data.csv")
    filtered_data = new_day_data[["min", "max", "intercept_one", "intercept_two"]]
    filtered_data["number_of_intercepts"] = 2 - filtered_data[["intercept_one", "intercept_two"]].isnull().sum()

    if num_of_intercepts == 2:
        filtered_data.dropna()
        filtered_data["intercept_one"] = numpy.where(
            numpy.logical_and(filtered_data["intercept_one"] <= 390, filtered_data["intercept_one"] >= 0),
            filtered_data["intercept_one"], numpy.nan)
        filtered_data["intercept_two"] = numpy.where(
            numpy.logical_and(filtered_data["intercept_two"] <= 390, filtered_data["intercept_two"] >= 0),
            filtered_data["intercept_two"], numpy.nan)

        filtered_data["difference"] = filtered_data["intercept_two"] - filtered_data["intercept_one"]
        filtered_data.dropna()
        x = numpy.arange(0, 390, 10)
        plot.plot(x, -x + 195, 'r', color = "red")
        plot_data(filtered_data["difference"], filtered_data["intercept_one"], "difference", "intercept_one", "difference versus intercept_one")
        return
    '''filtered_data["final_intercept"] = numpy.where(filtered_data["intercept_one"].isna() == False, filtered_data["intercept_one"], numpy.nan)
    filtered_data["final_intercept"] = numpy.where(numpy.logical_or(filtered_data["final_intercept"].isna() == True, filtered_data["intercept_two"].isna() == False), filtered_data["intercept_two"], filtered_data["final_intercept"])
    filtered_data["final_intercept"] = numpy.where(numpy.logical_and(filtered_data["final_intercept"] <= 390, filtered_data["final_intercept"] >= 0), filtered_data["final_intercept"], numpy.nan)
    filtered_data["final_intercept"] = numpy.where(filtered_data["max"] == filtered_data["final_intercept"], filtered_data["final_intercept"], numpy.nan)
    filtered_data.dropna()'''
    plot_data(filtered_data["final_intercept"], numpy.full(filtered_data.__len__(), 0), "intercept", "", "one_intercept")

def plot_data(x, y, x_label, y_label, title):
    plot.plot(x, y, 'o', color="blue")
    plot.title(title)
    plot.xlabel(x_label)
    plot.ylabel(y_label)
    plot.show()