<template>
  <h2>Жанры</h2>

  <!-- Статистика -->
  <div class="stats-line">
    <div class="stats-left">
      <div class="stat">Количество жанров: {{ genreStats?.count || 0 }}</div>
      <div class="stat">Самый используемый: {{ genreStats?.top || "нет данных" }}</div>
    </div>

    <div class="stats-right">
      <button class="btn btn-success btn-sm me-2" @click="exportGenresExcel">Excel</button>
      <button class="btn btn-primary btn-sm" @click="exportGenresWord">Word</button>
    </div>
  </div>

  <!-- Поиск -->
  <div class="mb-3">
    <input v-model="searchQuery" type="text" class="form-control" placeholder="Поиск по жанрам" @input="filterGenres" />
  </div>

  <!-- Сортировка -->
  <div class="mb-3">
    <select v-model="sortOrder" @change="sortGenres" class="form-select">
      <option value="asc">От A до Я</option>
      <option value="desc">От Я до A</option>
    </select>
  </div>

  <!-- Добавление Жанра (только админ) -->
  <form v-if="isAdmin" class="mb-3" @submit.prevent="onAddGenre">
    <div class="row g-2 align-items-center">
      <div class="col">
        <input v-model="genreToAdd.name" class="form-control" placeholder="Название жанра" required />
      </div>
      <div class="col-auto">
        <button type="submit" class="btn btn-outline-success">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Массовое удаление (только админ) -->
  <div v-if="isAdmin && selectedGenres.length" class="mb-3">
    <button class="btn btn-danger" @click="showDeleteSelectedModal">
      Удалить выбранные ({{ selectedGenres.length }})
    </button>
  </div>

  <!-- Список жанров -->
  <ul class="list-group">
    <li v-for="g in filteredGenres" :key="g.id"
      class="list-group-item d-flex justify-content-between align-items-center"
      :class="{ 'selected': isAdmin && selectedGenres.includes(g.id) }"
      @click="isAdmin && toggleSelection(g.id)">
      <div>{{ g.name }}</div>

      <!-- Кнопки (только админ) -->
      <div v-if="isAdmin">
        <button class="btn btn-sm btn-success me-2" @click.stop="onEditClick(g)">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click.stop="onRemoveClick(g)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модалки -->
  <div class="modal fade" id="editGenreModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактирование жанра</h5>
          <button type="button" class="btn-close" @click="hideEditModal"></button>
        </div>
        <div class="modal-body">
          <input v-model="genreToEdit.name" class="form-control" placeholder="Название жанра" />
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="hideEditModal">Отмена</button>
          <button type="button" class="btn btn-success" @click="onUpdateGenre">Сохранить</button>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="deleteGenreModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Удаление жанра</h5>
          <button type="button" class="btn-close" @click="hideDeleteModal"></button>
        </div>
        <div class="modal-body">
          Вы действительно хотите удалить <strong>{{ genreToDelete.name }}</strong>?
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="hideDeleteModal">Отмена</button>
          <button type="button" class="btn btn-danger" @click="confirmDelete">Удалить</button>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="deleteSelectedModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Удаление выбранных жанров</h5>
          <button type="button" class="btn-close" @click="hideDeleteSelectedModal"></button>
        </div>
        <div class="modal-body">
          Вы действительно хотите удалить <strong>{{ selectedGenres.length }}</strong> жанров?
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="hideDeleteSelectedModal">Отмена</button>
          <button type="button" class="btn btn-danger" @click="confirmDeleteSelected">Удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import axios from "axios";
import * as bootstrap from "bootstrap";

const genres = ref([]);
const filteredGenres = ref([]);
const searchQuery = ref("");
const sortOrder = ref("asc");
const genreStats = ref(null);
const user = ref(null);
const isAdmin = computed(() => user.value?.is_superuser);
const selectedGenres = ref([]);

const genreToAdd = reactive({ name: "" });
const genreToEdit = reactive({ id: null, name: "", modalInstance: null });
const genreToDelete = reactive({ id: null, name: "" });

let deleteModalInstance = null;
let deleteSelectedModalInstance = null;

async function fetchUser() {
  const r = await axios.get("/userprofile/info/");
  user.value = r.data;
}

async function fetchGenres() {
  const r = await axios.get("/genres/");
  genres.value = r.data;
  filterGenres();
}

async function fetchGenreStats() {
  const r = await axios.get("/genres/stats/");
  genreStats.value = r.data;
}

