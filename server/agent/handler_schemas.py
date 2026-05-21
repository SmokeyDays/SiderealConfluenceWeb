"""Explicit JSON Schemas for critical game-interface handlers.

Add schemas here for handlers whose docstrings contain nested structures
that are ambiguous to the automatic parser. llm_caller will prefer these
schemas when present.
"""

SCHEMAS = {
  "trade_proposal": {
    "type": "object",
    "properties": {
      "to": {"type": "array", "items": {"type": "string"}},
      "send": {
        "type": "object",
        "properties": {
          "items": {"type": "object", "additionalProperties": {"type": "integer"}},
          "factories": {"type": "array", "items": {"type": "string"}},
          "techs": {"type": "array", "items": {"type": "string"}}
        },
        "additionalProperties": False
      },
      "receive": {
        "type": "object",
        "properties": {
          "items": {"type": "object", "additionalProperties": {"type": "integer"}},
          "factories": {"type": "array", "items": {"type": "string"}},
          "techs": {"type": "array", "items": {"type": "string"}}
        },
        "additionalProperties": False
      },
      "message": {"type": "string"}
    },
    "required": ["to", "send", "receive", "message"],
    "additionalProperties": False
  },

  "produce": {
    "type": "object",
    "properties": {
      "factory_name": {"type": "string"},
      "converter_index": {"type": "integer"},
      "extra_properties": {"type": "object", "additionalProperties": True}
    },
    "required": ["factory_name", "converter_index", "extra_properties"],
    "additionalProperties": False
  },

  "exchange_arbitrary": {
    "type": "object",
    "properties": {
      "items": {"type": "object", "additionalProperties": {"type": "integer"}}
    },
    "required": ["items"],
    "additionalProperties": False
  },

  "exchange_wild": {
    "type": "object",
    "properties": {
      "items": {"type": "object", "additionalProperties": {"type": "integer"}}
    },
    "required": ["items"],
    "additionalProperties": False
  },

  "update_bulletin_board": {
    "type": "object",
    "properties": {
      "message": {"type": "string"},
      "seeking": {"type": "object", "additionalProperties": {"type": "integer"}},
      "offering": {"type": "object", "additionalProperties": {"type": "integer"}}
    },
    "required": ["message", "seeking", "offering"],
    "additionalProperties": False
  },

  "discard_colonies": {
    "type": "object",
    "properties": {
      "colonies": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["colonies"],
    "additionalProperties": False
  },

  "submit_bid": {
    "type": "object",
    "properties": {
      "colony_bid": {"type": "integer"},
      "research_bid": {"type": "integer"}
    },
    "required": ["colony_bid", "research_bid"],
    "additionalProperties": False
  },

  "withdraw_trade_proposal": {
    "type": "object",
    "properties": {"id": {"type": "integer"}},
    "required": ["id"],
    "additionalProperties": False
  },

  "accept_trade_proposal": {
    "type": "object",
    "properties": {"id": {"type": "integer"}},
    "required": ["id"],
    "additionalProperties": False
  },

  "submit_pick": {
    "type": "object",
    "properties": {
      "type": {"type": "string"},
      "pick_id": {"type": "integer"}
    },
    "required": ["type", "pick_id"],
    "additionalProperties": False
  }
}
