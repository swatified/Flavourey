"""
Test script to verify the Indian Food Dataset integration.
Run this to check if the dataset is properly loaded and searchable.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.recommender import search_menu_items, _load_food_dataset


async def test_dataset_loading():
    """Test 1: Load dataset"""
    print("=" * 60)
    print("TEST 1: Loading Indian Food Dataset")
    print("=" * 60)
    
    try:
        items = _load_food_dataset()
        print(f" Successfully loaded {len(items)} dishes!")
        
        # Show first 3 items
        print("\nFirst 3 dishes:")
        for i, item in enumerate(items[:3], 1):
            print(f"  {i}. {item.get('title')} - ₹{item.get('price_inr')} ({item.get('diet_type')})")
        
        return True
    except Exception as e:
        print(f" Error loading dataset: {e}")
        return False


async def test_mood_search():
    """Test 2: Search by mood"""
    print("\n" + "=" * 60)
    print("TEST 2: Search by Mood (stressed)")
    print("=" * 60)
    
    try:
        result = await search_menu_items(mood="stressed", limit=5)
        
        if result.get('error'):
            print(f"Error: {result['error']}")
            return False
        
        print(f"Found {result['count']} comfort foods for stressed mood:")
        for i, item in enumerate(result['items'], 1):
            print(f"  {i}. {item['name']}")
            print(f"     Price: ₹{item['price']} | Calories: {item['calories']} | Rating: {item['rating']}⭐")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


async def test_dietary_filter():
    """Test 3: Filter by dietary preference"""
    print("\n" + "=" * 60)
    print("TEST 3: Filter by Dietary (vegetarian, budget ₹150)")
    print("=" * 60)
    
    try:
        result = await search_menu_items(
            dietary="veg",
            max_budget=150,
            limit=5
        )
        
        if result.get('error'):
            print(f"Error: {result['error']}")
            return False
        
        print(f"Found {result['count']} vegetarian dishes under ₹150:")
        for i, item in enumerate(result['items'], 1):
            print(f"  {i}. {item['name']} - ₹{item['price']}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


async def test_allergen_filter():
    """Test 4: Filter by allergens"""
    print("\n" + "=" * 60)
    print("TEST 4: Filter with Allergen Avoidance (no dairy, no nuts)")
    print("=" * 60)
    
    try:
        result = await search_menu_items(
            mood="happy",
            allergens_to_avoid=["dairy", "nuts"],
            limit=5
        )
        
        if result.get('error'):
            print(f" Error: {result['error']}")
            return False
        
        print(f" Found {result['count']} dishes without dairy or nuts:")
        for i, item in enumerate(result['items'], 1):
            print(f"  {i}. {item['name']}")
            print(f"     Ingredients: {item['ingredients'][:80]}...")
        
        return True
    except Exception as e:
        print(f" Error: {e}")
        return False


async def test_cuisine_filter():
    """Test 5: Filter by cuisine"""
    print("\n" + "=" * 60)
    print("TEST 5: Filter by Cuisine (South Indian)")
    print("=" * 60)
    
    try:
        result = await search_menu_items(
            cuisine="South Indian",
            max_budget=200,
            limit=5
        )
        
        if result.get('error'):
            print(f" Error: {result['error']}")
            return False
        
        print(f" Found {result['count']} South Indian dishes:")
        for i, item in enumerate(result['items'], 1):
            print(f"  {i}. {item['name']} - ₹{item['price']}")
            print(f"     Cuisine: {item['cuisine']}")
        
        return True
    except Exception as e:
        print(f" Error: {e}")
        return False


async def test_complex_query():
    """Test 6: Complex multi-filter query"""
    print("\n" + "=" * 60)
    print("TEST 6: Complex Query")
    print("Mood: energetic | Diet: veg | Budget: ₹250 | Max Calories: 600")
    print("=" * 60)
    
    try:
        result = await search_menu_items(
            mood="energetic",
            dietary="veg",
            max_budget=250,
            max_calories=600,
            limit=5
        )
        
        if result.get('error'):
            print(f" Error: {result['error']}")
            return False
        
        print(f" Found {result['count']} dishes matching all criteria:")
        for i, item in enumerate(result['items'], 1):
            print(f"  {i}. {item['name']}")
            print(f"     ₹{item['price']} | {item['calories']} cal | {item['rating']}⭐ | {item['diet_type']}")
        
        return True
    except Exception as e:
        print(f" Error: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n TESTING INDIAN FOOD DATASET INTEGRATION")
    print("=" * 60)
    
    tests = [
        test_dataset_loading,
        test_mood_search,
        test_dietary_filter,
        test_allergen_filter,
        test_cuisine_filter,
        test_complex_query
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print(" All tests passed! Dataset integration is working perfectly.")
    else:
        print(f" {total - passed} test(s) failed. Check errors above.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
