"""
Tool definitions for Flavourey LLM.
Defines the function schemas that can be called by the AI.
"""

SEARCH_MENU_TOOL = {
    "type": "function",
    "function": {
        "name": "search_menu",
        "description": "Search the Indian food menu database (5940+ dishes) based on user's mood, dietary restrictions, budget, and preferences. Returns real dishes with prices, ratings, calories, and ingredients.",
        "parameters": {
            "type": "object",
            "properties": {
                "mood": {
                    "type": "string",
                    "description": "User's current mood or emotional state",
                    "enum": ["happy", "sad", "stressed", "energetic", "romantic", "angry", "relaxed", "tired", "excited", "neutral"]
                },
                "max_budget": {
                    "type": "number",
                    "description": "Maximum budget in Indian Rupees (INR)"
                },
                "dietary": {
                    "type": "string",
                    "description": "Dietary preference",
                    "enum": ["veg", "non-veg", "any"],
                    "default": "any"
                },
                "allergens_to_avoid": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of allergens or ingredients to avoid (e.g., dairy, nuts, gluten, eggs, garlic, onion)"
                },
                "spice_preference": {
                    "type": "string",
                    "description": "Spice level preference",
                    "enum": ["mild", "medium", "spicy", "any"]
                },
                "max_calories": {
                    "type": "integer",
                    "description": "Maximum calories per dish"
                },
                "cuisine": {
                    "type": "string",
                    "description": "Specific cuisine type (e.g., 'South Indian', 'North Indian', 'Andhra', 'Mexican', 'Udupi')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of dishes to return (default: 8)",
                    "default": 8
                }
            },
            "required": []
        }
    }
}

LOG_ORDER_TOOL = {
    "type": "function",
    "function": {
        "name": "log_order",
        "description": "Log a food order with details for tracking and analytics",
        "parameters": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session identifier"
                },
                "dishes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "quantity": {"type": "integer"},
                            "price": {"type": "number"}
                        }
                    },
                    "description": "List of dishes ordered"
                },
                "total_amount": {
                    "type": "number",
                    "description": "Total order amount in INR"
                },
                "mood": {
                    "type": "string",
                    "description": "User's mood when ordering"
                },
                "special_instructions": {
                    "type": "string",
                    "description": "Any special cooking instructions"
                }
            },
            "required": ["dishes", "total_amount"]
        }
    }
}

# All available tools
ALL_TOOLS = [SEARCH_MENU_TOOL, LOG_ORDER_TOOL]
