<template>
  <h2>Книги</h2>

  <!-- Статистика + кнопки -->
  <div class="stats-line">
    <!-- Статистика слева -->
    <div class="stats-left">
      <div class="stat">Количество: {{ bookStats?.count || 0 }}</div>
      <div class="stat">Среднее: {{ bookStats?.avg || 0 }}</div>
      <div class="stat">Максимум: {{ bookStats?.max || 0 }}</div>
      <div class="stat">Минимум: {{ bookStats?.min || 0 }}</div>
    </div>

    <!-- Кнопки справа -->
    <div class="stats-right">
      <button class="btn btn-success btn-sm me-2" @click="exportBooksExcel">Excel</button>
      <button class="btn btn-primary btn-sm" @click="exportBooksWord">Word</button>
    </div>
  </div>

  <!-- Поиск -->
  <div class="mb-3">
    <input 
      v-model="searchQuery" 
      type="text" 
      class="form-control" 
      placeholder="Поиск по книгам" 
      @input="filterBooks"
    />
  </div>

  <!-- Сортировка -->
  <div class="mb-3">
    <select v-model="sortOrder" @change="sortBooks" class="form-select">
      <option value="asc">От A до Я</option>
      <option value="desc">От Я до A</option>
    </select>
  </div>

  <!-- Форма добавления -->
  <form class="mb-3" @submit.prevent="onAddBook">
    <div class="row g-2 align-items-center">
      <div class="col">
        <input v-model="bookToAdd.title" class="form-control" placeholder="Название книги" required />
      </div>
      <div class="col">
        <select v-model="bookToAdd.genre" class="form-select" required>
          <option value="" disabled>Выберите жанр</option>
          <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </div>
      <div class="col">
        <select v-model="bookToAdd.library" class="form-select" required>
          <option value="" disabled>Выберите библиотеку</option>
          <option v-for="l in libraries" :key="l.id" :value="l.id">{{ l.name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <button type="submit" class="btn btn-outline-success">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Список книг -->
  <ul class="list-group">
    <li 
      v-for="b in filteredBooks" 
      :key="b.id" 
      class="list-group-item d-flex justify-content-between align-items-center"
    >
      <div>
        <strong>{{ b.title }}</strong>
        <div class="text-muted small">{{ b.genre_name }} / {{ b.library_name }}</div>
      </div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(b)">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemoveClick(b)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модалки редактирования и удаления -->
  <div class="modal fade" id="editBookModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактирование книги</h5>
          <button type="button" class="btn-close" @click="hideEditModal"></button>
        </div>
        <div class="modal-body">
          <input v-model="bookToEdit.title" class="form-control mb-2" placeholder="Название книги" />
          <select v-model="bookToEdit.genre" class="form-select mb-2">
            <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
          <select v-model="bookToEdit.library" class="form-select">
            <option v-for="l in libraries" :key="l.id" :value="l.id">{{ l.name }}</option>
          </select>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="hideEditModal">Отмена</button>
          <button type="button" class="btn btn-success" @click="onUpdateBook">Сохранить</button>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="deleteBookModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Удаление книги</h5>
          <button type="button" class="btn-close" @click="hideDeleteModal"></button>
        </div>
        <div class="modal-body">
          Вы действительно хотите удалить <strong>{{ bookToDelete.title }}</strong>?
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

const books = ref([])
const filteredBooks = ref([])
const bookStats = ref(null)
const genres = ref([])
const libraries = ref([])

// Добавление / редактирование
const bookToAdd = reactive({ title: '', genre: null, library: null })
const bookToEdit = reactive({ id: null, title: '', genre: null, library: null, modalInstance: null })

// Удаление
const bookToDelete = reactive({ id: null, title: '' })
let deleteModalInstance = null

const searchQuery = ref('')
const sortOrder = ref('asc')

// --- API функции ---
async function fetchBooks() {
  const r = await axios.get('/books/')
  books.value = r.data.map(b => ({
    ...b,
    genre_name: b.genre_name || b.genre,
    library_name: b.library_name || b.library
  }))
  filterBooks()
}

async function fetchBookStats() {
  const r = await axios.get('/books/stats/')
  bookStats.value = r.data
}

async function fetchGenres() {
  const r = await axios.get('/genres/')
  genres.value = r.data
}

async function fetchLibraries() {
  const r = await axios.get('/libraries/')
  libraries.value = r.data
}

// --- Фильтр / сортировка ---
function filterBooks() {
  filteredBooks.value = books.value.filter(b =>
    b.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
  sortBooks()
}

function sortBooks() {
  filteredBooks.value.sort((a, b) => {
    const A = a.title.toLowerCase()
    const B = b.title.toLowerCase()
    return sortOrder.value === 'asc' ? A.localeCompare(B) : B.localeCompare(A)
  })
}

// --- Добавление ---
async function onAddBook() {
  if (!bookToAdd.genre || !bookToAdd.library) return alert('Выберите жанр и библиотеку')
  await axios.post('/books/', { 
    title: bookToAdd.title,
    genre: bookToAdd.genre,
    library: bookToAdd.library
  })
  bookToAdd.title = ''
  bookToAdd.genre = null
  bookToAdd.library = null
  await fetchBooks()
  await fetchBookStats()
}

// --- Редактирование ---
function onEditClick(b) {
  bookToEdit.id = b.id
  bookToEdit.title = b.title
  bookToEdit.genre = b.genre
  bookToEdit.library = b.library
  const modalEl = document.getElementById('editBookModal')
  bookToEdit.modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  bookToEdit.modalInstance.show()
}

async function onUpdateBook() {
  if (!bookToEdit.id) return
  await axios.put(`/books/${bookToEdit.id}/`, { 
    title: bookToEdit.title,
    genre: bookToEdit.genre,
    library: bookToEdit.library
  })
  await fetchBooks()
  await fetchBookStats()
  hideEditModal()
}

function hideEditModal() {
  if (bookToEdit.modalInstance) bookToEdit.modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  bookToEdit.id = null
  bookToEdit.title = ''
  bookToEdit.genre = null
  bookToEdit.library = null
}

// --- Удаление ---
function onRemoveClick(b) {
  bookToDelete.id = b.id
  bookToDelete.title = b.title
  const modalEl = document.getElementById('deleteBookModal')
  deleteModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  deleteModalInstance.show()
}

async function confirmDelete() {
  if (!bookToDelete.id) return
  await axios.delete(`/books/${bookToDelete.id}/`)
  await fetchBooks()
  await fetchBookStats()
  hideDeleteModal()
}

function hideDeleteModal() {
  if (deleteModalInstance) deleteModalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  bookToDelete.id = null
  bookToDelete.title = ''
}

// --- Экспорт данных ---
function exportBooksExcel() {
  exportData('excel')
}

function exportBooksWord() {
  exportData('word')
}

function exportData(type = 'excel') {
  axios({
    url: `/books/export/?type=${type}`,
    method: 'GET',
    responseType: 'blob'
  }).then((response) => {
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', type === 'excel' ? 'books.xlsx' : 'books.docx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }).catch((err) => {
    console.error('Ошибка при скачивании:', err)
    alert('Ошибка при скачивании файла')
  })
}

// --- Инициализация ---
onMounted(async () => {
  await fetchBooks()
  await fetchBookStats()
  await fetchGenres()
  await fetchLibraries()
})
</script>

<style scoped>
.stats-line {
  display: flex;
  align-items: center;
  justify-content: space-between; /* Левая статистика, правые кнопки */
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
