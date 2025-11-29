<template>
  <div>
    <h2>Библиотеки</h2>

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
        <div class="stat">Количество библиотек: {{ libraryStats?.count || 0 }}</div>
        <div class="stat">Самая используемая библиотека: {{ libraryStats?.top || "нет данных" }}</div>
      </div>

      <div class="stats-right" v-if="isAdmin">
        <button class="btn btn-success btn-sm me-2" @click="exportLibrariesExcel">Excel</button>
        <button class="btn btn-primary btn-sm" @click="exportLibrariesWord">Word</button>
      </div>
    </div>

    <!-- Поиск -->
    <div class="mb-3">
      <input v-model="searchQuery" type="text" class="form-control" placeholder="Поиск по библиотекам"
        @input="filterLibraries" />
    </div>

    <!-- Сортировка -->
    <div class="mb-3">
      <select v-model="sortOrder" @change="sortLibraries" class="form-select">
        <option value="asc">От A до Я</option>
        <option value="desc">От Я до A</option>
      </select>
    </div>

    <!-- Добавление (только админ) -->
    <form v-if="isAdmin" class="mb-3" @submit.prevent="onAddLibrary">
      <div class="row g-2 align-items-center">
        <div class="col">
          <input v-model="libraryToAdd.name" class="form-control" placeholder="Название библиотеки" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-outline-success">Добавить</button>
        </div>
      </div>
    </form>

    <!-- Массовое удаление (только админ) -->
    <div v-if="isAdmin && selectedLibraries.length" class="mb-3">
      <button class="btn btn-danger" @click="showDeleteSelectedModal">
        Удалить выбранные ({{ selectedLibraries.length }})
      </button>
    </div>

    <!-- Список библиотек -->
    <ul class="list-group">
      <li v-for="l in filteredLibraries" :key="l.id"
        class="list-group-item d-flex justify-content-between align-items-center"
        :class="{ 'selected': isAdmin && selectedLibraries.includes(l.id) }" @click="isAdmin && toggleSelection(l.id)">
        <div>{{ l.name }}</div>

        <!-- Кнопки (только админ) -->
        <div v-if="isAdmin">
          <button class="btn btn-sm btn-success me-2" @click.stop="onEditClick(l)">
            <i class="bi bi-pen-fill"></i>
          </button>
          <button class="btn btn-sm btn-danger" @click.stop="onRemoveClick(l)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </li>
    </ul>

    <!-- Модалки -->
    <div class="modal fade" id="editLibraryModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактирование библиотеки</h5>
            <button type="button" class="btn-close" @click="hideEditModal"></button>
          </div>
          <div class="modal-body">
            <input v-model="libraryToEdit.name" class="form-control" placeholder="Название библиотеки" />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideEditModal">Отмена</button>
            <button type="button" class="btn btn-success" @click="onUpdateLibrary">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="deleteLibraryModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Удаление библиотеки</h5>
            <button type="button" class="btn-close" @click="hideDeleteModal"></button>
          </div>
          <div class="modal-body">
            Вы действительно хотите удалить <strong>{{ libraryToDelete.name }}</strong>?
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
            <h5 class="modal-title">Удаление выбранных библиотек</h5>
            <button type="button" class="btn-close" @click="hideDeleteSelectedModal"></button>
          </div>
          <div class="modal-body">
            Вы действительно хотите удалить <strong>{{ selectedLibraries.length }}</strong> библиотек?
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

// --- State ---
const libraries = ref([]);
const filteredLibraries = ref([]);
const searchQuery = ref("");
const sortOrder = ref("asc");
const libraryStats = ref(null);
const user = ref(null);
const isAdmin = computed(() => user.value?.is_superuser);
const selectedLibraries = ref([]);

const libraryToAdd = reactive({ name: "" });
const libraryToEdit = reactive({ id: null, name: "", modalInstance: null });
const libraryToDelete = reactive({ id: null, name: "" });

let deleteModalInstance = null;
let deleteSelectedModalInstance = null;

// --- Notification ---
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

// --- Fetchers ---
async function fetchUser() {
  try {
    const r = await axios.get("/userprofile/info/");
    user.value = r.data;
  } catch (err) {
    handleApiError(err, 'Не удалось получить информацию о пользователе');
  }
}

async function fetchLibraries() {
  try {
    const r = await axios.get("/libraries/");
    libraries.value = r.data;
    filterLibraries();
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить список библиотек');
  }
}

