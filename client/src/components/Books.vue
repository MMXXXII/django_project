<template>
  <div>
    <h2>Книги</h2>

    <transition name="notif-fade">
      <div v-if="notification.visible" class="notification" :class="'notification-' + notification.type" role="status"
        aria-live="polite">
        {{ notification.message }}
      </div>
    </transition>

    <!-- Статистика книг -->
    <div class="stats-line">
      <div class="stats-left">
        <div class="stat">Всего книг: {{ bookStats?.count || 0 }}</div>
        <div class="stat" v-if="bookStats?.most_borrowed">
          Самая популярная: "{{ bookStats.most_borrowed.title }}" ({{ bookStats.most_borrowed.borrow_count }} выдач)
        </div>
      </div>
      <div class="stats-right" v-if="isAdmin">
        <button class="btn btn-success btn-sm me-2" @click="exportBooksExcel">Excel</button>
        <button class="btn btn-primary btn-sm" @click="exportBooksWord">Word</button>
      </div>
    </div>

    <!-- Поиск -->
    <div class="mb-3">
      <input v-model="searchQuery" type="text" class="form-control" placeholder="Поиск по книгам"
        @input="filterBooks" />
    </div>

    <!-- Сортировка -->
    <div class="mb-3">
      <select v-model="sortOrder" @change="sortBooks" class="form-select">
        <option value="asc">От A до Я</option>
        <option value="desc">От Я до A</option>
      </select>
    </div>

    <!-- Форма добавления (только админ) -->
    <form class="mb-3" @submit.prevent="onAddBook" v-if="isAdmin">
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

    <!-- Кнопка массового удаления (только админ) -->
    <div v-if="isAdmin && selectedBooks.length" class="mb-3">
      <button class="btn btn-danger" @click="showDeleteSelectedModal">
        Удалить выбранные ({{ selectedBooks.length }})
      </button>
    </div>

    <!-- Список книг -->
    <ul class="list-group">
      <li v-for="b in filteredBooks" :key="b.id"
        class="list-group-item d-flex justify-content-between align-items-center"
        :class="{ selected: isAdmin && selectedBooks.includes(b.id) }" @click="isAdmin && toggleSelection(b.id)">
        <div>
          <strong>{{ b.title }}</strong>
          <div class="text-muted small">{{ b.genre_name }} / {{ b.library_name }}</div>
        </div>
        <div v-if="isAdmin">
          <button class="btn btn-sm btn-success me-2" @click.stop="onEditClick(b)">
            <i class="bi bi-pen-fill"></i>
          </button>
          <button class="btn btn-sm btn-danger" @click.stop="onRemoveClick(b)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </li>
    </ul>

    <!-- Edit modal -->
    <div class="modal fade" id="editBookModal" tabindex="-1" ref="editModalEl">
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

    <!-- Delete single modal -->
    <div class="modal fade" id="deleteBookModal" tabindex="-1" ref="deleteModalEl">
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

    <!-- Delete selected modal -->
    <div class="modal fade" id="deleteSelectedModal" tabindex="-1" ref="deleteSelectedModalEl">
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
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import * as bootstrap from 'bootstrap'

// --- state ---
const books = ref([])
const filteredBooks = ref([])
const bookStats = ref(null)
const genres = ref([])
const libraries = ref([])
const user = ref(null)
const isAdmin = computed(() => !!user.value?.is_superuser)

const bookToAdd = reactive({ title: '', genre: '', library: '' })
const bookToEdit = reactive({ id: null, title: '', genre: '', library: '' })
const bookToDelete = reactive({ id: null, title: '' })
const selectedBooks = ref([])

const searchQuery = ref('')
const sortOrder = ref('asc')

// notification
const notification = reactive({
  visible: false,
  message: '',
  type: 'success',
  _timeoutId: null
})

function showNotification(msg, type = "success", duration = 2000) {
  if (notification._timeoutId) {
    clearTimeout(notification._timeoutId)
    notification._timeoutId = null
  }
  notification.message = msg
  notification.type = type
  notification.visible = true

  notification._timeoutId = setTimeout(() => {
    notification.visible = false
    notification._timeoutId = null
  }, duration)
}

// --- modal refs ---
const editModalEl = ref(null)
const deleteModalEl = ref(null)
const deleteSelectedModalEl = ref(null)

let editModalInstance = null
let deleteModalInstance = null
let deleteSelectedModalInstance = null

// --- helpers ---
function handleApiError(err, fallbackMessage = 'Ошибка') {
  console.error(err)
  const msg = err?.response?.data?.detail || err?.message || fallbackMessage
  showNotification(msg, 'danger')
}

// --- fetchers ---
async function fetchUser() {
  try {
    const r = await axios.get('/userprofile/info/')
    user.value = r.data
  } catch (err) {
    handleApiError(err, 'Не удалось получить информацию о пользователе')
  }
}

async function fetchBooks() {
  try {
    const r = await axios.get('/books/')
    books.value = r.data.map(b => ({
      ...b,
      genre_name: b.genre_name || (b.genre ? (b.genre.name || '') : ''),
      library_name: b.library_name || (b.library ? (b.library.name || '') : ''),
      status: b.status || ''
    }))
    filterBooks()
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить список книг')
  }
}

async function fetchBookStats() {
  try {
    const r = await axios.get('/books/stats/')
    bookStats.value = r.data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить статистику')
  }
}

async function fetchGenres() {
  try {
    const r = await axios.get('/genres/')
    genres.value = r.data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить жанры')
  }
}

