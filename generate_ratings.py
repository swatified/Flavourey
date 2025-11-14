import pandas as pd
import numpy as np
import random

# Set random seed for reproducibility (optional - remove if you want different ratings each time)
random.seed(42)
np.random.seed(42)

# Read the CSV file
csv_file = 'assets/dataset/Indian-Food-Dataset.csv'
df = pd.read_csv(csv_file)

# Generate random star ratings between 3.0 and 5.0 (you can adjust the range)
# Using a normal distribution centered around 4.2 with some variation
# This creates more realistic ratings where most dishes are rated between 3.5 and 4.8
ratings = np.random.normal(4.2, 0.5, len(df))

# Clip the ratings to be between 3.0 and 5.0
ratings = np.clip(ratings, 3.0, 5.0)

# Round to 1 decimal place
ratings = np.round(ratings, 1)

# Add the ratings column to the dataframe
df['rating'] = ratings

# Save back to CSV
df.to_csv(csv_file, index=False)

print(f"Successfully added ratings to {len(df)} dishes!")
print(f"\nRating statistics:")
print(f"Average rating: {ratings.mean():.2f}")
print(f"Min rating: {ratings.min():.1f}")
print(f"Max rating: {ratings.max():.1f}")
print(f"\nFirst 10 dishes with ratings:")
print(df[['title', 'rating']].head(10))
