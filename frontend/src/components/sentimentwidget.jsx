export default function SentimentWidget({ sentiment }) {
  const assets = ['SOLUSD', 'DOGEUSD', 'SHIBUSD'];

  return (
    <div className="bg-[#1a1a3a] p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-[#00f6ff] mb-4">Live Sentiment Scores</h2>
      <ul className="space-y-3">
        {assets.map((asset, i) => (
          <li key={asset} className="flex justify-between">
            <span>{asset}</span>
            <span className={`font-bold ${sentiment[i] > 0.6 ? 'text-green-400' : sentiment[i] < 0.4 ? 'text-red-400' : 'text-yellow-300'}`}>
              {(sentiment[i] * 100).toFixed(1)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
