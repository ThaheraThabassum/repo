import pandas as pd

# Read the Excel file
df = pd.read_excel("db_config.xlsx")

# Print the entire DataFrame
print(df)

# Print individual columns for debugging
print("Database:", df.iloc[0, 0])
print("Table:", df.iloc[0, 1])
print("Option:", df.iloc[0, 2])
print("Where Condition:", df.iloc[0, 3])
