import csv
import random

def categorize_mood(title, category, ingredients, diet_type, calories):
    """
    Categorize dishes into moods based on their characteristics.
    
    Moods:
    - happy: Comfort food, popular dishes, mild sweets
    - sad: Warm, comforting, simple dishes (soups, khichdi, warm drinks)
    - angry: Very spicy, hot, fiery dishes
    - energetic: High-calorie, protein-rich, fried, grilled items
    - romantic: Rich, creamy, indulgent, chocolate, desserts
    - neutral: Healthy, light, balanced meals
    """
    title_lower = title.lower()
    ingredients_lower = ingredients.lower()
    
    # Romantic - rich, creamy, indulgent dishes, desserts, exotic items
    romantic_keywords = ['chocolate', 'cream', 'butter', 'paneer butter', 'korma', 'makhani', 
                        'malai', 'shahi', 'royal', 'rich', 'truffle', 'saffron', 'rose',
                        'strawberry', 'mango', 'tart', 'pie', 'mousse', 'cake', 'rabri',
                        'basundi', 'kulfi', 'falooda', 'romantic']
    
    if any(word in title_lower for word in romantic_keywords):
        if category == 'sweet' or any(word in title_lower for word in ['chocolate', 'strawberry', 'rose', 'saffron', 'cream cheese', 'truffle']):
            return 'romantic'
    
    # Angry - very spicy, hot, fiery dishes
    angry_keywords = ['chilli', 'chili', 'spicy', 'hot', 'pepper', 'vindaloo', 'ghost pepper',
                     'fire', 'schezwan', 'red chilli', 'angry', 'devil', 'fiery', 'tangy',
                     'achari', 'pickle']
    
    if any(word in title_lower for word in angry_keywords):
        if 'spicy' in title_lower or 'chilli' in title_lower or 'hot' in title_lower or 'vindaloo' in title_lower:
            return 'angry'
    
    # Check ingredients for high spice level
    if any(word in ingredients_lower for word in ['red chilli powder', 'green chillies', 'red chilli flakes', 'chilli paste']):
        spicy_count = ingredients_lower.count('chilli') + ingredients_lower.count('pepper')
        if spicy_count >= 3:
            return 'angry'
    
    # Sad - comfort food, warm soups, khichdi, simple dal-rice, tea/coffee, warm drinks
    sad_keywords = ['soup', 'khichdi', 'porridge', 'chai', 'tea', 'coffee', 'warm',
                   'comfort', 'kadhi', 'rasam', 'broth', 'stew']
    
    if any(word in title_lower for word in sad_keywords):
        if 'soup' in title_lower or 'khichdi' in title_lower or 'chai' in title_lower or 'tea' in title_lower or 'coffee' in title_lower:
            return 'sad'
    
    # Energetic - high calorie, protein-rich, spicy, fried items
    energetic_keywords = ['biryani', 'fried', 'tandoori', 'grilled', 'roast', 'kebab', 
                         'chicken', 'mutton', 'egg', 'protein', 'power', 'energy',
                         'masala', 'tikka', 'crispy', 'crunchy', 'bhurji']
    
    if calories > 600 or any(word in title_lower for word in energetic_keywords):
        if diet_type == 'non-veg' or 'fried' in title_lower or 'biryani' in title_lower or 'tandoori' in title_lower:
            return 'energetic'
        if calories > 700:
            return 'energetic'
    
    # Happy - comfort food, traditional favorites, mild sweets, popular dishes
    happy_keywords = ['dosa', 'idli', 'pulao', 'dal', 'paratha', 'puri', 'poori',
                     'lassi', 'halwa', 'ladoo', 'burfi', 'gulab jamun', 'pizza', 'burger',
                     'sandwich', 'pasta', 'ice cream', 'samosa', 'pakora', 'peda',
                     'barfi', 'jalebi', 'rasgulla', 'paneer', 'aloo']
    
    if any(word in title_lower for word in happy_keywords):
        return 'happy'
    
    # Neutral - healthy salads, light dishes, balanced meals
    neutral_keywords = ['salad', 'raita', 'chutney', 'steamed', 'boiled', 'light',
                       'healthy', 'vegetable', 'stir fry', 'sauteed', 'sundal',
                       'poriyal', 'thoran', 'sabzi']
    
    if any(word in title_lower for word in neutral_keywords):
        if category == 'starter' or calories < 350:
            return 'neutral'
    
    if calories < 250 and category != 'sweet':
        return 'neutral'
    
    # Default assignments based on category
    if category == 'sweet':
        return 'happy'
    elif category == 'drink':
        return 'neutral'
    elif category == 'fast-food':
        return 'happy'
    elif category == 'starter':
        return 'neutral'
    else:  # main-course
        # Distribute remaining main courses
        if 'curry' in title_lower:
            return random.choice(['happy', 'energetic'])
        return 'neutral'


def add_mood_column(input_file='Indian-Food-Data.csv', output_file='Indian-Food-Data.csv'):
    """
    Add mood column to the Indian Food dataset.
    """
    # Set random seed for consistency
    random.seed(42)
    
    # Read the CSV
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Processing {len(rows)} dishes...")
    
    # Add mood column
    for i, row in enumerate(rows):
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1} dishes...")
        
        calories = int(row['calories']) if row['calories'].isdigit() else 0
        mood = categorize_mood(
            row['title'], 
            row['category'], 
            row['ingredients'], 
            row['diet_type'], 
            calories
        )
        row['mood'] = mood
    
    # Write back to CSV
    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ Successfully added mood column to the dataset!")
    print(f"  Total dishes categorized: {len(rows)}")
    
    # Show mood distribution
    from collections import Counter
    moods = Counter(row['mood'] for row in rows)
    print('\n  Mood distribution:')
    for mood, count in sorted(moods.items()):
        print(f'    {mood}: {count}')
    
    # Show some examples
    print("\n  Sample dishes by mood:")
    for mood_type in ['happy', 'sad', 'angry', 'energetic', 'romantic', 'neutral']:
        print(f"\n  {mood_type.upper()}:")
        count = 0
        for row in rows:
            if row['mood'] == mood_type and count < 3:
                print(f"    - {row['title'][:50]}")
                count += 1


if __name__ == "__main__":
    add_mood_column()
