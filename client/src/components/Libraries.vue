<template>
  <h2>Библиотеки</h2>

  <!-- Статистика + кнопки -->
  <div class="stats-line mb-3">
    <div class="stats-left">
      <div class="stat">Количество: {{ libraryStats?.count || 0 }}</div>
      <div class="stat">Среднее: {{ libraryStats?.avg || 0 }}</div>
      <div class="stat">Максимум: {{ libraryStats?.max || 0 }}</div>
      <div class="stat">Минимум: {{ libraryStats?.min || 0 }}</div>
    </div>
    <div class="stats-right">
      <button class="btn btn-success btn-sm me-2" @click="exportLibrariesExcel">Excel</button>
      <button class="btn btn-primary btn-sm" @click="exportLibrariesWord">Word</button>
    </div>
  </div>

  <!-- Поиск -->
  <div class="mb-3">
    <input 
      v-model="searchQuery" 
      type="text" 
      class="form-control" 
      placeholder="Поиск по библиотекам" 
      @input="filterLibraries"
    />
  </div>

  <!-- Сортировка -->
  <div class="mb-3">
    <select v-model="sortOrder" @change="sortLibraries" class="form-select">
      <option value="asc">От A до Я</option>
      <option value="desc">От Я до A</option>
    </select>
  </div>

  <!-- Форма добавления -->
  <form class="mb-3" @submit.prevent="onAddLibrary">
    <div class="row g-2 align-items-center">
      <div class="col">
        <input v-model="libraryToAdd.name" class="form-control" placeholder="Название библиотеки" required />
      </div>
      <div class="col-auto">
        <button type="button" class="btn btn-outline-success" @click="onAddLibrary">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Кнопка массового удаления -->
  <div v-if="selectedLibraries.length" class="mb-3">
    <button class="btn btn-danger" @click="showDeleteSelectedModal">
      Удалить выбранные ({{ selectedLibraries.length }})
    </button>
  </div>

  <!-- Список библиотек -->
  <ul class="list-group">
    <li 
      v-for="l in filteredLibraries" 
      :key="l.id" 
      class="list-group-item d-flex justify-content-between align-items-center"
      :class="{ 'selected': selectedLibraries.includes(l.id) }"
      @click="toggleSelection(l.id)"
    >
      <div>{{ l.name }}</div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click.stop="onEditClick(l)">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click.stop="onRemoveClick(l)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модалки редактирования и удаления -->
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

  <!-- Модалка массового удаления -->
  <div class="modal fade" id="deleteSelectedModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Удаление выбранных библиотек</h5>
          <button type="button" class="btn-close" @click="hideDeleteSelectedModal"></button>
        </div>
        <div class="modal-body">
          Вы действительно хотите удалить <strong>{{ selectedLibraries.length }}</strong> выбранных библиотек?
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
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import * as bootstrap from 'bootstrap'

const libraries = ref([])
const filteredLibraries = ref([])
const libraryStats = ref(null)

const libraryToAdd = reactive({ name: '' })
const libraryToEdit = reactive({ id: null, name: '', modalInstance: null })
const libraryToDelete = reactive({ id: null, name: '' })
const selectedLibraries = ref([])
let deleteModalInstance = null
let deleteSelectedModalInstance = null

const searchQuery = ref('')
const sortOrder = ref('asc')

// --- Получение данных ---
async function fetchLibraries() {
  const r = await axios.get('/libraries/')
  libraries.value = r.data
  filterLibraries()
}

async function fetchLibraryStats() {
  const r = await axios.get('/libraries/stats/')
  libraryStats.value = r.data
}

// --- Фильтр и сортировка ---
function filterLibraries() {
  filteredLibraries.value = libraries.value.filter(l =>
    l.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
  sortLibraries()
}

function sortLibraries() {
  filteredLibraries.value.sort((a, b) => {
    const A = a.name.toLowerCase()
    const B = b.name.toLowerCase()
    return sortOrder.value === 'asc' ? A.localeCompare(B) : B.localeCompare(A)
  })
}

// --- Добавление ---
async function onAddLibrary() {
  if (!libraryToAdd.name) return
  await axios.post('/libraries/', { ...libraryToAdd })
  libraryToAdd.name = ''
  await fetchLibraries()
  await fetchLibraryStats()
}

// --- Редактирование ---
function onEditClick(l) {
  libraryToEdit.id = l.id
  libraryToEdit.name = l.name
  const modalEl = document.getElementById('editLibraryModal')
  libraryToEdit.modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  libraryToEdit.modalInstance.show()
}

async function onUpdateLibrary() {
  if (!libraryToEdit.id) return
  await axios.put(`/libraries/${libraryToEdit.id}/`, { name: libraryToEdit.name })
  await fetchLibraries()
  await fetchLibraryStats()
  hideEditModal()
}

function hideEditModal() {
  if (libraryToEdit.modalInstance) libraryToEdit.modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  libraryToEdit.id = null
  libraryToEdit.name = ''
}

// --- Удаление одного ---
function onRemoveClick(l) {
  libraryToDelete.id = l.id
  libraryToDelete.name = l.name
  const modalEl = document.getElementById('deleteLibraryModal')
  deleteModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  deleteModalInstance.show()
}

async function confirmDelete() {
  if (!libraryToDelete.id) return
  await axios.delete(`/libraries/${libraryToDelete.id}/`)
  await fetchLibraries()
  await fetchLibraryStats()
  hideDeleteModal()
}

function hideDeleteModal() {
  if (deleteModalInstance) deleteModalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  libraryToDelete.id = null
  libraryToDelete.name = ''
}

// --- Выделение ---
function toggleSelection(id) {
  if (selectedLibraries.value.includes(id)) {
    selectedLibraries.value = selectedLibraries.value.filter(x => x !== id)
  } else {
    selectedLibraries.value.push(id)
  }
}

// --- Модалка массового удаления ---
function showDeleteSelectedModal() {
  const modalEl = document.getElementById('deleteSelectedModal')
  deleteSelectedModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  deleteSelectedModalInstance.show()
}

function hideDeleteSelectedModal() {
  if (deleteSelectedModalInstance) deleteSelectedModalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

// --- Массовое удаление ---
async function confirmDeleteSelected() {
  if (!selectedLibraries.value.length) return
  await Promise.all(selectedLibraries.value.map(id => axios.delete(`/libraries/${id}/`)))
  selectedLibraries.value = []
  await fetchLibraries()
  await fetchLibraryStats()
  hideDeleteSelectedModal()
}

// --- Экспорт данных ---
function exportLibrariesExcel() {
  exportLibraries('excel')
}

function exportLibrariesWord() {
  exportLibraries('word')
}

function exportLibraries(type = 'excel') {
  axios({
    url: `/libraries/export/?type=${type}`,
    method: 'GET',
    responseType: 'blob'
  }).then(response => {
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', type === 'excel' ? 'libraries.xlsx' : 'libraries.docx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }).catch(err => {
    console.error('Ошибка при скачивании:', err)
    alert('Ошибка при скачивании файла')
  })
}

// --- Инициализация ---
onMounted(async () => {
  await Promise.all([fetchLibraries(), fetchLibraryStats()])
})
</script>

<style scoped>
.stats-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

/* Подсветка выделенных библиотек */
.list-group-item.selected {
  background-color: #d1e7dd;
  border-color: #0f5132;
  color: #0f5132;
}
</style>
