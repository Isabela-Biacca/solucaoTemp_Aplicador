function parseLog(content) {
  return content
    .split("\n")
    .map((line) => {
      const match = line.match(/\[(.*?)\]\s(.*)/);
      if (!match) return null;

      const [_, timestamp, message] = match;
      let status = "OK";
      let order = "-";

      if (message.includes("Erro crítico")) status = "ERROR";
      if (message.includes("ignorada") || message.includes("Falha"))
        status = "WARN";

      const orderMatch = message.match(/Ordem\s(\d+)/);
      if (orderMatch) order = orderMatch[1];

      return {
        timestamp,
        order,
        message: message.replace(/(Ordem \d+|Erro crítico:)\s?/, ""),
        status,
      };
    })
    .filter(Boolean);
}

let table;
async function loadLogs(date) {
  try {
    const response = await fetch(`/get_log?date=${date || ""}`);
    const data = await response.json();

    if (data.error) throw new Error(data.error);

    const logs = parseLog(data.content);

    if ($.fn.DataTable.isDataTable("#logsTable")) {
      table.destroy();
    }

    table = $("#logsTable").DataTable({
      data: logs,
      pageLength: 10,
      language: {
        url: "//cdn.datatables.net/plug-ins/1.11.5/i18n/pt-BR.json",
      },
      columns: [
        { data: "timestamp" },
        { data: "order" },
        { data: "message" },
        {
          data: "status",
          render: function (data) {
            return `<span class="status status-${data.toLowerCase()}">${data}</span>`;
          },
        },
      ],
      initComplete: function () {
        // Aplica filtros iniciais
        $("#filterOrder").on("keyup", function () {
          table.column(1).search(this.value).draw();
        });

        $("#filterStatus").on("change", function () {
          table.column(3).search(this.value).draw();
        });
      },
    });
  } catch (error) {
    alert(error.message);
  }
}

// Event Listeners
document.getElementById("filterDate").addEventListener("change", () => {
  loadLogs(document.getElementById("filterDate").value);
});

// Initial load
const today = new Date().toISOString().split("T")[0];
document.getElementById("filterDate").value = today;
loadLogs(today);
