import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from simple_trading_env import SimpleTradingEnv
import os

# Create environment
env = SimpleTradingEnv()

# Check environment compatibility
check_env(env)

# Create PPO model
model = PPO("MlpPolicy", env, verbose=1)

# Train the model
model.learn(total_timesteps=50000)

# Save model
model_save_path = "neuro_rl_model"
os.makedirs(model_save_path, exist_ok=True)
model.save(f"{model_save_path}/ppo_neuro_trader")

# Optional: evaluate the trained model
obs, _ = env.reset()
for _ in range(100):
    action, _ = model.predict(obs)
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        obs, _ = env.reset()
