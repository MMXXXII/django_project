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

  <!-- Список библиотек -->
  <ul class="list-group">
    <li v-for="l in filteredLibraries" :key="l.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>{{ l.name }}</div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(l)">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemoveClick(l)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модалки редактирования и удаления остаются без изменений -->
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
let deleteModalInstance = null

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

// --- Добавление / редактирование / удаление ---
async function onAddLibrary() {
  if (!libraryToAdd.name) return
  await axios.post('/libraries/', { ...libraryToAdd })
  libraryToAdd.name = ''
  await fetchLibraries()
  await fetchLibraryStats()
}

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
</style>
