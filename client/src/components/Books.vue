<template>
  <div>
    <h2>Книги</h2>

    <!-- Статистика и кнопки -->
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
        <div class="col" v-if="genres.length">
          <select v-model="bookToAdd.genre" class="form-select" required>
            <option value="" disabled>Выберите жанр</option>
            <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <div class="col" v-if="libraries.length">
          <select v-model="bookToAdd.library" class="form-select" required>
            <option value="" disabled>Выберите библиотеку</option>
            <option v-for="l in libraries" :key="l.id" :value="l.id">{{ l.name }}</option>
          </select>
        </div>
        <div class="col">
          <input type="file" @change="onFileChange($event, bookToAdd)" class="form-control" />
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
        <div class="d-flex align-items-center gap-2">
          <img 
            v-if="b.cover_url" 
            :src="b.cover_url" 
            alt="Обложка" 
            class="img-thumbnail" 
            style="height:50px; cursor:pointer;" 
            @click="showCoverModal(b.cover_url)" 
          />
          <div>
            <strong>{{ b.title }}</strong>
            <div class="text-muted small">{{ b.genre_name }} / {{ b.library_name }}</div>
          </div>
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

    <!-- Модалки -->
    <div class="modal fade" id="editBookModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактирование книги</h5>
            <button type="button" class="btn-close" @click="hideEditModal"></button>
          </div>
          <div class="modal-body">
            <input v-model="bookToEdit.title" class="form-control mb-2" placeholder="Название книги" />
            <select v-model="bookToEdit.genre" class="form-select mb-2" v-if="genres.length">
              <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
            </select>
            <select v-model="bookToEdit.library" class="form-select mb-2" v-if="libraries.length">
              <option v-for="l in libraries" :key="l.id" :value="l.id">{{ l.name }}</option>
            </select>
            <input type="file" @change="onFileChange($event, bookToEdit)" class="form-control mb-2" />
            <div v-if="bookToEdit.cover_url" class="mt-2">
              <img :src="bookToEdit.cover_url" alt="Обложка" class="img-thumbnail" style="height:100px; cursor:pointer;" @click="showCoverModal(bookToEdit.cover_url)" />
            </div>
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

    <div class="modal fade" id="coverModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-body text-center">
            <img :src="coverModalUrl" alt="Обложка книги" class="img-fluid" />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
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

const bookToAdd = reactive({ title: '', genre: null, library: null, coverFile: null })
const bookToEdit = reactive({ id: null, title: '', genre: null, library: null, coverFile: null, cover_url: null, modalInstance: null })
const bookToDelete = reactive({ id: null, title: '' })
let deleteModalInstance = null

const searchQuery = ref('')
const sortOrder = ref('asc')

const coverModalUrl = ref(null)
let coverModalInstance = null

// --- API ---
async function fetchBooks() {
  const r = await axios.get('/books/')
  books.value = r.data.map(b => ({
    ...b,
    genre_name: b.genre_name || b.genre,
    library_name: b.library_name || b.library,
    cover_url: b.cover || null
  }))
  filterBooks()
}

async function fetchBookStats() { bookStats.value = (await axios.get('/books/stats/')).data }
async function fetchGenres() { genres.value = (await axios.get('/genres/')).data }
async function fetchLibraries() { libraries.value = (await axios.get('/libraries/')).data }

// --- Фильтр / сортировка ---
function filterBooks() {
  filteredBooks.value = books.value.filter(b => b.title.toLowerCase().includes(searchQuery.value.toLowerCase()))
  sortBooks()
}
function sortBooks() {
  filteredBooks.value.sort((a, b) => {
    const A = a.title.toLowerCase()
    const B = b.title.toLowerCase()
    return sortOrder.value === 'asc' ? A.localeCompare(B) : B.localeCompare(A)
  })
}

// --- Файл обложки ---
function onFileChange(e, bookObj) {
  const file = e.target.files[0]
  if (file) bookObj.coverFile = file
}

// --- Добавление ---
async function onAddBook() {
  if (!bookToAdd.genre || !bookToAdd.library) return alert('Выберите жанр и библиотеку')
  const formData = new FormData()
  formData.append('title', bookToAdd.title)
  formData.append('genre', bookToAdd.genre)
  formData.append('library', bookToAdd.library)
  if (bookToAdd.coverFile) formData.append('cover', bookToAdd.coverFile)
  await axios.post('/books/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  bookToAdd.title = ''
  bookToAdd.genre = null
  bookToAdd.library = null
  bookToAdd.coverFile = null
  await fetchBooks()
  await fetchBookStats()
}

// --- Редактирование ---
function onEditClick(b) {
  bookToEdit.id = b.id
  bookToEdit.title = b.title
  bookToEdit.genre = b.genre_id || b.genre
  bookToEdit.library = b.library_id || b.library
  bookToEdit.cover_url = b.cover_url
  const modalEl = document.getElementById('editBookModal')
  bookToEdit.modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  bookToEdit.modalInstance.show()
}

async function onUpdateBook() {
  if (!bookToEdit.id) return
  const formData = new FormData()
  formData.append('title', bookToEdit.title)
  formData.append('genre', bookToEdit.genre)
  formData.append('library', bookToEdit.library)
  if (bookToEdit.coverFile) formData.append('cover', bookToEdit.coverFile)
  await axios.put(`/books/${bookToEdit.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
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
  bookToEdit.coverFile = null
  bookToEdit.cover_url = null
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

// --- Просмотр обложки ---
function showCoverModal(url) {
  coverModalUrl.value = url
  if (!coverModalInstance) {
    const modalEl = document.getElementById('coverModal')
    coverModalInstance = new bootstrap.Modal(modalEl)
  }
  coverModalInstance.show()
}

// --- Экспорт ---
function exportBooksExcel() { exportData('excel') }
function exportBooksWord() { exportData('word') }
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
  }).catch(err => {
    console.error('Ошибка при скачивании:', err)
    alert('Ошибка при скачивании файла')
  })
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
.stats-line { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 14px; font-size:0.9em; }
.stats-left { display: flex; gap:12px; }
.stats-right { display:flex; gap:6px; }
.stat { background:#fafafa; border:1px solid #ddd; padding:4px 10px; border-radius:6px; color:#333; }
.img-thumbnail { border-radius:4px; }
</style>
