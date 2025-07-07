import gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import pandas as pd

class TradingEnv(gym.Env):
    def __init__(self, data: pd.DataFrame, assets: list, initial_capital: float):
        super(TradingEnv, self).__init__()
        self.data = data
        self.assets = assets
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {asset: 0 for asset in assets}
        self.current_step = 0
        self.max_steps = len(data) - 1
        
        # Observation space: [prices, volumes, sentiment, momentum, position_values, capital]
        # 3 assets * (prices + volumes + sentiment + momentum + position_values) + capital = 16
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(16,), dtype=np.float32
        )
        # Action space: [action_type, quantity] per asset (3 assets * 2 = 6)
        self.action_space = gym.spaces.Box(
            low=-1, high=1, shape=(6,), dtype=np.float32
        )
        
        self.prices = {asset: self.data[asset].iloc[self.current_step] for asset in self.assets}

    def reset(self):
        self.capital = self.initial_capital
        self.positions = {asset: 0 for asset in self.assets}
        self.current_step = 0
        self.prices = {asset: self.data[asset].iloc[self.current_step] for asset in self.assets}
        return self._get_observation()

    def _get_observation(self):
        prices = [self.data[asset].iloc[self.current_step] for asset in self.assets]
        volumes = [self.data[f"{asset}_volume"].iloc[self.current_step] for asset in self.assets]
        # Mock sentiment and momentum (real values come from NeuroMemeSurge)
        sentiment = [0.5 for _ in self.assets]  # Placeholder
        momentum = [0.0 for _ in self.assets]   # Placeholder
        position_values = [self.positions[asset] * self.prices[asset] for asset in self.assets]
        return np.array(prices + volumes + sentiment + momentum + position_values + [self.capital], dtype=np.float32)

    def step(self, action):
        self.prices = {asset: self.data[asset].iloc[self.current_step] for asset in self.assets}
        portfolio_value = sum(self.positions[asset] * self.prices[asset] for asset in self.assets) + self.capital
        
        for i, asset in enumerate(self.assets):
            action_type = action[i * 2]
            quantity = abs(action[i * 2 + 1]) * portfolio_value / self.prices[asset]
            
            if action_type > 0.3 and self.capital > quantity * self.prices[asset]:
                self.positions[asset] += quantity
                self.capital -= quantity * self.prices[asset]
            elif action_type < -0.3 and self.positions[asset] > 0:
                sell_quantity = min(quantity, self.positions[asset])
                self.positions[asset] -= sell_quantity
                self.capital += sell_quantity * self.prices[asset]
        
        self.current_step += 1
        done = self.current_step >= self.max_steps
        new_portfolio_value = sum(self.positions[asset] * self.prices[asset] for asset in self.assets) + self.capital
        reward = new_portfolio_value - portfolio_value
        
        return self._get_observation(), reward, done, {}

    def render(self, mode='human'):
        portfolio_value = sum(self.positions[asset] * self.prices[asset] for asset in self.assets) + self.capital
        print(f"Step: {self.current_step}, Portfolio Value: {portfolio_value:.2f}")

class RLTrader:
    def __init__(self, env):
        self.env = DummyVecEnv([lambda: env])
        self.model = PPO("MlpPolicy", self.env, verbose=1)

    def train(self, total_timesteps=50000):
        self.model.learn(total_timesteps=total_timesteps)

    def save(self, path):
        self.model.save(path)

    def load(self, path):
        self.model = PPO.load(path, env=self.env)

    def predict(self, observation):
        action, _ = self.model.predict(observation, deterministic=True)
        return action