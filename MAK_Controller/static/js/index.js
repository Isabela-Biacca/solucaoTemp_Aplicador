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
  const orderId = document.getElementById("orderInput").value;
  const response = await fetch(`/move/${orderId}`);
  alert(await response.text());
  loadOrders(); // Atualiza a lista após mover
}

// Atualizar alertas a cada 30 segundos
function updateAlerts() {
  fetch("/api/pending_actions")
    .then((response) => response.json())
    .then((data) => {
      const container = document.querySelector(".alert-container");
      const list = document.getElementById("alertList");

      if (data.alerts && data.alerts.length > 0) {
        container.style.display = "block";
        list.innerHTML = data.alerts
          .map(
            (alert) =>
              `<div style="margin: 10px 0; padding: 10px; background: white; border-radius: 3px;">
                    ${alert}
                </div>`
          )
          .join("");
      } else {
        container.style.display = "none";
      }
    });
}

setInterval(updateAlerts, 30000);
updateAlerts(); // Carrega inicialmente

setInterval(loadOrders, 5000); // Atualiza a cada 5 segundos
loadOrders();
