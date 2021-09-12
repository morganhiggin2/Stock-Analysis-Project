from get_data import *
from analyze_data import *

#main file (where I would run the function from the get_data.py file to get it to do what I want (ex. get the data, organize it))

def equation_grouping_analysis():
    data = pandas.read_csv(write_path + "/info/day_data.csv")
    data = data[["ticker", "day", "a", "b", "c", "d"]]

    #just a b and c for now

    print("a:, mean:", data["a"].mean(), " std:", data["a"].std(), " median:", data["a"].median(), " max:", data["a"].max(), " min:", data["a"].min())
    print("b:, mean:", data["b"].mean(), " std:", data["b"].std(), " median:", data["b"].median(), " max:", data["b"].max(), " min:", data["b"].min())
    print("c:, mean:", data["c"].mean(), " std:", data["c"].std(), " median:", data["c"].median(), " max:", data["c"].max(), " min:", data["c"].min())

    #plot.plot(data['d'], numpy.linspace(0, len(data['a']) - 1, len(data['a'])), 'o')
    #plot.xlabel("b")
    #plot.ylabel("c")
    figure = plot.figure()
    ax = figure.add_subplot(111, projection='3d')

    ax.scatter(data["a"], data["b"], data["c"], marker='o')

    ax.set_xlabel('a')
    ax.set_ylabel('b')
    ax.set_zlabel('c')

    plot.show()

#equation_grouping_analysis()
'''day_data = pandas.read_csv(write_path + "/info/day_data.csv")
a = organize_by_type_of_day_three(day_data).reset_index(inplace=False)
a.__delitem__("index")
a.columns = ["ticker", "day", "intercept_one", "intercept_two", "value_at_min", "value_at_max", "start", "min", "max", "end"]
new_day_data = pandas.merge(day_data, a)
new_day_data.to_csv(write_path + "/info/new_day_data.csv")'''

#lets analyize the day_data
new_day_data = pandas.read_csv(write_path + "/info/new_day_data.csv")
name_of_column_one = "value_at_min"
name_of_column_two = "max"
new_table = new_day_data[[name_of_column_one, name_of_column_two]]
new_table.dropna()

def plot_two_values(values1, values2, x_label, y_label):
    plot.plot(values1, values2, 'o', color="blue")
    plot.xlabel(x_label)
    plot.ylabel(y_label)
    plot.show()

plot_two_values(new_table[name_of_column_one], new_table[name_of_column_two], name_of_column_one, name_of_column_two)
analyze_intercepts(2, 0)
#make a new table with two columsn
#drop na columns

#a = numpy.invert(organize_by_type_of_day(day_data))
#left_over = day_data[a[0]].dropna()

#[plot_day_data(*r, True) for r in day_data[["ticker", "day"]].values]

#print(day_data[a[0]].dropna())

#plot_day_data("AAXJ", 18117, True)





