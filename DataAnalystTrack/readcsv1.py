import numpy as np
import pandas as pd


class DataShell:

    # Initialize class with self and inputFile
    def __init__(self, input_file):
        self.file = input_file

    # Define generate_csv method, with self argument
    def generate_csv(self):
        self.data_as_csv = pd.read_csv(self.file)
        return self.data_as_csv


file = open("pd_template.csv", mode="r")
data = DataShell(file)
print(data.generate_csv())


# many more stuffz here

file.close()
