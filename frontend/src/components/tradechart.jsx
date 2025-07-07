import { useEffect, useRef } from 'react';
import { Chart } from 'chart.js/auto';

export default function TradeChart({ portfolio }) {
  const chartRef = useRef(null);

  useEffect(() => {
    const ctx = chartRef.current.getContext('2d');
    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['SOLUSD', 'DOGEUSD', 'SHIBUSD'],
        datasets: [{
          label: 'Asset Holdings ($)',
          data: [
            (portfolio.positions?.SOLUSD || 0) * 150,
            (portfolio.positions?.DOGEUSD || 0) * 0.15,
            (portfolio.positions?.SHIBUSD || 0) * 0.000011,
          ],
          backgroundColor: ['#00f6ff', '#ff00ff', '#00ff00'],
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Position Value Chart',
            color: '#e0e0ff'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              color: '#e0e0ff'
            }
          },
          x: {
            ticks: {
              color: '#e0e0ff'
            }
          }
        }
      }
    });
    return () => chart.destroy();
  }, [portfolio]);

  return <canvas ref={chartRef} height="200"></canvas>;
}
