import numpy as np
import pandas as pd
import gym
from gym import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from transformers import pipeline

class TradingEnv(gym.Env):
    def __init__(self, data, assets, initial_capital=400.0):
        super(TradingEnv, self).__init__()
        self.data = data
        self.assets = assets
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {asset: 0 for asset in assets}
        self.current_step = 0
        self.max_steps = len(data) - 1
        self.fee_rate = 0.0016
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        
        self.action_space = spaces.Box(low=-1, high=1, shape=(len(assets) * 2,), dtype=np.float32)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(len(assets) * 3 + len(assets) + 1,), dtype=np.float32
        )
    
    def reset(self):
        self.capital = self.initial_capital
        self.positions = {asset: 0 for asset in self.assets}
        self.current_step = 0
        return self._get_observation()
    
    def _get_observation(self):
        prices = [self.data[asset].iloc[self.current_step] for asset in self.assets]
        volumes = [self.data[asset + '_volume'].iloc[self.current_step] if asset + '_volume' in self.data else 0 for asset in self.assets]
        sentiment_scores = [self._get_sentiment_score(asset) for asset in self.assets]
        position_values = [self.positions[asset] * prices[i] for i, asset in enumerate(self.assets)]
        return np.array(prices + volumes + sentiment_scores + position_values + [self.capital])
    
    def _get_sentiment_score(self, asset):
        return np.random.uniform(0.5, 1.5)
    
    def step(self, action):
        prices = [self.data[asset].iloc[self.current_step] for asset in self.assets]
        old_value = self.capital + sum(self.positions[asset] * prices[i] for i, asset in enumerate(self.assets))
        
        for i, asset in enumerate(self.assets):
            action_type = action[i * 2]
            quantity = abs(action[i * 2 + 1]) * self.capital / prices[i]
            if action_type > 0.5 and self.capital > quantity * prices[i]:
                cost = quantity * prices[i] * (1 + self.fee_rate)
                self.capital -= cost
                self.positions[asset] += quantity
            elif action_type < -0.5 and self.positions[asset] > 0:
                sell_quantity = min(quantity, self.positions[asset])
                revenue = sell_quantity * prices[i] * (1 - self.fee_rate)
                self.capital += revenue
                self.positions[asset] -= sell_quantity
        
        self.current_step += 1
        new_value = self.capital + sum(self.positions[asset] * prices[i] for i, asset in enumerate(self.assets))
        reward = (new_value - old_value) / self.initial_capital
        done = self.current_step >= self.max_steps or (self.initial_capital - new_value) / self.initial_capital > 0.2
        info = {"portfolio_value": new_value}
        return self._get_observation(), reward, done, info

class RLTrader:
    def __init__(self, env):
        self.env = DummyVecEnv([lambda: env])
        self.model = PPO("MlpPolicy", self.env, verbose=0)
    
    def train(self, total_timesteps=10000):
        self.model.learn(total_timesteps=total_timesteps)
    
    def predict(self, observation):
        action, _ = self.model.predict(observation)
        return action

    def save(self, path):
        self.model.save(path)
    
    def load(self, path):
        self.model = PPO.load(path, env=self.env)