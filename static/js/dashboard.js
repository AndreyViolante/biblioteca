// Lê o JSON escrito pelo json_script e desenha um gráfico de barras.
function desenhar(idDados, idCanvas, horizontal) {
  const origem = document.getElementById(idDados);
  if (!origem) return; // o operador não recebe a série por mês
  const dados = JSON.parse(origem.textContent);
  const canvas = document.getElementById(idCanvas);

  // Sem dados, ou sem internet para carregar o Chart.js: mostra em texto.
  if (dados.length === 0 || typeof Chart === 'undefined') {
    const p = document.createElement('p');
    p.className = 'suave';
    p.textContent = dados.length
      ? dados.map(d => `${d.rotulo}: ${d.total}`).join(' · ')
      : 'Sem dados no período.';
    canvas.parentElement.replaceWith(p);
    return;
  }

  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: dados.map(d => d.rotulo),
      datasets: [{ data: dados.map(d => d.total), backgroundColor: '#24577a', borderRadius: 4, maxBarThickness: 34 }]
    },
    options: {
      indexAxis: horizontal ? 'y' : 'x',
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { [horizontal ? 'x' : 'y']: { beginAtZero: true, ticks: { precision: 0 } } }
    }
  });
}

desenhar('dados-mes', 'graf-mes', false);
desenhar('dados-categoria', 'graf-categoria', true);
