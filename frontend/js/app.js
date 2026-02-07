const API_BASE = "https://leocode.onrender.com/dados";


let currentPage = 1;
const limit = 9;

/* ===============================
   ELEMENTOS
================================ */
const searchInput = document.getElementById("searchInput");
const cargoFilter = document.getElementById("cargoFilter");
const ambitoFilter = document.getElementById("ambitoFilter");
const statusFilter = document.getElementById("statusFilter");
const salarioMinInput = document.getElementById("salarioMin");
const btnBuscar = document.getElementById("btnBuscar");

const cardsContainer = document.getElementById("cards");
const paginationContainer = document.getElementById("pagination");

const skeletonTemplate = document.getElementById("skeleton");

/* ===============================
   BUSCA PRINCIPAL
================================ */
async function buscarDados(page = 1) {
  currentPage = page;
  mostrarSkeleton();

  const params = new URLSearchParams({
    page,
    limit,
    q: searchInput.value.trim(),
    cargo: cargoFilter.value,
    ambito: ambitoFilter.value,
    status: statusFilter.value,
    salario_min: salarioMinInput.value || 0,
  });

  const url = `${API_BASE}/dados?${params.toString()}`;

  try {
    const res = await fetch(url);
    const data = await res.json();

    renderCards(data.results);
    renderPagination(data.page, data.total, data.limit);
  } catch (err) {
    console.error(err);
    cardsContainer.innerHTML = `
      <p class="col-span-full text-center text-red-500">
        Erro ao carregar concursos
      </p>
    `;
  }
}

/* ===============================
   RENDERIZAÇÃO DOS CARDS
================================ */
function renderCards(lista) {
  cardsContainer.innerHTML = "";

  if (!lista || !lista.length) {
    cardsContainer.innerHTML = `
      <p class="col-span-full text-center text-gray-500">
        Nenhum concurso encontrado
      </p>
    `;
    return;
  }

  lista.forEach(item => {
    const salarioNum =
      parseInt((item.salario || "").replace(/\D/g, "")) || 0;

    const emAlta = salarioNum >= 800000;

    const statusBadge =
      item.status === "aberto"
        ? `<span class="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full">🟢 Aberto</span>`
        : `<span class="bg-yellow-100 text-yellow-700 text-xs px-2 py-1 rounded-full">🟡 Previsto</span>`;

    const card = document.createElement("div");
    card.className = `
      bg-white p-4 rounded-xl shadow
      transition-all duration-300 ease-out
      hover:-translate-y-1 hover:shadow-lg
      opacity-0 animate-fadeIn
      flex flex-col justify-between
    `;

    card.innerHTML = `
      <div class="space-y-2">
        <div class="flex items-center justify-between gap-2 flex-wrap">
          ${statusBadge}
          ${
            emAlta
              ? `<span class="bg-orange-100 text-orange-700 text-xs px-2 py-1 rounded-full">🔥 Em alta</span>`
              : ""
          }
        </div>

        <h3 class="font-semibold text-sm text-gray-900">
          ${item.instituicao}
        </h3>

        <p class="text-xs text-gray-600"><strong>Cargo:</strong> ${item.cargo}</p>
        <p class="text-xs text-gray-600"><strong>Âmbito:</strong> ${item.ambito}</p>
        <p class="text-xs text-gray-600"><strong>Salário:</strong> ${item.salario}</p>
        <p class="text-xs text-gray-600">
          <strong>Inscrição até:</strong> ${item.data_inscricao || "—"}
        </p>
      </div>

      <a
        href="${item.link}"
        target="_blank"
        class="mt-4 block text-center bg-blue-600 text-white text-sm py-2 rounded-lg hover:bg-blue-700 transition"
      >
        Ver edital
      </a>
    `;

    cardsContainer.appendChild(card);
  });
}

/* ===============================
   PAGINAÇÃO
================================ */
function renderPagination(page, total, limit) {
  paginationContainer.innerHTML = "";

  const totalPages = Math.ceil(total / limit);
  if (totalPages <= 1) return;

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    btn.className = `
      px-3 py-1 rounded text-sm border
      ${i === page ? "bg-blue-600 text-white" : "bg-white"}
    `;
    btn.onclick = () => buscarDados(i);
    paginationContainer.appendChild(btn);
  }
}

/* ===============================
   SKELETON LOADING
================================ */
function mostrarSkeleton() {
  cardsContainer.innerHTML = "";

  if (!skeletonTemplate) {
    cardsContainer.innerHTML = `
      <p class="col-span-full text-center text-gray-400">
        🔎 Buscando concursos...
      </p>
    `;
    return;
  }

  for (let i = 0; i < limit; i++) {
    const clone = skeletonTemplate.content.cloneNode(true);
    cardsContainer.appendChild(clone);
  }
}

/* ===============================
   EVENTOS
================================ */
btnBuscar.addEventListener("click", () => buscarDados(1));

searchInput.addEventListener("keydown", e => {
  if (e.key === "Enter") buscarDados(1);
});

/* ===============================
   INIT
================================ */
buscarDados();










