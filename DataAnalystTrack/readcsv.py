import numpy as np
import pandas as pd

class DataShell:

    # Initialize class with self and inputFile
    def __init__(self, inputFile):
        self.file = inputFile

    # Define generate_csv method, with self argument
    def generate_csv(self):
        self.data_as_csv = pd.read_csv(self.file)
        return self.data_as_csv


# Instantiate DataShell with us_life_expectancy as input argument
with open("fp.csv", mode="r") as file:
    data = DataShell(file)
    print(data.generate_csv())


# data_shell = DataShell(us_life_expectancy)

# Call data_shell's generate_csv method, assign it to df
# df = data_shell.generate_csv()

# Print df
# print(df)