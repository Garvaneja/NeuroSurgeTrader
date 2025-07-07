import { useState } from 'react';

export default function StrategyToggle() {
  const [strategy, setStrategy] = useState('RL');

  return (
    <div className="bg-[#1a1a3a] p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-[#00f6ff] mb-4">Trading Strategy</h2>
      <div className="flex space-x-4">
        {['RL', 'Momentum', 'Mean Reversion'].map((mode) => (
          <button
            key={mode}
            onClick={() => setStrategy(mode)}
            className={`px-4 py-2 rounded ${
              strategy === mode ? 'bg-[#00f6ff] text-[#0a0a1a]' : 'bg-[#2a2a4a] text-white hover:bg-[#3a3a5a]'
            }`}
          >
            {mode}
          </button>
        ))}
      </div>
      <p className="mt-4">Current Mode: <span className="font-bold">{strategy}</span></p>
    </div>
  );
}
