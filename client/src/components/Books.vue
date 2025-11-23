<template>
  <div>
    <h2>Книги</h2>

    <!-- Статистика + кнопки -->
    <div class="stats-line">
      <div class="stats-left">
        <div class="stat">Количество: {{ bookStats?.count || 0 }}</div>
        <div class="stat">Среднее: {{ bookStats?.avg || 0 }}</div>
        <div class="stat">Максимум: {{ bookStats?.max || 0 }}</div>
        <div class="stat">Минимум: {{ bookStats?.min || 0 }}</div>
      </div>
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

    <!-- Кнопка массового удаления -->
    <div v-if="selectedBooks.length" class="mb-3">
      <button class="btn btn-danger" @click="showDeleteSelectedModal">
        Удалить выбранные ({{ selectedBooks.length }})
      </button>
    </div>

    <!-- Список книг -->
    <ul class="list-group">
      <li 
        v-for="b in filteredBooks" 
        :key="b.id" 
        class="list-group-item d-flex justify-content-between align-items-center"
        :class="{ 'selected': selectedBooks.includes(b.id) }"
        @click="toggleSelection(b.id)"
      >
        <div>
          <strong>{{ b.title }}</strong>
          <div class="text-muted small">{{ b.genre_name }} / {{ b.library_name }}</div>
        </div>
        <div>
          <button class="btn btn-sm btn-success me-2" @click.stop="onEditClick(b)">
            <i class="bi bi-pen-fill"></i>
          </button>
          <button class="btn btn-sm btn-danger" @click.stop="onRemoveClick(b)">
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

    <!-- Модалка массового удаления -->
    <div class="modal fade" id="deleteSelectedModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Удаление выбранных книг</h5>
            <button type="button" class="btn-close" @click="hideDeleteSelectedModal"></button>
          </div>
          <div class="modal-body">
            Вы действительно хотите удалить <strong>{{ selectedBooks.length }}</strong> выбранных книг?
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
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import * as bootstrap from 'bootstrap'

const books = ref([])
const filteredBooks = ref([])
const bookStats = ref(null)
const genres = ref([])
const libraries = ref([])

const bookToAdd = reactive({ title: '', genre: null, library: null })
const bookToEdit = reactive({ id: null, title: '', genre: null, library: null, modalInstance: null })
const bookToDelete = reactive({ id: null, title: '' })

const selectedBooks = ref([])
let deleteModalInstance = null
let deleteSelectedModalInstance = null

const searchQuery = ref('')
const sortOrder = ref('asc')

// --- API ---
async function fetchBooks() {
  const r = await axios.get('/books/')
  books.value = r.data.map(b => ({ 
    ...b, 
    genre_name: b.genre_name || b.genre,
    library_name: b.library_name || b.library 
  }))
  filterBooks()
}
async function fetchBookStats() { bookStats.value = (await axios.get('/books/stats/')).data }
async function fetchGenres() { genres.value = (await axios.get('/genres/')).data }
async function fetchLibraries() { libraries.value = (await axios.get('/libraries/')).data }

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

// --- CRUD ---
async function onAddBook() {
  if (!bookToAdd.genre || !bookToAdd.library) return alert('Выберите жанр и библиотеку')
  await axios.post('/books/', { ...bookToAdd })
  bookToAdd.title = ''
  bookToAdd.genre = null
  bookToAdd.library = null
  await fetchBooks()
  await fetchBookStats()
}

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
  await axios.put(`/books/${bookToEdit.id}/`, { title: bookToEdit.title, genre: bookToEdit.genre, library: bookToEdit.library })
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

// --- Удаление одного ---
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

// --- Выделение и массовое удаление ---
function toggleSelection(id) {
  if (selectedBooks.value.includes(id)) {
    selectedBooks.value = selectedBooks.value.filter(x => x !== id)
  } else {
    selectedBooks.value.push(id)
  }
}
function showDeleteSelectedModal() {
  const modalEl = document.getElementById('deleteSelectedModal')
  deleteSelectedModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  deleteSelectedModalInstance.show()
}
function hideDeleteSelectedModal() {
  if (deleteSelectedModalInstance) deleteSelectedModalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}
async function confirmDeleteSelected() {
  if (!selectedBooks.value.length) return
  await Promise.all(selectedBooks.value.map(id => axios.delete(`/books/${id}/`)))
  selectedBooks.value = []
  await fetchBooks()
  await fetchBookStats()
  hideDeleteSelectedModal()
}

// --- Экспорт ---
function exportBooksExcel() { exportData('excel') }
function exportBooksWord() { exportData('word') }
function exportData(type = 'excel') {
  axios({ url: `/books/export/?type=${type}`, method: 'GET', responseType: 'blob' })
    .then((res) => {
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', type === 'excel' ? 'books.xlsx' : 'books.docx')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    })
    .catch(err => { console.error(err); alert('Ошибка при скачивании файла') })
}

// --- Инициализация ---
onMounted(async () => {
  await fetchGenres()
  await fetchLibraries()
  await fetchBooks()
  await fetchBookStats()
})
</script>

<style scoped>
.stats-line { display:flex; justify-content:space-between; gap:12px; margin-bottom:14px; font-size:0.9em; }
.stats-left { display:flex; gap:12px; }
.stats-right { display:flex; gap:6px; }
.stat { background:#fafafa; border:1px solid #ddd; padding:4px 10px; border-radius:6px; color:#333; }
.list-group-item.selected { background-color: #d1e7dd; border-color: #0f5132; color: #0f5132; }
</style>
