import pandas as pd
from matplotlib import pyplot as plt
file = pd.read_csv('new10.csv', sep=',', header=0, nrows=10)

df = pd.DataFrame(file)
price = df['Price']
item = df['Product']
plt.style.use('seaborn-pastel')
plt.scatter(item, price, label="Philadelphia", marker='s', linestyle='--')
plt.xlabel("Items")
plt.ylabel("Cost")
plt.title("Top 12 Protein items")
plt.tight_layout()
plt.show()




