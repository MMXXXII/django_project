<template>
  <div>
    <h2>Жанры</h2>

    <!-- Уведомления -->
    <transition name="notif-fade">
      <div v-if="notification.visible" class="notification" :class="'notification-' + notification.type" role="status"
        aria-live="polite">
        {{ notification.message }}
      </div>
    </transition>

    <!-- Статистика -->
    <div class="stats-line">
      <div class="stats-left">
        <div class="stat">Количество жанров: {{ genreStats?.count || 0 }}</div>
        <div class="stat">Самый используемый жанр: {{ genreStats?.top || "нет данных" }}</div>
      </div>

      <div class="stats-right" v-if="isAdmin">
        <button class="btn btn-success btn-sm me-2" @click="exportGenresExcel">Excel</button>
        <button class="btn btn-primary btn-sm" @click="exportGenresWord">Word</button>
      </div>
    </div>

    <!-- Поиск -->
    <div class="mb-3">
      <input v-model="searchQuery" type="text" class="form-control" placeholder="Поиск по жанрам"
        @input="filterGenres" />
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
        :class="{ 'selected': isAdmin && selectedGenres.includes(g.id) }" @click="isAdmin && toggleSelection(g.id)">
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

// Notification
const notification = reactive({
  visible: false,
  message: '',
  type: 'success',
  _timeoutId: null
});

function showNotification(msg, type = "success", duration = 2000) {
  if (notification._timeoutId) {
    clearTimeout(notification._timeoutId);
    notification._timeoutId = null;
  }
  notification.message = msg;
  notification.type = type;
  notification.visible = true;

  notification._timeoutId = setTimeout(() => {
    notification.visible = false;
    notification._timeoutId = null;
  }, duration);
}

function handleApiError(err, fallbackMessage = 'Ошибка') {
  console.error(err);
  const msg = err?.response?.data?.detail || err?.message || fallbackMessage;
  showNotification(msg, 'danger');
}

async function fetchUser() {
  try {
    const r = await axios.get("/userprofile/info/");
    user.value = r.data;
  } catch (err) {
    handleApiError(err, 'Не удалось получить информацию о пользователе');
  }
}

async function fetchGenres() {
  try {
    const r = await axios.get("/genres/");
    genres.value = r.data;
    filterGenres();
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить список жанров');
  }
}

async function fetchGenreStats() {
  try {
    const r = await axios.get("/genres/stats/");
    genreStats.value = r.data;
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить статистику');
  }
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
  
  try {
    await axios.post("/genres/", { ...genreToAdd });
    genreToAdd.name = "";
    await fetchGenres();
    await fetchGenreStats();
    showNotification('Жанр добавлен', 'success');
  } catch (err) {
    handleApiError(err, 'Ошибка при добавлении жанра');
  }
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
  
  try {
    await axios.put(`/genres/${genreToEdit.id}/`, { name: genreToEdit.name });
    hideEditModal();
    await fetchGenres();
    await fetchGenreStats();
    showNotification('Изменения сохранены', 'warning');
  } catch (err) {
    handleApiError(err, 'Ошибка при обновлении жанра');
  }
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
  
  try {
    const deletedId = genreToDelete.id;
    await axios.delete(`/genres/${deletedId}/`);

    // Убираем удаленный жанр из выделенных
    selectedGenres.value = selectedGenres.value.filter(id => id !== deletedId);

    hideDeleteModal();
    await fetchGenres();
    await fetchGenreStats();
    showNotification('Жанр удален', 'danger');
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении жанра');
  }
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
  
  try {
    await Promise.all(
      selectedGenres.value.map((id) => axios.delete(`/genres/${id}/`))
    );
    selectedGenres.value = [];
    hideDeleteSelectedModal();
    await fetchGenres();
    await fetchGenreStats();
    showNotification('Выбранные жанры удалены', 'danger');
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении выбранных жанров');
  }
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
      showNotification('Файл сформирован, скачивание началось', 'success');
    })
    .catch((err) => {
      handleApiError(err, 'Ошибка при скачивании файла');
    });
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

.stats-left {
  display: flex;
  gap: 12px;
}

.stats-right {
  display: flex;
  gap: 6px;
}

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

/* Notification styles */
.notification {
  position: fixed;
  top: 12px;
  left: 50%;
  transform: translateX(-50%);
  color: #fff;
  padding: 8px 14px;
  border-radius: 8px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
  z-index: 1060;
  font-size: 14px;
  max-width: 90%;
  text-align: center;
}

/* Transition for notification */
.notif-fade-enter-active,
.notif-fade-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.notif-fade-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-8px);
}

.notif-fade-enter-to {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.notif-fade-leave-from {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.notif-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-8px);
}

/* Bootstrap colors */
.notification-success {
  background: #198754;
}

.notification-danger {
  background: #dc3545;
}

.notification-warning {
  background: #ffc107;
  color: #000;
}
</style>