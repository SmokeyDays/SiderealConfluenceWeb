import json
import os

from server.utils.log import logger
from server.utils.pubsub import pubsub


class Achievement:
  def __init__(self, id: str, name: str, scope: str, description: str, hint: str, difficulty: int):
    self.id = id
    self.name = name
    self.scope = scope
    self.description = description
    self.hint = hint
    self.difficulty = difficulty

  def to_dict(self):
    return {
      "id": self.id,
      "name": self.name,
      "scope": self.scope,
      "description": self.description,
      "hint": self.hint,
      "difficulty": self.difficulty
    }
  
  def from_dict(data: dict):
    return Achievement(data["id"], data["name"], data["scope"], data["description"], data["hint"], data["difficulty"])

def load_achievements():
  achievements = {}
  achievement_data_path = './server/utils/src/achievements.txt'
  if os.path.exists(achievement_data_path):
    with open(achievement_data_path, 'r', encoding='utf-8') as f:
      for line in f:
        if line.strip() == "":
          continue
        id, name, scope, description, hint, difficulty = line.split('\t')
        achievements[id] = Achievement(id, name, scope, description, hint, int(difficulty))
  return achievements

class AchievementManager:
  def __init__(self):
    self.achievements = load_achievements()
  def get_achievement(self, id: str):
    return self.achievements[id]

  def get_all_achievements(self):
    return list(self.achievements.keys())
  
achievement_manager = AchievementManager()

def unlock_achievement(username: str, achievement_id: str):
  pubsub.publish(f"achievement_{achievement_id}", None, username)
  pubsub.publish(f"add_achievement", {"id": achievement_id, "username": username})
  logger.info(f"{username} 解锁了成就 {achievement_id}")
