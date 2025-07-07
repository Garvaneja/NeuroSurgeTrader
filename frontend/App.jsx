import { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './src/components/Dashboard';
import SentimentWidget from './src/components/SentimentWidget';
import StrategyToggle from './src/components/StrategyToggle';
import TradeChart from './src/components/TradeChart';
import BotStatusBadge from './src/components/BotStatusBadge';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [portfolio, setPortfolio] = useState(null);
  const [botStatus, setBotStatus] = useState(null);
  const [sentiment, setSentiment] = useState([0.5, 0.5, 0.5]);
  const [config, setConfig] = useState(null);

  const fetchLiveBotData = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/portfolio');
      console.log('[Live Fetch] Portfolio:', res.data);
      setPortfolio(res.data);
      setBotStatus(res.data);
    } catch (err) {
      console.error('[Live Fetch Error]', err);
    }
  };

  const fetchConfig = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/config');
      console.log('[Config Fetch]', res.data);
      setConfig(res.data);
    } catch (err) {
      console.error('[Config Fetch Error]', err);
    }
  };

  useEffect(() => {
    fetchLiveBotData();
    fetchConfig();
    const refresh = setInterval(() => {
      fetchLiveBotData();
      fetchConfig();
    }, 10000);
    return () => clearInterval(refresh);
  }, []);

  const isActive = botStatus?.status === 'Running' || portfolio?.last_trade;

  return (
    <div className="min-h-screen bg-[#0a0a1a] text-[#e0e0ff] p-6">
      <header className="mb-8">
        <h1 className="text-5xl font-bold text-[#00f6ff]">NeuroMemeSurge</h1>
        {botStatus ? (
          <div className="flex items-center gap-4 mt-2">
            <BotStatusBadge botStatus={botStatus} />
            <span className={`px-3 py-1 rounded-full font-bold text-sm ${
              isActive ? 'bg-green-500 text-black' : 'bg-yellow-400 text-black'
            }`}>
              {isActive ? 'ACTIVE' : 'IDLE'}
            </span>
          </div>
        ) : (
          <p className="text-red-500">Bot not running</p>
        )}
      </header>

      <nav className="mb-4 flex gap-4">
        {['dashboard', 'sentiment', 'strategy'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded ${
              activeTab === tab
                ? 'bg-[#00f6ff] text-[#0a0a1a]'
                : 'bg-[#1a1a3a] text-[#e0e0ff] hover:bg-[#2a2a4a]'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </nav>

      <main>
        {!portfolio ? (
          <p className="text-yellow-400">Waiting for bot to sync...</p>
        ) : (
          <>
            {portfolio.last_trade ? (
              <div className="mb-4 bg-black text-green-400 p-3 rounded">
                <strong>Last Trade:</strong> {portfolio.last_trade.asset} — {portfolio.last_trade.type.toUpperCase()} {portfolio.last_trade.quantity} @ ${portfolio.last_trade.price}
              </div>
            ) : (
              <p className="mb-4 text-yellow-300">No trades yet.</p>
            )}
            <pre className="text-sm text-green-400 bg-black p-4 rounded max-h-64 overflow-y-auto">
              {JSON.stringify(portfolio, null, 2)}
            </pre>
            {config && (
              <div className="mt-4 text-sm bg-[#111] text-cyan-300 p-4 rounded">
                <h3 className="font-bold mb-2">Live Config</h3>
                <pre>{JSON.stringify(config, null, 2)}</pre>
              </div>
            )}
            {activeTab === 'dashboard' && <Dashboard portfolio={portfolio} />}
            {activeTab === 'sentiment' && <SentimentWidget sentiment={sentiment} />}
            {activeTab === 'strategy' && <StrategyToggle />}
          </>
        )}
      </main>
    </div>
  );
}
