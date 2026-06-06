import os
import logging
import joblib
import pandas as pd
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MatchPredictor:
    TEAM_NAME_MAPPING = {"USA": "United States", "South Korea": "Korea Republic", "North Korea": "Korea DPR"}

    def __init__(self):
        self.model = None
        self.features = None
        
        # Determine the path to the model file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "worldcup_model.pkl")
        
        # Try to load the model
        if os.path.exists(model_path):
            try:
                data = joblib.load(model_path)
                self.model = data.get('model')
                self.features = data.get('features')
                logger.info(f"Model successfully loaded from {model_path}.")
            except Exception as e:
                logger.error(f"Error loading the model: {e}")
        else:
            logger.warning(f"WARNING: Model file not found at {model_path}. Please run train_model.py first.")

    def predict_win_probability(self, home_team: str, away_team: str) -> dict:
        """
        Predict the probability of match outcomes between home_team and away_team.
        Returns a dictionary with percentages.
        """
        # Map team names if they are in the dictionary
        home_team = self.TEAM_NAME_MAPPING.get(home_team, home_team)
        away_team = self.TEAM_NAME_MAPPING.get(away_team, away_team)

        if self.model is None or self.features is None:
            logger.error("Cannot predict: Model is not loaded.")
            return {"error": "Model not loaded"}

        # 1. Initialize a DataFrame with 0s for all features seen during training
        input_data = pd.DataFrame(columns=self.features)
        input_data.loc[0] = 0

        # By default, assume neutral = 0 (false)
        if 'neutral' in self.features:
            input_data.loc[0, 'neutral'] = 0

        # 2. Encode Home Team
        home_col = f"home_team_{home_team}"
        if home_col in self.features:
            input_data.loc[0, home_col] = 1
        else:
            logger.warning(f"Home team '{home_team}' was not in the training dataset.")

        # 3. Encode Away Team
        away_col = f"away_team_{away_team}"
        if away_col in self.features:
            input_data.loc[0, away_col] = 1
        else:
            logger.warning(f"Away team '{away_team}' was not in the training dataset.")

        # 4. Predict probabilities
        # predict_proba returns a 2D array, we take the first row [0]
        probabilities = self.model.predict_proba(input_data)[0]

        # 5. Map probabilities to correct outcome labels based on model classes
        # Remember: 1 = Home Win, 0 = Draw, 2 = Away Win
        result = {"home_win": 0.0, "draw": 0.0, "away_win": 0.0}
        
        for idx, class_label in enumerate(self.model.classes_):
            percent = round(probabilities[idx] * 100, 2)
            
            if class_label == 1:
                result["home_win"] = percent
            elif class_label == 0:
                result["draw"] = percent
            elif class_label == 2:
                result["away_win"] = percent

        return result
