import pandas as pd
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Determine absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_CSV = os.path.join(BASE_DIR, "dataset", "Match_Results.csv")
PENALTY_CSV = os.path.join(BASE_DIR, "dataset", "Penalty_Shootouts.csv")
MODEL_PATH = os.path.join(BASE_DIR, "worldcup_model.pkl")

def train():
    print("1. Loading datasets...")
    df_results = pd.read_csv(RESULTS_CSV)
    df_penalties = pd.read_csv(PENALTY_CSV)

    # Convert date strings to datetime objects for filtering
    df_results['date'] = pd.to_datetime(df_results['date'], errors='coerce')
    df_penalties['date'] = pd.to_datetime(df_penalties['date'], errors='coerce')

    print("2. Filtering data from year 2000 onwards...")
    df_results = df_results[df_results['date'].dt.year >= 2000].copy()
    df_penalties = df_penalties[df_penalties['date'].dt.year >= 2000].copy()

    print("3. Data Cleaning & Merging (Handling Penalty Shootouts)...")
    # Initial label: 1 (Home win), 2 (Away win), 0 (Draw)
    df_results['match_outcome'] = 0
    df_results.loc[df_results['home_score'] > df_results['away_score'], 'match_outcome'] = 1
    df_results.loc[df_results['home_score'] < df_results['away_score'], 'match_outcome'] = 2

    # Merge to find which draws were resolved by penalties
    df_merged = pd.merge(
        df_results, 
        df_penalties[['date', 'home_team', 'away_team', 'winner']], 
        on=['date', 'home_team', 'away_team'], 
        how='left'
    )

    # Update outcomes for matches that ended in a draw but had a penalty shootout winner
    mask_draw = (df_merged['match_outcome'] == 0) & (df_merged['winner'].notnull())
    df_merged.loc[mask_draw & (df_merged['winner'] == df_merged['home_team']), 'match_outcome'] = 1
    df_merged.loc[mask_draw & (df_merged['winner'] == df_merged['away_team']), 'match_outcome'] = 2

    print("4. Feature Engineering...")
    # Select basic features for the RandomForest model
    features = ['home_team', 'away_team', 'neutral']
    X = df_merged[features].copy()
    
    # Convert 'neutral' boolean to int (1/0)
    X['neutral'] = X['neutral'].fillna(False).astype(int)

    # One-hot encode the categorical team names
    X = pd.get_dummies(X, columns=['home_team', 'away_team'])
    y = df_merged['match_outcome']

    print("5. Training RandomForestClassifier...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print("6. Evaluating & Saving Model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("="*40)
    print(f"Model Accuracy on Test Set: {accuracy * 100:.2f}%")
    print("="*40)

    # Save both the model and the feature columns (required for alignment during prediction)
    model_data = {
        'model': model,
        'features': X.columns.tolist()
    }
    joblib.dump(model_data, MODEL_PATH, compress=3)
    print(f"Model saved successfully to: {MODEL_PATH}")

if __name__ == "__main__":
    train()
