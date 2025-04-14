async function loadOrders() {
  const response = await fetch("/api/orders");
  const data = await response.json();

  bw = [];
  pc = [];
  hc = [];

  data.input.forEach((order) => {
    if (order.linha.startsWith("S")) {
      bw.push(order);
    } else if (order.linha.startsWith("D")) {
      pc.push(order);
    } else if (order.linha.startsWith("A")) {
      hc.push(order);
    }
  });

  // Ordenar BW (linhas S) numericamente
  bw.sort((a, b) => {
    const numA = parseInt(a.linha.replace(/^\D+/g, '')),
      numB = parseInt(b.linha.replace(/^\D+/g, ''));
    return numA - numB;
  });

  // Ordenar PC (linhas D) numericamente
  pc.sort((a, b) => {
    const numA = parseInt(a.linha.replace(/^\D+/g, '')),
      numB = parseInt(b.linha.replace(/^\D+/g, ''));
    return numA - numB;
  });

  // Ordenar HC (linhas A) numericamente
  hc.sort((a, b) => {
    const numA = parseInt(a.linha.replace(/^\D+/g, '')),
      numB = parseInt(b.linha.replace(/^\D+/g, ''));
    return numA - numB;
  });

  document.getElementById("bw-table").innerHTML =
    bw.length > 0
      ? bw
        .map((order) => {
          // Verifica se a linha começa com "S"
          if (order.linha.startsWith("S")) {
            return `
            <tr>
              <td>${order.linha}</td>
              <td>${order.op}</td>
              <td>${order.sku}</td>
              <td>${order.data}</td>
              <td>
                <button class="btn-encerrar" onclick="encerrarOrdem('${order.op}', this)">Encerrar</button>
              </td>
            </tr>
          `;
          }
        })
        .join("")
      : `
      <tr>
        <td colspan="5">Nenhuma Ordem em produção no momento</td>
      </tr>
    `;

  document.getElementById("pc-table").innerHTML =
    pc.length > 0
      ? pc
        .map((order) => {
          // Verifica se a linha começa com "D"
          if (order.linha.startsWith("D")) {
            return `
            <tr>
              <td>${order.linha}</td>
              <td>${order.op}</td>
              <td>${order.sku}</td>
              <td>${order.data}</td>
              <td>
                <button class="btn-encerrar" onclick="encerrarOrdem('${order.op}', this)">Encerrar</button>
              </td>
            </tr>
          `;
          }
        })
        .join("")
      : `
      <tr>
        <td colspan="5">Nenhuma Ordem em produção no momento</td>
      </tr>
    `;

  document.getElementById("hc-table").innerHTML =
    hc.length > 0
      ? hc
        .map((order) => {
          // Verifica se a linha começa com "A
          if (order.linha.startsWith("A")) {
            return `
            <tr>
              <td>${order.linha}</td>
              <td>${order.op}</td>
              <td>${order.sku}</td>
              <td>${order.data}</td>
              <td>
                <button class="btn-encerrar" onclick="encerrarOrdem('${order.op}', this)">Encerrar</button>
              </td>
            </tr>
          `;
          }
        })
        .join("")
      : `
      <tr>
        <td colspan="5">Nenhuma Ordem em produção no momento</td>
      </tr>
    `;
}

async function moveOrder() {
  const orderId = document.getElementById('orderInput').value;

  try {
    const response = await fetch(`/move/${orderId}`);
    const result = await response.json();
    showNotification(result.message, response.status);
  } catch (error) {
    showNotification(error.message || 'Erro ao mover ordem', 'error');
  }
  loadOrders();
}

document.getElementById('orderInput').addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    e.preventDefault(); // Impede o comportamento padrão do formulário
    moveOrder();
  }
});

function moveOrderAndClear() {
  moveOrder(); // Chama a função para mover a ordem
  document.getElementById('orderInput').value = ""; // Limpa o campo de input
}

async function encerrarOrdem(orderId, button) {
  if (!confirm(`Deseja realmente encerrar a ordem ${orderId}?`)) return;

  button.disabled = true;
  button.textContent = 'Processando...';

  try {
    debugger
    const response = await fetch(`/encerrar/${orderId}`);
    const result = await response.json();
    showNotification(result.message, response.status);
    loadOrders();
  } catch (error) {
    showNotification(error.message || 'Erro ao encerrar ordem', 'error');
  } finally {
    button.disabled = false;
    button.textContent = 'Encerrar';
  }
}

// index.js
async function recoverOrder() {
  const orderId = document.getElementById('recoverInput').value;

  try {
    debugger
    const response = await fetch(`/recuperar/${orderId}`);
    const result = await response.json();
    showNotification(result.message, response.status);

    // Forçar processamento automático pelo observer
    setTimeout(loadOrders, 2000); // Aguardar 2s para atualização
  } catch (error) {
    showNotification(error.message || 'Erro ao recuperar ordem', 'error');
  }
}

document.getElementById('recoverInput').addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    e.preventDefault();
    recoverOrderAndClear();
  }
});

function recoverOrderAndClear() {
  recoverOrder();
  document.getElementById('recoverInput').value = "";
}

function showNotification(message, type = 'warning') {
  const notification = document.getElementById('notification');
  const notificationText = document.getElementById('notification-text');

  // Cores baseadas no tipo
  const colors = {
    404: '#ffd700',
    500: '#dc3545',
    200: '#28a745'
  };

  notification.style.backgroundColor = colors[type];
  notificationText.textContent = message;
  notification.style.display = 'block';

  // Fecha automaticamente após 5 segundos
  setTimeout(closeNotification, 5000);
}

function closeNotification() {
  document.getElementById('notification').style.display = 'none';
}

setInterval(loadOrders, 5000); // Atualiza a cada 5 segundos
loadOrders();
