import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class SimpleTradingEnv(gym.Env):
    def __init__(self, df=None, max_steps=500):
        super(SimpleTradingEnv, self).__init__()
        
        self.df = df if df is not None else self._load_default_data()
        self.max_steps = min(max_steps, len(self.df) - 1)
        self.current_step = 0
        self.start_balance = 1000
        self.balance = self.start_balance
        self.position = 0  # +1 if holding, 0 if not
        self.entry_price = 0

        self.observation_space = spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32)
        self.action_space = spaces.Discrete(3)  # 0: Hold, 1: Buy, 2: Sell

    def _load_default_data(self):
        # Default fake price/volume simulation
        data = {
            'price': np.cumsum(np.random.randn(1000)) + 100,
            'volume': np.random.rand(1000) * 1000
        }
        return pd.DataFrame(data)

    def _get_obs(self):
        price = self.df['price'].iloc[self.current_step]
        volume = self.df['volume'].iloc[self.current_step]
        return np.array([price, volume], dtype=np.float32) / 1000  # Normalize

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.balance = self.start_balance
        self.position = 0
        self.entry_price = 0
        return self._get_obs(), {}

    def step(self, action):
        current_price = self.df['price'].iloc[self.current_step]
        reward = 0

        # Buy
        if action == 1 and self.position == 0:
            self.entry_price = current_price
            self.position = 1

        # Sell
        elif action == 2 and self.position == 1:
            profit = current_price - self.entry_price
            reward = profit
            self.balance += profit
            self.position = 0

        self.current_step += 1
        terminated = self.current_step >= self.max_steps
        truncated = False
        obs = self._get_obs()

        return obs, reward, terminated, truncated, {}

    def render(self):
        print(f"Step: {self.current_step}, Balance: {self.balance}, Position: {self.position}")
