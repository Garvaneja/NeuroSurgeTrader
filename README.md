Quantum Trading Hub: NeuroMemeSurge
NeuroMemeSurge is a cutting-edge trading bot using neuro-sentiment reinforcement learning (RL) to trade SOLUSD, DOGEUSD, and SHIBUSD on Kraken with a $300 account. Integrated with a dark, futuristic React website, it targets high alpha (50%+ annualized) by capturing meme coin pumps and Solana surges.
Features

Neuro-Sentiment RL: PPO agent trained on prices, volumes, and simulated X sentiment to maximize returns.
Aggressive Trading: Up to 90% position sizes for high-confidence signals (e.g., DOGE pumps).
Risk Management: 4% stop-loss, 20% max drawdown, 12% volatility filter.
Website: Dashboards for portfolio ($320.50), bot control, backtesting, API keys, and live trades.
Alpha: Targets 150% annualized return, 50% alpha over Solana (80.64%).

Installation

Clone the Repository:
git clone https://github.com/Garvaneja/QuantumHybridBot.git
cd QuantumHybridBot


Set Up Backend:Install Python 3.8+ dependencies:
pip install -r requirements.txt


Set Up Frontend:Ensure Node.js 18+ is installed:
cd frontend
npm install
npm run build


Set Up Kraken API:

Fund Kraken with $300 (https://www.kraken.com).
Generate API keys and enter via the website’s API tab.


File Structure:

frontend/index.html, frontend/App.jsx, frontend/input.css, frontend/tailwind.config.js, frontend/package.json: React frontend.
api_server.py: FastAPI backend.
neuro_meme_surge.py, rl_model.py: RL bot.
kraken_trader.py, config_meme.yaml, requirements.txt: Reused.



Usage

Run Backend:
uvicorn api_server:app --host 0.0.0.0 --port 8000


Run Bot:
python neuro_meme_surge.py


Build and Serve Frontend:
cd frontend
npm run start  # For development (watches changes)

Serve with a local server:
python -m http.server 3000

Or deploy to Vercel:
npm run build
vercel

Access at http://localhost:3000 or Vercel URL.

Interact:

Dashboard: View portfolio, alpha (5%).
Bots: Start NeuroMemeSurge.
Backtest: Test 2025-05-17 to 2025-06-17.
API: Save Kraken keys.
Live: Monitor trades (e.g., Buy 1.2 SOLUSD at $150.25).



Notes

Sentiment: Simulated. Use X API for real data.
Fees: 0.16% Kraken fee impacts $300. Test with $1,000+.
Training: RL model trains in ~10,000 steps (1-2 hours on CPU).
Trial: Run for 30 days, stop if losses hit $60 (20% drawdown).
Frontend: Tailwind CSS is now a local dependency, eliminating CDN warnings.

License
MIT License.
Contact
Open a GitHub issue for support.
