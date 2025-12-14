

import json
import os
from typing import Callable
from server.utils.achievement import achievement_manager, unlock_achievement
from server.utils.logger import logger
from server.utils.pubsub import pubsub

class User:
  def __init__(self, username: str):
    self.username = username
    self.statistics = {}
    self.achievements = {}
    self.init_achievements()

    def add_statistics_listener(data, scope):
      self.add_statistics(data["key"], data["value"])
    pubsub.subscribe(f"add_statistics", add_statistics_listener, self.username)
    def set_statistics_listener(data, scope):
      self.set_statistics(data["key"], data["value"])
    pubsub.subscribe(f"set_statistics", set_statistics_listener, self.username)
  
  def add_statistics(self, key: str, value: int):
    if key not in self.statistics:
      self.statistics[key] = 0
    self.statistics[key] += value
    self.check_statistics(key, self.statistics[key])

  def set_statistics(self, key: str, value: int):
    self.statistics[key] = value
    self.check_statistics(key, self.statistics[key])

  def check_statistics(self, key: str, value: int):
    if key == "wins":
      if value >= 1:
        unlock_achievement(self.username, "king_of_scw1")
    if key == "games_played":
      if value >= 1:
        unlock_achievement(self.username, "first_time")
    if key == "slave":
      if value >= 1:
        unlock_achievement(self.username, "slave_of_scw1")
    if key == "caylion_colonies":
      if value >= 1:
        unlock_achievement(self.username, "caylion_a_small_step")
    if key == "yengii_tech_invented":
      if value >= 1:
        unlock_achievement(self.username, "yengii_first_tech")
    if key == "tech_invented":
      if value >= 100:
        unlock_achievement(self.username, "tech_100")

  def init_achievements(self):
    for achievement_id in achievement_manager.get_all_achievements():
      if achievement_id not in self.achievements:
        self.achievements[achievement_id] = False
    for achievement_id in list(self.achievements.keys()):
      if achievement_id not in achievement_manager.get_all_achievements():
        del self.achievements[achievement_id]
    for achievement_id in self.achievements:
      if not self.achievements[achievement_id]:
        def make_listener(aid):
          def listener(data, scope):
            self.achievements[aid] = True
            pubsub.unsubscribe(f"achievement_{aid}", listener, self.username)
          return listener
        listener = make_listener(achievement_id)
        pubsub.subscribe(f"achievement_{achievement_id}", listener, self.username)
  def to_dict(self):
    return {
      "username": self.username,
      "achievements": self.achievements
    }

  def from_dict(data: dict):
    user = User(data["username"])
    user.achievements = data["achievements"]
    return user

class UserManager:
  def __init__(self):
    self.users = {}

    user_data_path = './server/data/users.json'
    if os.path.exists(user_data_path):
      with open(user_data_path, 'r') as f:
        users_dict = json.load(f)
        self.users = {username: User.from_dict(user_dict) for username, user_dict in users_dict.items()}

  def get_user(self, username: str) -> User:
    if username not in self.users:
      self.users[username] = User(username)
    return self.users[username]
  
  def save_users(self):
    if not os.path.exists('./server/data'):
      os.makedirs('./server/data')
    with open('./server/data/users.json', 'w') as f:
      users_dict = {username: user.to_dict() for username, user in self.users.items()}
      json.dump(users_dict, f)

user_manager = UserManager()
