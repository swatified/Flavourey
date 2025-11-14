"""
Test script for /chat/completions endpoint with STREAMING (Agora-compatible)
"""
import requests
import json
import sys

url = "http://localhost:8000/chat/completions"

# Test 1: Simple streaming request
payload1 = {
    "model": "gemini-2.5-pro",
    "messages": [
        {"role": "user", "content": "I feel stressed, suggest some comfort food"}
    ],
    "modalities": ["text"],
    "stream": True  # Changed to True for Agora compatibility
}

print("=" * 60)
print("TEST 1: Streaming request (Agora format)")
print("=" * 60)

try:
    with requests.post(url, json=payload1, stream=True) as response:
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print("\nStreaming response:")
        print("-" * 60)
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                
                if decoded.startswith("data: "):
                    data_content = decoded[6:]
                    
                    if data_content == "[DONE]":
                        print("\n[Stream completed]")
                        break
                    
                    try:
                        chunk_json = json.loads(data_content)
                        if "choices" in chunk_json:
                            delta = chunk_json["choices"][0].get("delta", {})
                            if "content" in delta:
                                content = delta["content"]
                                full_response += content
                                sys.stdout.write(content)
                                sys.stdout.flush()
                    except json.JSONDecodeError:
                        pass
        
        print(f"\n{'-' * 60}")
        print(f"Full response: {full_response!r}\n")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST 2: Streaming with tool calling")
print("=" * 60)

# Test 2: Request with tool calling (streaming)
payload2 = {
    "model": "gemini-2.5-pro",
    "messages": [
        {"role": "user", "content": "I'm feeling romantic and want dinner. I'm vegetarian and my budget is 500 rupees."}
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
    "modalities": ["text"],
    "stream": True  # Changed to True
}

try:
    with requests.post(url, json=payload2, stream=True) as response:
        print(f"Status Code: {response.status_code}")
        print("\nStreaming response:")
        print("-" * 60)
        
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                
                if decoded.startswith("data: "):
                    data_content = decoded[6:]
                    
                    if data_content == "[DONE]":
                        print("\n[Stream completed]")
                        break
                    
                    try:
                        chunk_json = json.loads(data_content)
                        if "choices" in chunk_json:
                            delta = chunk_json["choices"][0].get("delta", {})
                            if "content" in delta:
                                sys.stdout.write(delta["content"])
                                sys.stdout.flush()
                            if "tool_calls" in delta:
                                print(f"\n[Tool call detected: {delta['tool_calls']}]")
                    except json.JSONDecodeError:
                        pass
        
        print(f"\n{'-' * 60}\n")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
print("All tests completed!")
print("=" * 60)
