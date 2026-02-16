
import pandas as pd
import holidays

class FeatureEngineer:
    def __init__(self):
        self.kr_holidays = holidays.KR()

    def add_calendar_features(self, df: pd.DataFrame, date_col="date") -> pd.DataFrame:
        """
        Adds calendar-based features to the dataframe.
        Expected input: DataFrame with a 'date' column (datetime or string YYYY-MM-DD).
        """
        df = df.copy()
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col])

        # Basic Calendar Features
        df["year"] = df[date_col].dt.year
        df["month"] = df[date_col].dt.month
        df["day"] = df[date_col].dt.day
        df["day_of_week"] = df[date_col].dt.dayofweek # 0=Mon, 6=Sun
        
        # Weekend (Saturday=5, Sunday=6)
        df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)
        
        # Holiday (South Korea)
        # holidays library keys are date objects
        df["is_holiday"] = df[date_col].apply(lambda x: 1 if x in self.kr_holidays else 0)
        
        return df

if __name__ == "__main__":
    # Test
    dates = ["2024-01-01", "2024-01-02", "2023-12-25", "2023-05-05"]
    test_df = pd.DataFrame({"date": dates})
    
    fe = FeatureEngineer()
    processed = fe.add_calendar_features(test_df)
    print(processed)
