const API_BASE = "https://leocode.onrender.com";

let currentPage = 1;
const limit = 9;
let debounceTimer;

/* ELEMENTOS */
const searchInput = document.getElementById("searchInput");
const cargoFilter = document.getElementById("cargoFilter");
const ambitoFilter = document.getElementById("ambitoFilter");
const statusFilter = document.getElementById("statusFilter");
const salarioMinInput = document.getElementById("salarioMin");
const btnBuscar = document.getElementById("btnBuscar");
const ordenacaoSelect = document.getElementById("ordenacao");

const cardsContainer = document.getElementById("cards");
const paginationContainer = document.getElementById("pagination");
const skeletonTemplate = document.getElementById("skeleton");

/* FAVORITOS */
function getFavoritos() {
  return JSON.parse(localStorage.getItem("favoritos") || "[]");
}
function toggleFavorito(link) {
  let favs = getFavoritos();
  favs = favs.includes(link) ? favs.filter(f => f !== link) : [...favs, link];
  localStorage.setItem("favoritos", JSON.stringify(favs));
  buscarDados(currentPage);
}

/* BUSCA */
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
    ordenacao: ordenacaoSelect?.value || ""
  });

  const res = await fetch(`${API_BASE}/dados?${params.toString()}`);
  const data = await res.json();

  renderCards(data.results);
  renderPagination(data.page, data.total, data.limit);
}

/* CARDS */
function renderCards(lista) {
  cardsContainer.innerHTML = "";
  if (!lista || !lista.length) {
    cardsContainer.innerHTML = `<p class="col-span-full text-center text-gray-500">Nenhum concurso encontrado</p>`;
    return;
  }

  const favs = getFavoritos();

  lista.forEach(item => {
    const salarioNum = parseInt((item.salario || "").replace(/\D/g, "")) || 0;
    if (salarioNum < (salarioMinInput.value || 0) * 100) return;

    const emAlta = salarioNum >= 800000;
    const isFav = favs.includes(item.link);

    const card = document.createElement("div");
    card.className = "bg-white p-4 rounded-xl shadow hover:-translate-y-1 hover:shadow-lg transition animate-fadeIn flex flex-col justify-between";

    card.innerHTML = `
      <div class="space-y-2">
        <div class="flex gap-2 flex-wrap">
          <span class="text-xs px-2 py-1 rounded-full ${item.status === "aberto" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}">
            ${item.status === "aberto" ? "🟢 Aberto" : "🟡 Previsto"}
          </span>
          ${emAlta ? `<span class="bg-orange-100 text-orange-700 text-xs px-2 py-1 rounded-full">🔥 Em alta</span>` : ""}
        </div>

        <h3 class="font-semibold text-sm">${item.instituicao}</h3>
        <p class="text-xs">Cargo: ${item.cargo}</p>
        <p class="text-xs">Âmbito: ${item.ambito}</p>
        <p class="text-xs">Salário: ${item.salario}</p>
        <p class="text-xs">Inscrição até: ${item.data_inscricao || "—"}</p>

        <button onclick="toggleFavorito('${item.link}')" class="text-xs ${isFav ? "text-yellow-600" : "text-gray-400"}">
          ⭐ ${isFav ? "Favorito" : "Favoritar"}
        </button>
      </div>

      <a href="${item.link}" target="_blank"
        class="mt-4 bg-blue-600 text-white text-sm py-2 rounded-lg text-center hover:bg-blue-700">
        Ver edital
      </a>
    `;
    cardsContainer.appendChild(card);
  });
}

/* PAGINAÇÃO */
function renderPagination(page, total, limit) {
  paginationContainer.innerHTML = "";
  const totalPages = Math.ceil(total / limit);
  if (totalPages <= 1) return;

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    btn.className = `px-3 py-1 border rounded ${i === page ? "bg-blue-600 text-white" : ""}`;
    btn.onclick = () => buscarDados(i);
    paginationContainer.appendChild(btn);
  }
}

/* SKELETON */
function mostrarSkeleton() {
  cardsContainer.innerHTML = "";
  for (let i = 0; i < limit; i++) {
    cardsContainer.appendChild(skeletonTemplate.content.cloneNode(true));
  }
}

/* EVENTOS */
btnBuscar.addEventListener("click", () => buscarDados(1));
searchInput.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => buscarDados(1), 400);
});
ordenacaoSelect?.addEventListener("change", () => buscarDados(1));

/* INIT */
buscarDados();