async function fetchLibraries() {
  try {
    const r = await axios.get('/libraries/')
    libraries.value = r.data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить библиотеки')
  }
}

// --- фильтр/сортировка ---
function filterBooks() {
  const q = searchQuery.value.trim().toLowerCase()
  filteredBooks.value = books.value.filter(b => {
    const matchesQ = !q || (b.title && b.title.toLowerCase().includes(q))
    const notBorrowed = b.status !== 'borrowed'
    return matchesQ && notBorrowed
  })
  sortBooks()
}

function sortBooks() {
  filteredBooks.value.sort((a, b) => {
    const A = (a.title || '').toLowerCase()
    const B = (b.title || '').toLowerCase()
    return sortOrder.value === 'asc' ? A.localeCompare(B) : B.localeCompare(A)
  })
}

// --- CRUD ---
async function onAddBook() {
  if (!isAdmin.value) return
  if (!bookToAdd.title || !bookToAdd.genre || !bookToAdd.library) {
    showNotification('Заполните название, жанр и библиотеку', 'warning')
    return
  }

  try {
    await axios.post('/books/', { title: bookToAdd.title, genre: bookToAdd.genre, library: bookToAdd.library })
    bookToAdd.title = ''
    bookToAdd.genre = ''
    bookToAdd.library = ''
    await fetchBooks()
    await fetchBookStats()
    showNotification('Книга добавлена', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при добавлении книги')
  }
}

function onEditClick(b) {
  if (!isAdmin.value) return
  bookToEdit.id = b.id
  bookToEdit.title = b.title || ''
  bookToEdit.genre = b.genre && typeof b.genre === 'object' ? b.genre.id : b.genre || ''
  bookToEdit.library = b.library && typeof b.library === 'object' ? b.library.id : b.library || ''

  if (editModalEl.value) {
    editModalInstance = bootstrap.Modal.getOrCreateInstance(editModalEl.value)
    editModalInstance.show()
  }
}

async function onUpdateBook() {
  if (!isAdmin.value || !bookToEdit.id) return
  try {
    await axios.put(`/books/${bookToEdit.id}/`, {
      title: bookToEdit.title,
      genre: bookToEdit.genre,
      library: bookToEdit.library
    })
    await fetchBooks()
    await fetchBookStats()
    hideEditModal()
    showNotification('Изменения сохранены', 'warning')
  } catch (err) {
    handleApiError(err, 'Ошибка при обновлении книги')
  }
}

function hideEditModal() {
  if (editModalInstance) editModalInstance.hide()
  bookToEdit.id = null
  bookToEdit.title = ''
  bookToEdit.genre = ''
  bookToEdit.library = ''
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

function onRemoveClick(b) {
  if (!isAdmin.value) return
  bookToDelete.id = b.id
  bookToDelete.title = b.title || ''
  if (deleteModalEl.value) {
    deleteModalInstance = bootstrap.Modal.getOrCreateInstance(deleteModalEl.value)
    deleteModalInstance.show()
  }
}

async function confirmDelete() {
  if (!isAdmin.value || !bookToDelete.id) return
  try {
    await axios.delete(`/books/${bookToDelete.id}/`)
    await fetchBooks()
    await fetchBookStats()
    hideDeleteModal()
    showNotification('Книга удалена', 'danger')
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении книги')
  }
}

function hideDeleteModal() {
  if (deleteModalInstance) deleteModalInstance.hide()
  bookToDelete.id = null
  bookToDelete.title = ''
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

function toggleSelection(id) {
  if (!isAdmin.value) return
  const idx = selectedBooks.value.indexOf(id)
  if (idx >= 0) selectedBooks.value.splice(idx, 1)
  else selectedBooks.value.push(id)
}

function showDeleteSelectedModal() {
  if (!isAdmin.value) return
  if (deleteSelectedModalEl.value) {
    deleteSelectedModalInstance = bootstrap.Modal.getOrCreateInstance(deleteSelectedModalEl.value)
    deleteSelectedModalInstance.show()
  }
}

function hideDeleteSelectedModal() {
  if (deleteSelectedModalInstance) deleteSelectedModalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

async function confirmDeleteSelected() {
  if (!isAdmin.value || !selectedBooks.value.length) return
  try {
    await Promise.all(selectedBooks.value.map(id => axios.delete(`/books/${id}/`)))
    selectedBooks.value = []
    await fetchBooks()
    await fetchBookStats()
    hideDeleteSelectedModal()
    showNotification('Выбранные книги удалены', 'danger')
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении выбранных книг')
  }
}

// --- Экспорт ---
function exportBooksExcel() {
  if (!isAdmin.value) return
  exportData('excel')
}

function exportBooksWord() {
  if (!isAdmin.value) return
  exportData('word')
}

function exportData(type = 'excel') {
  axios({
    url: `/books/export/?type=${type}`,
    method: 'GET',
    responseType: 'blob'
  })
    .then(res => {
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', type === 'excel' ? 'books.xlsx' : 'books.docx')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      showNotification('Файл сформирован, скачивание началось', 'success')
    })
    .catch(err => {
      handleApiError(err, 'Ошибка при скачивании файла')
    })
}

// --- Инициализация ---
onMounted(async () => {
  await Promise.all([fetchUser(), fetchGenres(), fetchLibraries()])
  await Promise.all([fetchBooks(), fetchBookStats()])
})
</script>

<style scoped>
.stats-line {
  display: flex;
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

/* bootstrap colors */
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