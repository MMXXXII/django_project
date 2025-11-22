<template>
  <h2>Библиотеки</h2>

  <!-- Статистика -->
  <div class="stats-line mb-3">
    <div class="stat">Количество: {{ libraryStats?.count || 0 }}</div>
    <div class="stat">Среднее: {{ libraryStats?.avg || 0 }}</div>
    <div class="stat">Максимум: {{ libraryStats?.max || 0 }}</div>
    <div class="stat">Минимум: {{ libraryStats?.min || 0 }}</div>
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

  <!-- Модалка редактирования -->
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

  <!-- Модалка удаления -->
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
  if (libraryToEdit.modalInstance) {
    libraryToEdit.modalInstance.hide()
    libraryToEdit.modalInstance = null
  }
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  libraryToEdit.id = null
  libraryToEdit.name = ''
}

// --- Удаление ---
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

// --- Инициализация ---
onMounted(async () => {
  await Promise.all([fetchLibraries(), fetchLibraryStats()])
})
</script>

<style scoped>
.stats-line {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
  font-size: 0.9em;
}
.stat {
  background: #fafafa;
  border: 1px solid #ddd;
  padding: 4px 10px;
  border-radius: 6px;
  color: #333;
}
</style>