function filterGenres() {
  filteredGenres.value = genres.value.filter((g) =>
    g.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
  sortGenres();
}

function sortGenres() {
  filteredGenres.value.sort((a, b) =>
    sortOrder.value === "asc"
      ? a.name.localeCompare(b.name)
      : b.name.localeCompare(a.name)
  );
}

async function onAddGenre() {
  if (!genreToAdd.name || !isAdmin.value) return;
  await axios.post("/genres/", { ...genreToAdd });
  genreToAdd.name = "";
  await fetchGenres();
  await fetchGenreStats();
}

function onEditClick(g) {
  if (!isAdmin.value) return;
  genreToEdit.id = g.id;
  genreToEdit.name = g.name;
  const modal = document.getElementById("editGenreModal");
  genreToEdit.modalInstance = bootstrap.Modal.getOrCreateInstance(modal);
  genreToEdit.modalInstance.show();
}

async function onUpdateGenre() {
  if (!isAdmin.value || !genreToEdit.id) return;
  await axios.put(`/genres/${genreToEdit.id}/`, { name: genreToEdit.name });
  hideEditModal();
  await fetchGenres();
  await fetchGenreStats();
}

function hideEditModal() {
  if (genreToEdit.modalInstance) genreToEdit.modalInstance.hide();
  document.querySelectorAll(".modal-backdrop").forEach((el) => el.remove());
  genreToEdit.id = null;
  genreToEdit.name = "";
}

function onRemoveClick(g) {
  if (!isAdmin.value) return;
  genreToDelete.id = g.id;
  genreToDelete.name = g.name;
  const modal = document.getElementById("deleteGenreModal");
  deleteModalInstance = bootstrap.Modal.getOrCreateInstance(modal);
  deleteModalInstance.show();
}

async function confirmDelete() {
  if (!isAdmin.value || !genreToDelete.id) return;
  const deletedId = genreToDelete.id;
  await axios.delete(`/genres/${deletedId}/`);
  
  // Убираем удаленный жанр из выделенных
  selectedGenres.value = selectedGenres.value.filter(id => id !== deletedId);
  
  hideDeleteModal();
  await fetchGenres();
  await fetchGenreStats();
}

function hideDeleteModal() {
  if (deleteModalInstance) deleteModalInstance.hide();
  document.querySelectorAll(".modal-backdrop").forEach((el) => el.remove());
  genreToDelete.id = null;
  genreToDelete.name = "";
}

function toggleSelection(id) {
  if (!isAdmin.value) return;
  if (selectedGenres.value.includes(id)) {
    selectedGenres.value = selectedGenres.value.filter((x) => x !== id);
  } else {
    selectedGenres.value.push(id);
  }
}

function showDeleteSelectedModal() {
  if (!isAdmin.value) return;
  const modal = document.getElementById("deleteSelectedModal");
  deleteSelectedModalInstance = bootstrap.Modal.getOrCreateInstance(modal);
  deleteSelectedModalInstance.show();
}

function hideDeleteSelectedModal() {
  if (deleteSelectedModalInstance) deleteSelectedModalInstance.hide();
  document.querySelectorAll(".modal-backdrop").forEach((el) => el.remove());
}

async function confirmDeleteSelected() {
  if (!isAdmin.value) return;
  await Promise.all(
    selectedGenres.value.map((id) => axios.delete(`/genres/${id}/`))
  );
  selectedGenres.value = [];
  hideDeleteSelectedModal();
  await fetchGenres();
  await fetchGenreStats();
}

function exportGenresExcel() { exportData("excel"); }
function exportGenresWord() { exportData("word"); }

function exportData(type = "excel") {
  axios({
    url: `/genres/export/?type=${type}`,
    method: "GET",
    responseType: "blob",
  })
    .then((res) => {
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", type === "excel" ? "genres.xlsx" : "genres.docx");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    })
    .catch(() => alert("Ошибка при скачивании файла"));
}

onMounted(async () => {
  await fetchUser();
  await fetchGenres();
  await fetchGenreStats();
});
</script>

<style scoped>
.stats-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  font-size: 0.9em;
}
.stats-left { display: flex; gap: 12px; }
.stats-right { display: flex; gap: 6px; }
.stat {
  background: #fafafa;
  border: 1px solid #ddd;
  padding: 4px 10px;
  border-radius: 6px;
  color: #333;
}
.list-group-item.selected {
  background-color: #d1e7dd;
  border-color: #0f5132;
  color: #0f5132;
}
</style>