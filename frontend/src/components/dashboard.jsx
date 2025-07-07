import TradeChart from './TradeChart';

export default function Dashboard({ portfolio }) {
  return (
    <div className="bg-[#1a1a3a] p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-[#00f6ff] mb-4">Portfolio Overview</h2>
      <p className="mb-2">Portfolio Value: ${portfolio.portfolio_value?.toFixed(2) || '0.00'}</p>
      <p className="mb-2">Last Trade: {portfolio.last_trade ? `${portfolio.last_trade.asset} ${portfolio.last_trade.type} at ${portfolio.last_trade.price}` : 'None'}</p>
      <div className="mt-6">
        <TradeChart portfolio={portfolio} />
      </div>
    </div>
  );
}
