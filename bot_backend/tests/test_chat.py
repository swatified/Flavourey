"""
Test script for /chat/completions endpoint
"""
import requests
import json

url = "http://localhost:8000/chat/completions"

# Test 1: Simple request without tools
payload1 = {
    "model": "gemini-2.5-pro",
    "messages": [
        {"role": "user", "content": "I feel stressed, suggest some comfort food"}
    ],
    "stream": False
}

print("=" * 60)
print("TEST 1: Simple request without tools")
print("=" * 60)

try:
    response = requests.post(url, json=payload1)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(response, 'text'):
        print(f"Response text: {response.text}")

print("\n" + "=" * 60)
print("TEST 2: Request with tool calling")
print("=" * 60)



# Test 2: Request with tool calling
payload2 = {
    "model": "gemini-2.5-pro",
    "messages": [
        {"role": "user", "content": "I feel stressed, suggest some comfort food under 300 rupees"}
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "search_menu",
                "description": "Search menu items based on mood, dietary restrictions, and budget",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mood": {
                            "type": "string",
                            "description": "User mood (e.g., happy, sad, stressed, energetic, romantic)"
                        },
                        "max_budget": {
                            "type": "number",
                            "description": "Maximum budget in INR"
                        },
                        "dietary": {
                            "type": "string",
                            "enum": ["veg", "non-veg", "vegan", "any"],
                            "description": "Dietary preference"
                        },
                        "allergens_to_avoid": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of allergens to avoid"
                        }
                    },
                    "required": ["mood"]
                }
            }
        }
    ],
    "stream": False
}

try:
    response = requests.post(url, json=payload2)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(response, 'text'):
        print(f"Response text: {response.text}")
