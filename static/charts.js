// CricVision Charts.js helpers
// Dark theme compatible

function createShotPieChart(canvasId, shotData) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: shotData.labels || ['Cover Drive', 'Pull Shot', 'Late Cut', 'Defensive'],
      datasets: [{
        data: shotData.data || [30, 25, 20, 25],
        backgroundColor: [
          '#10b981', // emerald
          '#6366f1', // indigo
          '#f59e0b', // amber
          '#6b7280'  // gray
        ],
        borderColor: '#0a0f1c',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: {
            color: '#f8fafc',
            font: { size: 14 }
          }
        }
      },
      scales: {
        y: { display: false }
      }
    }
  });
}

function createLeaderboardBarChart(canvasId, userData) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: userData.labels || ['User1', 'User2', 'User3'],
      datasets: [{
        label: 'Analyses',
        data: userData.data || [15, 12, 10],
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: '#10b981',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          ticks: { color: '#94a3b8' },
          grid: { color: 'rgba(255,255,255,0.1)' }
        },
        x: {
          ticks: { color: '#f8fafc' },
          grid: { display: false }
        }
      },
      plugins: {
        legend: {
          labels: { color: '#f8fafc' }
        }
      }
    }
  });
}

function createAnalysisLineChart(canvasId, timeData) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: timeData.labels || ['Jan', 'Feb', 'Mar', 'Apr'],
      datasets: [{
        label: 'Analyses',
        data: timeData.data || [5, 10, 8, 15],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          ticks: { color: '#94a3b8' },
          grid: { color: 'rgba(255,255,255,0.1)' }
        },
        x: {
          ticks: { color: '#f8fafc' }
        }
      },
      plugins: {
        legend: { labels: { color: '#f8fafc' } }
      }
    }
  });
}
