"""
Recommender module for mood-based menu search and filtering.
Uses the real Indian Food Dataset from assets/dataset/Indian-Food-Dataset.csv
"""

import os
import csv
import re
from typing import Optional, List, Dict, Any
from .data_loader import FoodDataset

# Cache for loaded dataset
_cached_dataset = None


def _load_food_dataset():
    """Load and cache the Indian Food Dataset."""
    global _cached_dataset
    
    if _cached_dataset is not None:
        return _cached_dataset
    
    # Try multiple paths to find the CSV
    possible_paths = [
        'assets/dataset/Indian-Food-Dataset.csv',
        '../assets/dataset/Indian-Food-Dataset.csv',
        '../../assets/dataset/Indian-Food-Dataset.csv',
        os.path.join(os.path.dirname(__file__), '../../assets/dataset/Indian-Food-Dataset.csv'),
    ]
    
    csv_path = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_path = path
            break
    
    if not csv_path:
        raise FileNotFoundError("Could not find Indian-Food-Dataset.csv")
    
    # Load CSV into memory
    items = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)
    
    _cached_dataset = items
    return items


class Recommender:
    def __init__(self, dataset: Optional[FoodDataset] = None):
        self.dataset = dataset  # Keep for backward compatibility

    def recommend(self, mood: str, max_calories: Optional[int] = None, tastes: Optional[List[str]] = None, top_n: int = 5) -> List[Dict]:
        if self.dataset:
            return self.dataset.recommend(mood=mood, max_calories=max_calories, tastes=tastes, top_n=top_n)
        return []


# Tool function for LLM - uses real dataset
async def search_menu_items(
    mood: Optional[str] = None,
    max_budget: Optional[float] = None,
    dietary: str = "any",
    allergens_to_avoid: Optional[List[str]] = None,
    spice_preference: Optional[str] = None,
    max_calories: Optional[int] = None,
    cuisine: Optional[str] = None,
    limit: int = 8
) -> Dict[str, Any]:
    """
    Search menu items from the real Indian Food Dataset based on criteria.
    
    This function can be called as a tool by the LLM.
    
    Args:
        mood: User's current mood (happy, sad, stressed, energetic, romantic, etc.)
        max_budget: Maximum budget in INR
        dietary: Dietary preference (veg, non-veg, any)
        allergens_to_avoid: List of allergens to avoid (dairy, nuts, gluten, eggs, etc.)
        spice_preference: Spice preference (mild, medium, spicy)
        max_calories: Maximum calories
        cuisine: Specific cuisine type (South Indian, North Indian, Mexican, etc.)
        limit: Maximum number of items to return
        
    Returns:
        Dict with 'items' list containing matching menu items from the real dataset
    """
    try:
        # Load the real dataset
        all_items = _load_food_dataset()
        
        # Start with all items
        filtered_items = list(all_items)
        
        # Filter by dietary preference
        if dietary and dietary != "any":
            if dietary in ["veg", "vegetarian"]:
                filtered_items = [item for item in filtered_items if item.get('diet_type', '').lower() == 'veg']
            elif dietary in ["non-veg", "nonveg", "non-vegetarian"]:
                filtered_items = [item for item in filtered_items if item.get('diet_type', '').lower() == 'non-veg']
        
        # Filter by budget
        if max_budget:
            filtered_items = [
                item for item in filtered_items
                if float(item.get('price_inr', 0)) <= max_budget
            ]
        
        # Filter by calories
        if max_calories:
            filtered_items = [
                item for item in filtered_items
                if int(item.get('calories', 0)) <= max_calories
            ]
        
        # Filter by cuisine
        if cuisine:
            cuisine_lower = cuisine.lower()
            filtered_items = [
                item for item in filtered_items
                if cuisine_lower in item.get('type-of-cuisine', '').lower()
            ]
        
        # Filter by allergens (check ingredients)
        if allergens_to_avoid:
            allergens_set = set(a.lower() for a in allergens_to_avoid)
            filtered_items = [
                item for item in filtered_items
                if not any(allergen in item.get('ingredients', '').lower() for allergen in allergens_set)
            ]
        
        # Score and sort by mood relevance
        if mood:
            mood_keywords = _get_mood_keywords(mood)
            
            def mood_score(item):
                score = 0.0
                ingredients = item.get('ingredients', '').lower()
                title = item.get('title', '').lower()
                cuisine_type = item.get('type-of-cuisine', '').lower()
                
                # Check for mood keywords in title and ingredients
                for keyword in mood_keywords:
                    if keyword in title:
                        score += 3.0
                    if keyword in ingredients:
                        score += 1.0
                    if keyword in cuisine_type:
                        score += 0.5
                
                # Boost rating
                rating = float(item.get('rating', 0))
                score += rating * 0.5
                
                return score
            
            # Sort by mood relevance
            filtered_items = sorted(filtered_items, key=mood_score, reverse=True)
        else:
            # If no mood, sort by rating
            filtered_items = sorted(
                filtered_items,
                key=lambda x: float(x.get('rating', 0)),
                reverse=True
            )
        
        # Limit results
        filtered_items = filtered_items[:limit]
        
        # Format results
        result_items = []
        for item in filtered_items:
            result_items.append({
                "name": item.get('title', 'Unknown Dish'),
                "price": float(item.get('price_inr', 0)),
                "cuisine": item.get('type-of-cuisine', 'Indian'),
                "diet_type": item.get('diet_type', 'veg'),
                "rating": float(item.get('rating', 0)),
                "calories": int(item.get('calories', 0)),
                "ingredients": item.get('ingredients', ''),
                "image_url": item.get('image-url', '')
            })
        
        return {
            "items": result_items,
            "count": len(result_items),
            "total_in_dataset": len(all_items),
            "filters_applied": {
                "mood": mood,
                "max_budget": max_budget,
                "dietary": dietary,
                "allergens_avoided": allergens_to_avoid or [],
                "max_calories": max_calories,
                "cuisine": cuisine
            }
        }
    
    except FileNotFoundError as e:
        return {
            "error": f"Dataset not found: {str(e)}",
            "items": [],
            "suggestion": "Please ensure the Indian-Food-Dataset.csv is in assets/dataset/"
        }
    except Exception as e:
        return {
            "error": f"Search error: {str(e)}",
            "items": []
        }


def _get_mood_keywords(mood: str) -> List[str]:
    """Get relevant food keywords for a given mood."""
    mood_lower = mood.lower()
    
    mood_mappings = {
        'happy': ['sweet', 'chocolate', 'dessert', 'cake', 'ice cream', 'festive', 'celebration'],
        'sad': ['comfort', 'warm', 'soup', 'mac', 'cheese', 'chocolate', 'creamy', 'rich'],
        'stressed': ['comfort', 'creamy', 'cheese', 'pasta', 'biryani', 'rich'],
        'energetic': ['spicy', 'tangy', 'protein', 'chicken', 'biryani', 'curry', 'rice'],
        'romantic': ['rich', 'creamy', 'special', 'paneer', 'butter', 'kebab', 'dessert'],
        'angry': ['spicy', 'hot', 'chilli', 'pepper', 'vindaloo', 'tandoori'],
        'relaxed': ['light', 'healthy', 'salad', 'soup', 'idli', 'dosa', 'upma'],
        'tired': ['energy', 'protein', 'dal', 'rice', 'curry', 'nutritious'],
        'excited': ['festive', 'special', 'biryani', 'kebab', 'tandoori', 'celebration']
    }
    
    return mood_mappings.get(mood_lower, [])
