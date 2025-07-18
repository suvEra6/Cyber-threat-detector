import pandas as pd

df = pd.read_csv("data/formatted_logs.csv")
print("📂 Columns in formatted_logs.csv:")
print(df.columns.tolist())
