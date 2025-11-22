<template>
  <h2>Жанры</h2>

  <!-- Статистика + кнопки -->
  <div class="stats-line">
    <!-- Статистика слева -->
    <div class="stats-left">
      <div class="stat">Количество: {{ genreStats?.count || 0 }}</div>
      <div class="stat">Среднее: {{ genreStats?.avg || 0 }}</div>
      <div class="stat">Максимум: {{ genreStats?.max || 0 }}</div>
      <div class="stat">Минимум: {{ genreStats?.min || 0 }}</div>
    </div>

    <!-- Кнопки справа -->
    <div class="stats-right">
      <button class="btn btn-success btn-sm me-2" @click="exportGenresExcel">Excel</button>
      <button class="btn btn-primary btn-sm" @click="exportGenresWord">Word</button>
    </div>
  </div>

  <!-- Поиск -->
  <div class="mb-3">
    <input 
      v-model="searchQuery" 
      type="text" 
      class="form-control" 
      placeholder="Поиск по жанрам" 
      @input="filterGenres"
    />
  </div>

  <!-- Сортировка -->
  <div class="mb-3">
    <select v-model="sortOrder" @change="sortGenres" class="form-select">
      <option value="asc">От A до Я</option>
      <option value="desc">От Я до A</option>
    </select>
  </div>

  <!-- Форма добавления -->
  <form class="mb-3" @submit.prevent="onAddGenre">
    <div class="row g-2 align-items-center">
      <div class="col">
        <input v-model="genreToAdd.name" class="form-control" placeholder="Название жанра" required />
      </div>
      <div class="col-auto">
        <button type="button" class="btn btn-outline-success" @click="onAddGenre">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Список жанров -->
  <ul class="list-group">
    <li v-for="g in filteredGenres" :key="g.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>{{ g.name }}</div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(g)">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemoveClick(g)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модалки редактирования и удаления -->
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
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import * as bootstrap from 'bootstrap'

const genres = ref([])
const filteredGenres = ref([])
const genreStats = ref(null)

const genreToAdd = reactive({ name: '' })
const genreToEdit = reactive({ id: null, name: '', modalInstance: null })
const genreToDelete = reactive({ id: null, name: '' })
let deleteModalInstance = null

const searchQuery = ref('')
const sortOrder = ref('asc')

// --- Получение данных ---
async function fetchGenres() {
  const r = await axios.get('/genres/')
  genres.value = r.data
  filterGenres()
}

async function fetchGenreStats() {
  const r = await axios.get('/genres/stats/')
  genreStats.value = r.data
}

// --- Фильтр и сортировка ---
function filterGenres() {
  filteredGenres.value = genres.value.filter(g =>
    g.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
  sortGenres()
}

function sortGenres() {
  filteredGenres.value.sort((a, b) => {
    const A = a.name.toLowerCase()
    const B = b.name.toLowerCase()
    return sortOrder.value === 'asc' ? A.localeCompare(B) : B.localeCompare(A)
  })
}

// --- Добавление ---
async function onAddGenre() {
  if (!genreToAdd.name) return
  await axios.post('/genres/', { ...genreToAdd })
  genreToAdd.name = ''
  await fetchGenres()
  await fetchGenreStats()
}

// --- Редактирование ---
function onEditClick(g) {
  genreToEdit.id = g.id
  genreToEdit.name = g.name
  const modalEl = document.getElementById('editGenreModal')
  genreToEdit.modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  genreToEdit.modalInstance.show()
}

async function onUpdateGenre() {
  if (!genreToEdit.id) return
  await axios.put(`/genres/${genreToEdit.id}/`, { name: genreToEdit.name })
  await fetchGenres()
  await fetchGenreStats()
  hideEditModal()
}

function hideEditModal() {
  if (genreToEdit.modalInstance) genreToEdit.modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  genreToEdit.id = null
  genreToEdit.name = ''
}

// --- Удаление ---
function onRemoveClick(g) {
  genreToDelete.id = g.id
  genreToDelete.name = g.name
  const modalEl = document.getElementById('deleteGenreModal')
  deleteModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  deleteModalInstance.show()
}

async function confirmDelete() {
  if (!genreToDelete.id) return
  await axios.delete(`/genres/${genreToDelete.id}/`)
  await fetchGenres()
  await fetchGenreStats()
  hideDeleteModal()
}

function hideDeleteModal() {
  if (deleteModalInstance) deleteModalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  genreToDelete.id = null
  genreToDelete.name = ''
}

// --- Экспорт ---
function exportGenresExcel() {
  exportData('excel')
}
function exportGenresWord() {
  exportData('word')
}
function exportData(type = 'excel') {
  axios({
    url: `/genres/export/?type=${type}`,
    method: 'GET',
    responseType: 'blob'
  }).then(res => {
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', type === 'excel' ? 'genres.xlsx' : 'genres.docx')
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
  await Promise.all([fetchGenres(), fetchGenreStats()])
})
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
</style>
