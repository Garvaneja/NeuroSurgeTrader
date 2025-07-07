export default function BotStatusBadge({ botStatus }) {
  return (
    <div className="flex space-x-4 mt-2">
      <span className="px-4 py-1 bg-[#00f6ff] text-[#0a0a1a] rounded-full font-bold">
        Status: {botStatus.status || 'Unknown'}
      </span>
      <span className="px-4 py-1 bg-[#8b00ff] text-white rounded-full font-bold">
        Alpha: {botStatus.alpha ? `${(botStatus.alpha * 100).toFixed(2)}%` : 'N/A'}
      </span>
    </div>
  );
}
