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
            </tr>
          `;
          }
        })
        .join("")
      : `
      <tr>
        <td colspan="3">Nenhuma Ordem em produção no momento</td>
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
            </tr>
          `;
          }
        })
        .join("")
      : `
      <tr>
        <td colspan="3">Nenhuma Ordem em produção no momento</td>
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
            </tr>
          `;
          }
        })
        .join("")
      : `
      <tr>
        <td colspan="3">Nenhuma Ordem em produção no momento</td>
      </tr>
    `;
}

async function moveOrder() {
  const orderId = document.getElementById('orderInput').value;
  try {
    const response = await fetch(`/move/${orderId}`);
    const result = await response.text();
    showNotification(result, response.status);
  } catch (error) {
    showNotification(error.message || 'Erro ao mover ordem', 'error');
  }
  loadOrders();
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
