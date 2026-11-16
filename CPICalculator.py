import numpy as np                 # for the annual rate math
import pandas as pd                # to read and work with the csv data
import matplotlib.pyplot as plt    # for the graph

# the csv is in the same folder as this file, and the graph gets saved there too
DATA_FILE = "STATIC_INFLATIONCALC.csv"
GRAPH_FILE = "CPI_Graph.png"

# month names so the results say "September 2000" instead of "9/2000"
MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']


# This class holds the CPI data and does the graph + the calculations
class CPICalculator:

    def __init__(self, filename):
        # we skip the first 8 lines of the bank of canada since they're just info
        self.df = pd.read_csv(filename, skiprows=8)

        # renaming the columns for ease of use
        self.df.columns = ['Date', 'CPI']

        # we have to format dates from text to  real dates so matplotlib can use them
        self.df['Date'] = pd.to_datetime(self.df['Date'])

        # pct_change(12) only works if there is one row per month, so i checked the row count with info()
        # 1914-01 to 2026-09 should be 1353 months but there were somehow 1355 rows in total
        # the 2 extra rows are dated april 30 (1927 and 1932), so only keep the rows from the 1st of each month
        self.df = self.df[self.df['Date'].dt.day == 1]

        # make year and month columns so its easy to find a date later
        self.df['Year'] = self.df['Date'].dt.year
        self.df['Month'] = self.df['Date'].dt.month

        # annual % change = this month vs same month last year (12 rows back)
        # the first 12 months will be empty since there is no year before them
        self.df['Annual Change'] = self.df['CPI'].pct_change(12) * 100

    # Draws the CPI and the annual % change on one graph and saves it as a png
    def plot_graph(self, filename):
        fig, ax = plt.subplots(figsize=(12, 6), layout='constrained')

        # CPI on the left side
        ax.plot(self.df['Date'], self.df['CPI'], color='blue', label='CPI')

        # dotted line at the base level (2002 = 100)
        ax.axhline(100, color='black', linestyle=':', label='Base Level (2002 = 100)')

        # second axis on the right side for the annual % change
        # twinx makes a new y axis that shares the same x axis (the dates)
        ax2 = ax.twinx()
        ax2.plot(self.df['Date'], self.df['Annual Change'], color='red', linewidth=0.7, label='Annual % Change')

        # title and axis labels
        ax.set_title('Consumer Price Index (CPI) in Canada', fontsize=16)
        ax.set_xlabel('Year')
        ax.set_ylabel('CPI (2002 = 100)')
        ax2.set_ylabel('Annual Change [%]')

        # legend for each axis (like in class), placed where they dont cover the lines
        # left axis legend shows the CPI and the base level, right one shows the % change
        ax.legend(loc='lower right')
        ax2.legend(loc='upper center')

        # the assignment only asks to save the graph as a png, so im not using a plt.show()
        # that way the calculator starts right away instead of waiting for the window to close
        fig.savefig(filename)

    # Returns the CPI for a year and month, or None if that date isnt in the data
    def get_cpi(self, year, month):
        # filter the data frame for the year and month the user typed
        row = self.df[(self.df['Year'] == year) & (self.df['Month'] == month)]
        if len(row) == 0:
            return None   # date is not in the data
        return row['CPI'].values[0]

    # Does the same calculations as the bank of canada calculator and prints the results
    def calculate(self, price, year1, month1, year2, month2):
        cpi1 = self.get_cpi(year1, month1)
        cpi2 = self.get_cpi(year2, month2)

        # new price = old price x (CPI 2 / CPI 1)
        new_price = price * cpi2 / cpi1

        # change percentage between the old and new price
        percent_change = (new_price - price) / price * 100

        # number of years can have a decimal since we use months too
        # ex. 2000-09 to 2001-03 is 6 months = 0.5 years
        years = ((year2 - year1) * 12 + (month2 - month1)) / 12

        # average annual rate (same as the bank of canada formula)
        # = (CPI 2 / CPI 1) ^ (1 / years) - 1, then x 100 for a percent
        # if both dates are the same month there are 0 years so we cant divide by it
        if years == 0:
            annual_rate = 0
        else:
            annual_rate = (np.power(cpi2 / cpi1, 1 / abs(years)) - 1) * 100

        # turn the month number into its name (month 1 is index 0 in the list)
        date1 = f"{MONTH_NAMES[month1 - 1]} {year1}"
        date2 = f"{MONTH_NAMES[month2 - 1]} {year2}"

        # print everything rounded to 2 decimals, with $ and CAD for the money
        # CPI is shown with 1 decimal like on the website
        print("----------------------------------------")
        print(f"\033[1mA basket costing ${price:,.2f} CAD in {date1} would cost ${new_price:,.2f} CAD in {date2}.\033[0m")
        print("----------------------------------------")
        print(f"CPI for first date ({date1}): {cpi1:.1f}")
        print(f"CPI for second date ({date2}): {cpi2:.1f}")
        print("----------------------------------------")
        print(f"Percent change: {percent_change:.2f}%")
        print(f"Number of years: {years:.2f}")
        print(f"Average annual rate of inflation: {annual_rate:.2f}%")
        print("----------------------------------------")
        


# Asks for the price and keeps asking until the user types a positive number
def ask_price():
    while True:
        try:
            # take out $ and commas first so things like $1,000 still work
            price = float(input("Enter the base price: ").replace('$', '').replace(',', ''))
            if price > 0:
                return price
            print("Price has to be more than 0")
        except ValueError:
            # float() fails if they type letters or leave it blank
            print("Please only enter a number")


# Asks for a date in YYYY-MM format and checks that it is in the data
def ask_date(text, calculator):
    while True:
        try:
            # split 2000-09 into the year and the month
            year, month = input(text).split('-')
            year = int(year)
            month = int(month)
        except ValueError:
            # happens if there is no dash, more than one dash, or it isnt numbers
            print("Wrong format, use YYYY-MM (example 2000-09)")
            continue

        if month < 1 or month > 12:
            print("Month has to be between 1 and 12")
        elif calculator.get_cpi(year, month) is None:
            print("That date is not in the data (1914-01 to 2026-09)")
        else:
            return year, month


# ----- main program -----

# load the data and save the graph first
calculator = CPICalculator(DATA_FILE)
calculator.plot_graph(GRAPH_FILE)

print("----------------------------------------")
print("Welcome to the Advanced Inflation Calculator")
print("Data available is from January 1914 to September 2026")
print("Please follow the following steps to calculate the inflation between the two dates")
print("----------------------------------------")

# get the inputs from the user (the functions above keep asking until they are valid)
price = ask_price()
year1, month1 = ask_date("Enter the first date (YYYY-MM): ", calculator)
year2, month2 = ask_date("Enter the second date (YYYY-MM): ", calculator)

# do the calculation and print the results
calculator.calculate(price, year1, month1, year2, month2)

# let them know where the graph is so they can look at it after
print(f"For more information, the historical CPI graph is saved in the project folder as {GRAPH_FILE}")
