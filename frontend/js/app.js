const API_BASE = "https://leocode.onrender.com";

fetch(`${API_BASE}/dados?page=1&limit=9`)


/* ELEMENTOS */
const searchInput = document.getElementById("searchInput");
const ambitoFilter = document.getElementById("ambitoFilter");
const frequenciaFilter = document.getElementById("frequenciaFilter");
const cargoFilter = document.getElementById("cargoFilter");
const salarioMinInput = document.getElementById("salarioMin");
const ordenacaoSelect = document.getElementById("ordenacao");
const btnBuscar = document.getElementById("btnBuscar");

const container = document.getElementById("cardsContainer");
const historicoEl = document.getElementById("historico");
const paginacaoEl = document.getElementById("paginacao");

let currentPage = 1;
const LIMIT = 9;

/* ===================== UTIL ===================== */

function salarioNumero(s) {
    if (!s || s === "Não informado") return 0;
    return parseInt(
        s.replace("R$", "")
            .replace(/\./g, "")
            .replace(",", "")
            .trim()
    ) || 0;
}

function calcularScore(i) {
    let score = 0;

    const sal = salarioNumero(i.salario);
    if (sal >= 8000) score += 40;
    else if (sal >= 5000) score += 30;
    else if (sal >= 3000) score += 20;
    else if (sal > 0) score += 10;

    if (i.cargo === "Professor") score += 20;
    else if (i.cargo === "Administrativo") score += 15;

    if (i.ambito === "Federal") score += 20;
    else if (i.ambito === "Estadual") score += 15;
    else if (i.ambito === "Municipal") score += 10;

    if (i.data_inscricao) score += 10;
    if (i.link && i.link.startsWith("http")) score += 10;

    return score;
}

/* ===================== SKELETON ===================== */

function mostrarSkeleton(qtd = 6) {
    container.innerHTML = "";
    const tpl = document.getElementById("skeleton");
    for (let i = 0; i < qtd; i++) {
        container.appendChild(tpl.content.cloneNode(true));
    }
}

/* ===================== BUSCA ===================== */

async function buscarDados(salvarNoHistorico = true) {
    mostrarSkeleton();

    const params = new URLSearchParams();

    if (searchInput.value) params.append("q", searchInput.value);
    if (ambitoFilter.value) params.append("ambito", ambitoFilter.value);
    
    if (cargoFilter.value) params.append("cargo", cargoFilter.value);
    if (salarioMinInput.value) params.append("salario_min", salarioMinInput.value);

    params.append("page", currentPage);
    params.append("limit", LIMIT);

    try {
        const res = await fetch(`${API_URL}?${params.toString()}`);
        const data = await res.json();

        console.log("DATA COMPLETA:", data);
        console.log("RESULTADOS:", data.results);
       



        let lista = data.results.map(i => ({
            ...i,
            score: calcularScore(i)
        }));

        /* ORDENAÇÃO */
        if (ordenacaoSelect.value === "salario") {
            lista.sort((a, b) => salarioNumero(b.salario) - salarioNumero(a.salario));
        } else if (ordenacaoSelect.value === "frequencia") {
            lista.sort((a, b) => (a.frequencia || "").localeCompare(b.frequencia || ""));
        } else {
            lista.sort((a, b) => b.score - a.score);
        }

        renderCards(lista);
        renderPaginacao(data.total);
         console.log("LISTA FINAL PARA RENDER:", lista);

        if (salvarNoHistorico) salvarHistorico();
    } catch (e) {
        console.error("ERRO REAL:", e);
        container.innerHTML =
            "<pre style='color:red'>" + e + "</pre>";
    }
}



/* ===================== CARDS ===================== */

function renderCards(lista) {
    container.innerHTML = "";

    if (!lista.length) {
        container.innerHTML =
            "<p class='text-gray-500'>Nenhum resultado encontrado.</p>";
        return;
    }

    lista.forEach((i, index) => {
        container.innerHTML += `
        <div class="bg-white p-5 rounded-lg shadow space-y-2">

            ${index === 0 ? `
            <span class="text-xs font-bold text-purple-700 bg-white-100 px-2 py-1 p-10 m-1 rounded">
                 Melhor oportunidade
            </span>` : ""}

            ${i.score >= 80 ? `
            <span class="text-xs font-semibold text-red-700 bg-black-100 px-2 py-1 rounded">
                Destaque
            </span>` : ""}

            <h2 class="font-semibold text-sm">${i.instituicao}</h2>

            <p class="text-sm"><strong>Cargo:</strong> ${i.cargo}</p>
            <p class="text-sm"><strong>Salário:</strong> ${i.salario}</p>
            <p class="text-sm"><strong>Carga Horaria:</strong> ${i.frequencia}</p>
            <p class="text-sm"><strong>Âmbito:</strong> ${i.ambito}</p>

            ${i.link ? `
            <a href="${i.link}" target="_blank"
               class="inline-block text-sm text-blue-600 hover:underline">
                 Ir ao edital
            </a>` : ""}
        </div>
        `;
    });
}

/* ===================== PAGINAÇÃO ===================== */

function renderPaginacao(total) {
    const totalPages = Math.ceil(total / LIMIT);
    paginacaoEl.innerHTML = "";

    if (totalPages <= 1) return;

    for (let i = 1; i <= totalPages; i++) {
        paginacaoEl.innerHTML += `
            <button
                class="px-3 py-1 border rounded
                ${i === currentPage ? "bg-blue-600 text-white" : ""}"
                onclick="trocarPagina(${i})">
                ${i}
            </button>
        `;
    }
}

function trocarPagina(p) {
    currentPage = p;
    buscarDados(false);
}

/* ===================== HISTÓRICO ===================== */

function salvarHistorico() {
    const texto = searchInput.value;
    if (!texto) return;

    let hist = JSON.parse(localStorage.getItem("buscas")) || [];

    hist.unshift({
        texto,
        ambito: ambitoFilter.value,
        cargo: cargoFilter.value
    });

    hist = hist.slice(0, 5);
    localStorage.setItem("buscas", JSON.stringify(hist));
    carregarHistorico();
}

function carregarHistorico() {
    historicoEl.innerHTML = "";

    (JSON.parse(localStorage.getItem("buscas")) || []).forEach(h => {
        const li = document.createElement("li");
        li.textContent = `${h.texto} ${h.ambito ? "• " + h.ambito : ""}`;
        li.className = "cursor-pointer text-blue-600 hover:underline";
        li.onclick = () => {
            searchInput.value = h.texto;
            ambitoFilter.value = h.ambito;
            cargoFilter.value = h.cargo;
            currentPage = 1;
            buscarDados(false);
        };
        historicoEl.appendChild(li);
    });
}

/* ===================== EVENTOS ===================== */

btnBuscar.onclick = async () => {
    currentPage = 1;

    try {
        
       await fetch("https://leocode-2.onrender.com/atualizar", {
   method: "POST"
       });

        // pequena espera (opcional)
        setTimeout(() => {
            buscarDados();
        }, 2000);

    } catch (e) {
        console.error("Erro ao atualizar:", e);
        buscarDados(); // fallback
    }
};


/* INIT */
buscarDados();
carregarHistorico();












