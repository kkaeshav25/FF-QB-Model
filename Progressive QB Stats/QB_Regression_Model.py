import pandas as pd
df_list = [pd.read_csv(f'qbstats_{year}.csv')for year in range(2020,2025)]
df = pd.concat(df_list, ignore_index = True)
