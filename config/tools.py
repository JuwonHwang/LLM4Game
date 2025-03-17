tool_rerole = {
    "type": "function",
    "function": {
        "name": "reroll",
        "description": "Refreshes the available units in the shop.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
        "strict": True
    }
}


tool_buy_exp = {
    "type": "function",
    "function": {
        "name": "buy_exp",
        "description": "Purchases a specified amount of experience points (EXP) to level up. Each purchase grants 4 EXP points. The maximum level attainable is 10.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
        "strict": True
    }
}

tool_buy_unit = {
    "type": "function",
    "function": {
        "name": "buy_unit",
        "description": "Purchases a specified amount of experience points (EXP) to level up. Each purchase grants 4 EXP points. The maximum level attainable is 10.",
        "parameters": {
            "type": "object",
            "properties": {
                "shop_index": {
                    "type": "integer",
                    "description": "The shop unit index to purchase.",
                }
            },
            "required": ["shop_index"],
            "additionalProperties": False
        },
        "strict": True
    }
}

tool_sell_unit = {
    "type": "function",
    "function": {
        "name": "sell_unit",
        "description": "Sell a unit from the specified source (bench or field).",
        "parameters": {
            "type": "object",
            "properties": {
                "source_type": {
                    "type": "string",
                    "description": "The source containing the unit to sell. Options are 'bench' or 'field'.",
                    "enum": ["bench", "field"],
                    "default": "bench"
                },
                "source_index": {
                    "type": "integer",
                    "description": "The index of the unit to sell within the specified source.",
                }
            },
            "required": ["source_type", "source_index"],
            "additionalProperties": False
        },
        "strict": True
    }
}

tool_move_unit = {
    "type": "function",
    "function": {
        "name": "move_unit",
        "description": "Move a unit from a specified source (bench or field) to a target location (bench or field).",
        "parameters": {
            "type": "object",
            "properties": {
                "source_type": {
                    "type": "string",
                    "description": "The source containing the unit to move. Options are 'bench' or 'field'.",
                    "enum": ["bench", "field"],
                    "default": "bench"
                },
                "target_type": {
                    "type": "string",
                    "description": "The destination for the unit. Options are 'bench' or 'field'.",
                    "enum": ["bench", "field"],
                    "default": "field"
                },
                "source_index": {
                    "type": "integer",
                    "description": "The index of the unit in the source to move.",
                },
                "target_index": {
                    "type": "integer",
                    "description": "The index in the target where the unit should be placed.",
                }
            },
            "required": ["source_type", "target_type", "source_index", "target_index"],
            "additionalProperties": False
        },
        "strict": True
    }
}

tool_none = {
    "type": "function",
    "function": {
        "name": "none",
        "description": "A no-operation function that performs no action.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
        "strict": True
    }
}