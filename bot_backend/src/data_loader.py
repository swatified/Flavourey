import os
from typing import List, Optional
import pandas as pd


class FoodDataset:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        # normalize column names to lower
        self.df.columns = [c.lower().strip() for c in self.df.columns]

    @classmethod
    def load_from_csv(cls, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV file not found: {path}")
        df = pd.read_csv(path)
        return cls(df)

    def _col(self, *names):
        # return first matching column name in df
        cols = self.df.columns
        for name in names:
            for c in cols:
                if name in c:
                    return c
        return None

    def filter_by_mood(self, mood: str) -> pd.DataFrame:
        col = self._col('mood', 'moods', 'labels')
        if col is None:
            return self.df
        # support comma-separated labels
        mask = self.df[col].astype(str).str.lower().str.contains(mood.lower(), na=False)
        return self.df[mask]

    def filter_by_taste(self, tastes: List[str]) -> pd.DataFrame:
        col = self._col('taste', 'tastes', 'tags', 'flavour', 'flavor')
        if col is None or not tastes:
            return self.df
        df = self.df
        mask = False
        for t in tastes:
            mask = mask | df[col].astype(str).str.lower().str.contains(t.lower(), na=False)
        return df[mask]

    def filter_by_calories(self, min_c: Optional[int], max_c: Optional[int]) -> pd.DataFrame:
        col = self._col('calorie', 'calories', 'kcal')
        if col is None:
            return self.df
        ser = pd.to_numeric(self.df[col], errors='coerce')
        mask = pd.Series(True, index=self.df.index)
        if min_c is not None:
            mask = mask & (ser >= min_c)
        if max_c is not None:
            mask = mask & (ser <= max_c)
        return self.df[mask]

    def recommend(self, mood: str, max_calories: Optional[int] = None, tastes: Optional[List[str]] = None, top_n: int = 5):
        # Basic scoring: mood match first, then taste match, then calories.
        df = self.filter_by_mood(mood)
        if tastes:
            taste_df = self.filter_by_taste(tastes)
            # prefer intersection
            df = df.merge(taste_df, how='inner') if not df.empty and not taste_df.empty else df
        if max_calories is not None:
            df = self.filter_by_calories(None, max_calories)

        # If still empty, fall back to full dataset filtered by tastes/calories
        if df.empty:
            df = self.df
            if tastes:
                df = self.filter_by_taste(tastes)
            if max_calories is not None:
                df = df[self.filter_by_calories(None, max_calories).index]

        # Simple ranking: prefer exact mood mentions and lower calories
        calorie_col = self._col('calorie', 'calories', 'kcal')
        def calorie_score(r):
            if calorie_col and pd.notna(r.get(calorie_col)):
                try:
                    return float(r.get(calorie_col))
                except Exception:
                    return 99999.0
            return 99999.0

        records = df.to_dict(orient='records')
        # sort by calorie ascending to prefer lighter meals
        records = sorted(records, key=lambda r: calorie_score(r))
        return records[:top_n]


if __name__ == '__main__':
    # quick local test
    path = os.environ.get('DATA_CSV', 'Indian-Food-Data.csv')
    if os.path.exists(path):
        ds = FoodDataset.load_from_csv(path)
        print('Loaded rows:', len(ds.df))
    else:
        print('No CSV found at', path)
