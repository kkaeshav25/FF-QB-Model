import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt

# Example team ratings (you should expand this as needed)
team_ratings = {
    'KC': 93, 'BUF': 90, 'PHI': 88, 'SF': 92, 'DAL': 87, 'BAL': 91,
    'DET': 85, 'CIN': 89, 'JAX': 82, 'NYJ': 86, 'CLE': 83, 'MIN': 80,
    'MIA': 88, 'LAC': 79, 'SEA': 81, 'CHI': 78, 'NO': 76, 'ATL': 77,
    'PIT': 82, 'DEN': 75, 'GB': 78, 'IND': 74, 'TEN': 73, 'TB': 72,
    'CAR': 70, 'NYG': 71, 'NE': 68, 'LV': 69, 'ARI': 67, 'HOU': 84,
    'WAS': 70, 'LAR': 76
}

files = {
    2020: "2020 QB stats.csv",
    2021: "2021 QB stats.csv",
    2022: "2022 QB stats.csv",
    2023: "2023 QB stats.csv",
    2024: "2024 QB stats.csv"
}

all_years_df = pd.DataFrame()

for year, path in files.items():
    df = pd.read_csv(path)
    df['Year'] = year
    all_years_df = pd.concat([all_years_df, df], ignore_index=True)

# Estimate games played
all_years_df['Games'] = all_years_df['YD'] / all_years_df['Y/G']
all_years_df = all_years_df[all_years_df['Games'] >= 10]  # filter consistent starters

# Normalize per game
all_years_df['CMP/G'] = all_years_df['CMP'] / all_years_df['Games']
all_years_df['ATT/G'] = all_years_df['ATT'] / all_years_df['Games']
all_years_df['TD/G'] = all_years_df['TD'] / all_years_df['Games']
all_years_df['INT/G'] = all_years_df['INT'] / all_years_df['Games']
all_years_df['FP/G'] = all_years_df['FP'] / all_years_df['Games']

# Merge team quality
all_years_df['Team_Quality'] = all_years_df['Team'].map(team_ratings)

df = all_years_df.sort_values(by=["Name", "Year"])

# Feature set
stat_cols = ['CMP/G', 'ATT/G', 'YD', 'TD/G', 'INT/G', 'Y/C', 'FP/G', 'Team_Quality']

# Create lagged features
for col in stat_cols:
    df[f'prev_{col}'] = df.groupby('Name')[col].shift(1)

df = df.dropna(subset=[f'prev_{col}' for col in stat_cols])

# Train on 2020–2022
train_df = df[df['Year'] <= 2022]
X_train = train_df[[f'prev_{col}' for col in stat_cols]]
y_train = train_df[['CMP', 'ATT', 'YD', 'TD', 'INT', 'Y/C', 'Y/G', 'FP']]

# Validate on 2023
val_df = df[df['Year'] == 2023]
X_val = val_df[[f'prev_{col}' for col in stat_cols]]
y_val = val_df[['CMP', 'ATT', 'YD', 'TD', 'INT', 'Y/C', 'Y/G', 'FP']]

# Model
model = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42))
model.fit(X_train, y_train)
val_preds = model.predict(X_val)

# Evaluate
mae = mean_absolute_error(y_val, val_preds)
print(f"Mean Absolute Error on 2023 validation set: {mae:.2f}")

# Predict 2025 from 2024
predict_df = df[df['Year'] == 2024]
X_predict = predict_df[[f'prev_{col}' for col in stat_cols]]
predictions = model.predict(X_predict)

# Output
predicted_2025 = pd.DataFrame(predictions, columns=[f'2025_{col}' for col in y_val.columns])
predicted_2025['Name'] = predict_df['Name'].values
predicted_2025['Team'] = predict_df['Team'].values
predicted_2025 = predicted_2025.sort_values(by=['2025_FP'], ascending=False)

print(predicted_2025)
# predicted_2025.to_csv("Predicted_QB_Stats_2025.csv", index=False)
