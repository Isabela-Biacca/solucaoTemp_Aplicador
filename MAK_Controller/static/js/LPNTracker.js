async function loadLpns() {
    const loading = document.getElementById("loading");

    loading.style.display = "block"; // mostra "carregando"

    const response = await fetch("/api/lpn");
    const data = await response.json();

    LM = [];
    SM = [];
    Lib = [];
    Oct = [];

    data.forEach((lpn) => {
        if (lpn.aplicador == "Leitor Movel") {
            LM.push(lpn);
        } else if (lpn.aplicador == "San Martin") {
            SM.push(lpn);
        } else if (lpn.aplicador == "Liberty") {
            Lib.push(lpn);
        } else if (lpn.aplicador == "Octopus") {
            Oct.push(lpn);
        }
    });

    loading.style.display = "none"; // esconde "carregando"

    document.getElementById("loadLM").innerHTML =
        LM.length > 0
            ? LM
                .map((lpn) => {
                    return `
                        <tr>
                            <td>${lpn.numLpn}</td>
                            <td>${lpn.op}</td>
                            <td>${lpn.sku}</td>
                            <td>${lpn.data}</td>
                        </tr>
                    `;
                })
                .join("")
            : `
                <tr>
                    <td colspan="4">Todas LPNs já foram enviadas para o MES.</td>
                </tr>
            `;

    document.getElementById("loadSM").innerHTML =
        SM.length > 0
            ? SM
                .map((lpn) => {
                    return `
                        <tr>
                            <td>${lpn.numLpn}</td>
                            <td>${lpn.op}</td>
                            <td>${lpn.sku}</td>
                            <td>${lpn.data}</td>
                        </tr>
                    `;

                })
                .join("")
            : `
                <tr>
                    <td colspan="4">Todas LPNs já foram enviadas para o MES.</td>
                </tr>
            `;

    document.getElementById("loadLib").innerHTML =
        Lib.length > 0
            ? Lib
                .map((lpn) => {
                    return `
                        <tr>
                            <td>${lpn.numLpn}</td>
                            <td>${lpn.op}</td>
                            <td>${lpn.sku}</td>
                            <td>${lpn.data}</td>
                        </tr>
                    `;
                })
                .join("")
            : `
                <tr>
                    <td colspan="4">Todas LPNs já foram enviadas para o MES.</td>
                </tr>
            `;

    document.getElementById("loadOct").innerHTML =
        Oct.length > 0
            ? Oct
                .map((lpn) => {
                    return `
                        <tr>
                            <td>${lpn.numLpn}</td>
                            <td>${lpn.op}</td>
                            <td>${lpn.sku}</td>
                            <td>${lpn.data}</td>
                        </tr>
                    `;
                })
                .join("")
            : `
                <tr>
                    <td colspan="4">Todas LPNs já foram enviadas para o MES.</td>
                </tr>
            `;


}

const itemsPerPage = 5;

let currentPageLM = 1;
let currentPageSM = 1;
let currentPageLib = 1;
let currentPageOct = 1;

let LM = [], SM = [], Lib = [], Oct = [];

async function searchLpn() {
    const loading = document.getElementById("loading");

    loading.style.display = "block"; // mostra "carregando"

    const query = document.getElementById("search").value;
    const response = await fetch(`/api/search?q=${query}`);
    const data = await response.json();

    LM = [], SM = [], Lib = [], Oct = [];

    data.forEach((lpn) => {
        switch (lpn.aplicador) {
            case "Leitor Movel": LM.push(lpn); break;
            case "San Martin": SM.push(lpn); break;
            case "Liberty": Lib.push(lpn); break;
            case "Octopus": Oct.push(lpn); break;
        }
    });

    loading.style.display = "none"; // esconde "carregando"

    renderTableSection(LM, currentPageLM, "searchLM");
    renderTableSection(SM, currentPageSM, "searchSM");
    renderTableSection(Lib, currentPageLib, "searchLib");
    renderTableSection(Oct, currentPageOct, "searchOct");

    renderPagination(LM, "paginationLM", "LM");
    renderPagination(SM, "paginationSM", "SM");
    renderPagination(Lib, "paginationLib", "Lib");
    renderPagination(Oct, "paginationOct", "Oct");

}

function renderTableSection(array, currentPage, elementId) {
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageItems = array.slice(start, end);

    document.getElementById(elementId).innerHTML =
        pageItems.length > 0
            ? pageItems.map(lpn => `
                <tr>
                    <td>${lpn.origem}</td>
                    <td>${lpn.numLpn}</td>
                    <td>${lpn.op}</td>
                    <td>${lpn.sku}</td>
                    <td>${lpn.data}</td>
                </tr>
            `).join("")
            : `<tr><td colspan="5">Nenhuma LPN encontrada.</td></tr>`;
}

function renderPagination(array, containerId, sectionKey) {
    const totalPages = Math.ceil(array.length / itemsPerPage);
    const pagination = document.getElementById(containerId);
    pagination.innerHTML = "";

    if (totalPages <= 1) return;

    let currentPageVar;
    switch (sectionKey) {
        case "LM": currentPageVar = currentPageLM; break;
        case "SM": currentPageVar = currentPageSM; break;
        case "Lib": currentPageVar = currentPageLib; break;
        case "Oct": currentPageVar = currentPageOct; break;
    }

    const setCurrentPage = (page) => {
        switch (sectionKey) {
            case "LM": currentPageLM = page; break;
            case "SM": currentPageSM = page; break;
            case "Lib": currentPageLib = page; break;
            case "Oct": currentPageOct = page; break;
        }

        renderTableSection(array, page, `search${sectionKey}`);
        renderPagination(array, containerId, sectionKey);
    };

    const createButton = (label, onClick, disabled = false) => {
        const btn = document.createElement("button");
        btn.innerHTML = label;
        btn.disabled = disabled;
        btn.onclick = onClick;
        btn.style.width = "min-content";
        btn.style.opacity = btn.disabled ? "0.5" : "1";
        btn.style.cursor = btn.disabled ? "default" : "pointer";
        btn.classList.toggle("paginationHover", !btn.disabled);
        return btn;
    };

    pagination.appendChild(
        createButton("<<", () => setCurrentPage(1), currentPageVar === 1)
    );

    pagination.appendChild(
        createButton("<", () => setCurrentPage(currentPageVar - 1), currentPageVar === 1)
    );

    pagination.appendChild(
        createButton(">", () => setCurrentPage(currentPageVar + 1), currentPageVar === totalPages)
    );

    pagination.appendChild(
        createButton(">>", () => setCurrentPage(totalPages), currentPageVar === totalPages)
    );
}

function loadLpnExec() {
    loadLpns();
    document.querySelector(".searchedLpns").style.display = "none";
    document.querySelector(".loadedLpns").style.display = "flex";
}

function searchLpnExec() {
    searchLpn();
    document.querySelector(".loadedLpns").style.display = "none";
    document.querySelector(".searchedLpns").style.display = "flex";
}

function clearSearch() {
    document.getElementById("search").value = "";
    searchLpnExec();
}

document.getElementById('search').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        e.preventDefault(); // Impede o comportamento padrão do formulário
        searchLpnExec();
    }
});

loadLpnExec();