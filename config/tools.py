tool_unit_lookup = {
    "type": "function",
    "function": {
        "name": "view_unit_status",
        "description": "View unit status with given unit id.",
        "parameters": {
            "type": "object",
            "properties": {
                "unit_id": {
                    "type": "string",
                    "description": "The unit id to view status.",
                }
            },
            "required": ["unit_id"],
            "additionalProperties": False
        },
        "strict": True
    }
}

tool_expected_gold = {
    "type": "function",
    "function": {
        "name": "calculate_next_round_expected_gold",
        "description": "Calculate the interest based on the gold you currently have.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
        "strict": True
    }
}

tool_field_strength = {
    "type": "function",
    "function": {
        "name": "calculate_field_strength_by_player_id",
        "description": "Calculates the strength of a player's field based on the cost of their units.",
        "parameters": {
            "type": "object",
            "properties": {
                "player_id": {
                    "type": "string",
                    "description": "The player_id whose strength level is to be calculated",
                },
            },
            "required": ["player_id"],
            "additionalProperties": False
        },
        "strict": True
    }
}