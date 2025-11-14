"""
Test script for Agora-compatible /chat/completions endpoint.
Tests streaming SSE responses with proper formatting.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"


def test_health():
    print("=" * 70)
    print("TEST: Health Check")
    print("=" * 70)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_non_streaming_rejection():
    print("=" * 70)
    print("TEST: Non-streaming Request (Should Reject)")
    print("=" * 70)
    
    payload = {
        "model": "gemini-2.5-pro",
        "messages": [
            {"role": "user", "content": "What food do you recommend for someone feeling sad?"}
        ],
        "stream": False
    }
    
    response = requests.post(f"{BASE_URL}/chat/completions", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_streaming_basic():
    print("=" * 70)
    print("TEST: Basic Streaming Request (Agora Format)")
    print("=" * 70)
    
    payload = {
        "model": "gemini-2.5-pro",
        "messages": [
            {"role": "user", "content": "recommend a north indian comfort food."}
        ],
        "modalities": ["text"],
        "stream": True
    }
    
    print(f"Request payload:\n{json.dumps(payload, indent=2)}\n")
    
    with requests.post(f"{BASE_URL}/chat/completions", json=payload, stream=True) as response:
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}\n")
        print("Streaming chunks:")
        print("-" * 70)
        
        chunk_count = 0
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                print(decoded)
                
                if decoded.startswith("data: "):
                    chunk_count += 1
                    data_content = decoded[6:]
                    
                    if data_content == "[DONE]":
                        print(f"\nStream ended with [DONE] sentinel")
                        break
                    
                    try:
                        chunk_json = json.loads(data_content)
                        if "choices" in chunk_json:
                            delta = chunk_json["choices"][0].get("delta", {})
                            if "content" in delta:
                                print(f"  -> Content: {delta['content']!r}")
                    except json.JSONDecodeError:
                        pass
        
        print("-" * 70)
        print(f"Total chunks received: {chunk_count}\n")


def test_streaming_with_tools():
    print("=" * 70)
    print("TEST: Streaming with Tools (Agora Format)")
    print("=" * 70)
    
    payload = {
        "model": "gemini-2.5-pro",
        "messages": [
            {"role": "user", "content": "I'm feeling romantic and want to order dinner. I'm vegetarian and my budget is 500 rupees. What do you recommend?"}
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
                                "description": "User's current mood (e.g., happy, sad, stressed, energetic, romantic)"
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
        "stream": True
    }
    
    print(f"Request payload:\n{json.dumps(payload, indent=2)}\n")
    
    with requests.post(f"{BASE_URL}/chat/completions", json=payload, stream=True) as response:
        print(f"Status: {response.status_code}")
        print("Streaming chunks:")
        print("-" * 70)
        
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                
                if decoded.startswith("data: "):
                    data_content = decoded[6:]
                    
                    if data_content == "[DONE]":
                        print(f"\nStream ended with [DONE] sentinel")
                        break
                    
                    try:
                        chunk_json = json.loads(data_content)
                        if "choices" in chunk_json:
                            delta = chunk_json["choices"][0].get("delta", {})
                            if "content" in delta:
                                sys.stdout.write(delta["content"])
                                sys.stdout.flush()
                            if "tool_calls" in delta:
                                print(f"\n  -> Tool call: {delta['tool_calls']}")
                    except json.JSONDecodeError:
                        pass
        
        print("\n" + "-" * 70 + "\n")


def test_agora_complete_flow():
    print("=" * 70)
    print("TEST: Complete Agora-style Request with All Fields")
    print("=" * 70)
    
    payload = {
        "model": "gemini-2.5-pro",
        "messages": [
            {"role": "system", "content": "You are Flavourey, a friendly mood-based food ordering assistant. Help users find food that matches their mood and preferences."},
            {"role": "user", "content": "I'm feeling happy and energetic! Suggest something spicy and flavorful."}
        ],
        "modalities": ["text"],
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    print(f"Request payload:\n{json.dumps(payload, indent=2)}\n")
    
    with requests.post(f"{BASE_URL}/chat/completions", json=payload, stream=True) as response:
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print("\nStreaming response:\n")
        
        full_content = ""
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                
                if decoded.startswith("data: "):
                    data_content = decoded[6:]
                    
                    if data_content == "[DONE]":
                        break
                    
                    try:
                        chunk_json = json.loads(data_content)
                        if "choices" in chunk_json:
                            delta = chunk_json["choices"][0].get("delta", {})
                            if "content" in delta:
                                content = delta["content"]
                                full_content += content
                                sys.stdout.write(content)
                                sys.stdout.flush()
                    except json.JSONDecodeError as e:
                        print(f"\nJSON decode error: {e}")
        
        print(f"\n\nFull response: {full_content!r}\n")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" Agora Custom LLM - Gemini Proxy Test Suite")
    print("=" * 70 + "\n")
    
    try:
        test_health()
        test_non_streaming_rejection()
        test_streaming_basic()
        test_streaming_with_tools()
        test_agora_complete_flow()
        
        print("=" * 70)
        print(" All tests completed!")
        print("=" * 70 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to server at", BASE_URL)
        print("Make sure the server is running: python main.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