async function fetchLibraryStats() {
  try {
    const r = await axios.get("/libraries/stats/");
    libraryStats.value = r.data;
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить статистику');
  }
}

// --- Filter/Sort ---
function filterLibraries() {
  filteredLibraries.value = libraries.value.filter((l) =>
    l.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
  sortLibraries();
}

function sortLibraries() {
  filteredLibraries.value.sort((a, b) =>
    sortOrder.value === "asc" ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name)
  );
}

// --- CRUD ---
async function onAddLibrary() {
  if (!libraryToAdd.name || !isAdmin.value) return;
  
  try {
    await axios.post("/libraries/", { ...libraryToAdd });
    libraryToAdd.name = "";
    await fetchLibraries();
    await fetchLibraryStats();
    showNotification('Библиотека добавлена', 'success');
  } catch (err) {
    handleApiError(err, 'Ошибка при добавлении библиотеки');
  }
}

function onEditClick(l) {
  if (!isAdmin.value) return;
  libraryToEdit.id = l.id;
  libraryToEdit.name = l.name;
  const modal = document.getElementById("editLibraryModal");
  libraryToEdit.modalInstance = bootstrap.Modal.getOrCreateInstance(modal);
  libraryToEdit.modalInstance.show();
}

async function onUpdateLibrary() {
  if (!isAdmin.value || !libraryToEdit.id) return;
  
  try {
    await axios.put(`/libraries/${libraryToEdit.id}/`, { name: libraryToEdit.name });
    hideEditModal();
    await fetchLibraries();
    await fetchLibraryStats();
    showNotification('Изменения сохранены', 'warning');
  } catch (err) {
    handleApiError(err, 'Ошибка при обновлении библиотеки');
  }
}

function hideEditModal() {
  if (libraryToEdit.modalInstance) libraryToEdit.modalInstance.hide();
  document.querySelectorAll(".modal-backdrop").forEach((el) => el.remove());
  libraryToEdit.id = null;
  libraryToEdit.name = "";
}

function onRemoveClick(l) {
  if (!isAdmin.value) return;
  libraryToDelete.id = l.id;
  libraryToDelete.name = l.name;
  const modal = document.getElementById("deleteLibraryModal");
  deleteModalInstance = bootstrap.Modal.getOrCreateInstance(modal);
  deleteModalInstance.show();
}

async function confirmDelete() {
  if (!isAdmin.value || !libraryToDelete.id) return;
  
  try {
    const deletedId = libraryToDelete.id;
    await axios.delete(`/libraries/${deletedId}/`);

    selectedLibraries.value = selectedLibraries.value.filter(id => id !== deletedId);

    hideDeleteModal();
    await fetchLibraries();
    await fetchLibraryStats();
    showNotification('Библиотека удалена', 'danger');
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении библиотеки');
  }
}

function hideDeleteModal() {
  if (deleteModalInstance) deleteModalInstance.hide();
  document.querySelectorAll(".modal-backdrop").forEach((el) => el.remove());
  libraryToDelete.id = null;
  libraryToDelete.name = "";
}

function toggleSelection(id) {
  if (!isAdmin.value) return;
  if (selectedLibraries.value.includes(id)) {
    selectedLibraries.value = selectedLibraries.value.filter((x) => x !== id);
  } else {
    selectedLibraries.value.push(id);
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
    await Promise.all(selectedLibraries.value.map((id) => axios.delete(`/libraries/${id}/`)));
    selectedLibraries.value = [];
    hideDeleteSelectedModal();
    await fetchLibraries();
    await fetchLibraryStats();
    showNotification('Выбранные библиотеки удалены', 'danger');
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении выбранных библиотек');
  }
}

// --- Export ---
function exportLibrariesExcel() { exportData("excel"); }
function exportLibrariesWord() { exportData("word"); }

function exportData(type = "excel") {
  axios({
    url: `/libraries/export/?type=${type}`,
    method: "GET",
    responseType: "blob",
  })
    .then((res) => {
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", type === "excel" ? "libraries.xlsx" : "libraries.docx");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showNotification('Файл сформирован, скачивание началось', 'success');
    })
    .catch((err) => {
      handleApiError(err, 'Ошибка при скачивании файла');
    });
}

// --- Init ---
onMounted(async () => {
  await fetchUser();
  await fetchLibraries();
  await fetchLibraryStats();
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