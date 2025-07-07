new Chart(ctx, {
  type: "line",
  data: {
    labels: ["Day 0", "Day 5", "Day 10", "Day 15", "Day 20", "Day 25", "Day 30"],
    datasets: [
      {
        label: "Portfolio Value ($)",
        data: [300, 312.0, 325.5, 338.0, 347.2, 354.8, 360.0],
        borderColor: "#00f6ff",
        backgroundColor: "rgba(0, 246, 255, 0.2)",
        fill: true
      },
      {
        label: "Benchmark (SOLUSD, $)",
        data: [300, 304.8, 309.6, 314.4, 319.2, 324.0, 328.8],
        borderColor: "#ff6d00",
        backgroundColor: "rgba(255, 109, 0, 0.2)",
        fill: true
      }
    ]
  },
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: "NeuroMemeSurge vs. SOLUSD (30 Days)",
        color: "#e0e0ff"
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Time (Days)",
          color: "#e0e0ff"
        }
      },
      y: {
        title: {
          display: true,
          text: "Value ($)",
          color: "#e0e0ff"
        },
        beginAtZero: false
      }
    }
  }
});
