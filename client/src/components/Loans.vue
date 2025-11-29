<template>
  <div>
    <h2>Выдачи</h2>

    <!-- Уведомления -->
    <transition name="notif-fade">
      <div v-if="notification.visible" class="notification" :class="'notification-' + notification.type" role="status"
        aria-live="polite">
        {{ notification.message }}
      </div>
    </transition>

    <!-- Статистика -->
    <div class="stats-line mb-3">
      <div class="stats-left">
        <div class="stat">Количество: {{ loanStats?.count || 0 }}</div>
        <div class="stat">Читатель с максимальным количеством книг: {{ loanStats?.topReader?.name || 'Не найден' }}
        </div>
        <div class="stat">Количество книг у этого читателя: {{ loanStats?.topReader?.loan_count || 0 }}</div>
      </div>
      <div class="stats-right" v-if="isAdmin">
        <button class="btn btn-success btn-sm me-2" @click="exportLoans('excel')">Excel</button>
        <button class="btn btn-primary btn-sm" @click="exportLoans('word')">Word</button>
      </div>
    </div>

    <!-- Фильтр по библиотеке -->
    <div class="mb-3">
      <select v-model="selectedLibrary" @change="filterLoans" class="form-select">
        <option value="">Все библиотеки</option>
        <option v-for="lib in libraries" :key="lib.id" :value="lib.id">{{ lib.name }}</option>
      </select>
    </div>

    <!-- Поиск -->
    <div class="mb-3">
      <input v-model="searchQuery" type="text" class="form-control" placeholder="Поиск по книгам или читателям"
        @input="filterLoans" />
    </div>

    <!-- Сортировка -->
    <div class="mb-3">
      <select v-model="sortOrder" @change="sortLoans" class="form-select">
        <option value="asc">От A до Я</option>
        <option value="desc">От Я до A</option>
      </select>
    </div>

    <!-- Форма добавления выдачи -->
    <form class="mb-3" @submit.prevent="onAddLoan">
      <div class="row g-2 align-items-center">
        <div class="col">
          <select v-model="loanToAdd.library" @change="onLibraryChange" class="form-select" required>
            <option value="" disabled>Выберите библиотеку</option>
            <option v-for="lib in libraries" :key="lib.id" :value="lib.id">{{ lib.name }}</option>
          </select>
        </div>
        <div class="col">
          <select v-model="loanToAdd.book" class="form-select" required>
            <option value="" disabled>Выберите книгу</option>
            <option v-for="b in availableBooks" :key="b.id" :value="b.id">
              {{ b.title }}
            </option>
          </select>
        </div>
        <div class="col-auto">
          <input type="date" v-model="loanToAdd.loan_date" class="form-control" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-outline-success">Добавить</button>
        </div>
      </div>
    </form>

    <!-- Список выдач -->
    <ul class="list-group mb-3">
      <li v-for="l in filteredLoans" :key="l.id"
        class="list-group-item d-flex justify-content-between align-items-center"
        :class="{ 'selected': isAdmin && selectedLoans.includes(l.id), 'returned': l.return_date }"
        @click="isAdmin && toggleSelection(l.id)">
        <div>
          <div>
            <strong>{{ booksById[l.book]?.title }}</strong> →
            {{ getMemberName(l.member) }}
            <span v-if="l.return_date" class="badge bg-success ms-2">Возвращена {{ l.return_date }}</span>
            <span v-else class="badge bg-warning ms-2">Выдана</span>
          </div>
          <div class="small text-muted">Дата выдачи: {{ l.loan_date }}</div>
          <div class="text-muted" style="font-size: 0.85em;">
            Библиотека: {{ getLibraryName(l.book) }}
          </div>
        </div>
        <div class="d-flex gap-2">
          <!-- Кнопка возврата для невозвращенных книг -->
          <button v-if="!l.return_date" class="btn btn-sm btn-info" @click.stop="onReturnBook(l)">
            <i class="bi bi-arrow-return-left"></i> Вернуть
          </button>

          <button v-if="isAdmin" class="btn btn-sm btn-success" @click.stop="onEditClick(l)">
            <i class="bi bi-pen-fill"></i>
          </button>
          <button v-if="isAdmin" class="btn btn-sm btn-danger" @click.stop="onRemoveClick(l)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </li>
    </ul>

    <!-- Массовое удаление для админа -->
    <div v-if="selectedLoans.length && isAdmin" class="mb-3">
      <button class="btn btn-danger" @click="showDeleteSelectedModal">
        Удалить выбранные ({{ selectedLoans.length }})
      </button>
    </div>

    <!-- Модалки -->
    <div class="modal fade" id="editLoanModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content" v-if="isAdmin">
          <div class="modal-header">
            <h5 class="modal-title">Редактирование выдачи</h5>
            <button type="button" class="btn-close" @click="hideEditModal"></button>
          </div>
          <div class="modal-body">
            <select v-model="loanToEdit.library" @change="onEditLibraryChange" class="form-select mb-2">
              <option value="" disabled>Выберите библиотеку</option>
              <option v-for="lib in libraries" :key="lib.id" :value="lib.id">{{ lib.name }}</option>
            </select>
            <select v-model="loanToEdit.book" class="form-select mb-2">
              <option value="" disabled>Выберите книгу</option>
              <option v-for="b in availableEditBooks" :key="b.id" :value="b.id">{{ b.title }}</option>
            </select>
            <select v-model="loanToEdit.member" class="form-select mb-2">
              <option v-for="m in allLibraryMembers" :key="m.id" :value="m.id">{{ m.first_name }}</option>
            </select>
            <input type="date" v-model="loanToEdit.loan_date" class="form-control" />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideEditModal">Отмена</button>
            <button type="button" class="btn btn-success" @click="onUpdateLoan">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="deleteLoanModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content" v-if="isAdmin">
          <div class="modal-header">
            <h5 class="modal-title">Удаление выдачи</h5>
            <button type="button" class="btn-close" @click="hideDeleteModal"></button>
          </div>
          <div class="modal-body">
            Вы действительно хотите удалить <strong>{{ loanToDeleteDisplay }}</strong>?
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
        <div class="modal-content" v-if="isAdmin">
          <div class="modal-header">
            <h5 class="modal-title">Удаление выбранных выдач</h5>
            <button type="button" class="btn-close" @click="hideDeleteSelectedModal"></button>
          </div>
          <div class="modal-body">
            Вы действительно хотите удалить <strong>{{ selectedLoans.length }}</strong> выбранных выдач?
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import * as bootstrap from 'bootstrap'

// --- State ---
const currentUser = reactive({ id: 0, first_name: '', role: 'user' })
const isAdmin = computed(() => currentUser.role === 'admin')
const currentMember = ref(null)

const libraries = ref([])
const selectedLibrary = ref('')
const books = ref([])
const allLibraryMembers = ref([])
const loans = ref([])
const filteredLoans = ref([])
const loanStats = ref(null)

const loanToAdd = reactive({ library: null, book: null, loan_date: '' })
const loanToEdit = reactive({ id: null, library: null, book: null, member: null, loan_date: '', modalInstance: null })
const loanToDelete = reactive({ id: null, book: null, member: null, loan_date: '' })
const selectedLoans = ref([])

let deleteModalInstance = null
let deleteSelectedModalInstance = null

const searchQuery = ref('')
const sortOrder = ref('asc')

// --- Notification ---
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

function handleApiError(err, fallbackMessage = 'Ошибка') {
  console.error(err)
  const msg = err?.response?.data?.detail || err?.message || fallbackMessage
  showNotification(msg, 'danger')
}

// --- Computed ---
const booksById = computed(() => Object.fromEntries(books.value.map(b => [b.id, b])))

const loanToDeleteDisplay = computed(() => {
  const book = booksById.value[loanToDelete.book]?.title || ''
  const member = getMemberName(loanToDelete.member)
  return `${book} → ${member}`
})

const availableBooks = computed(() =>
  books.value.filter(b => {
    if (loanToAdd.library && b.library !== Number(loanToAdd.library)) {
      return false
    }
    return b.is_available === true
  })
)

const availableEditBooks = computed(() =>
  books.value.filter(b => {
    if (loanToEdit.library && b.library !== Number(loanToEdit.library)) {
      return false
    }
    return b.is_available === true
  })
)

// --- Helpers ---
function getMemberName(memberId) {
  const member = allLibraryMembers.value.find(m => m.id === memberId)
  if (member) return member.first_name
  if (currentMember.value && currentMember.value.id === memberId) {
    return currentMember.value.first_name
  }
  return 'Неизвестно'
}

function getLibraryName(bookId) {
  const book = booksById.value[bookId]
  if (!book) return ''
  const library = libraries.value.find(lib => lib.id === book.library)
  return library ? library.name : ''
}

// --- Fetchers ---
async function fetchProfile() {
  try {
    const r = await axios.get('/userprofile/info/')
    if (r.data.id) {
      currentUser.id = r.data.id
      currentUser.first_name = r.data.username || r.data.first_name || ''
      currentUser.role = r.data.is_superuser ? 'admin' : 'user'
      console.log('[Loans] User profile loaded:', currentUser)
    }
  } catch (error) {
    handleApiError(error, 'Не удалось загрузить профиль пользователя')
  }
}

async function fetchCurrentMember() {
  try {
    const response = await axios.get('/library-members/')
    console.log('[Loans] Library members response:', response.data)

    if (response.data && response.data.length > 0) {
      if (isAdmin.value) {
        allLibraryMembers.value = response.data
        console.log('[Loans] Admin: loaded all library members')
      } else {
        currentMember.value = response.data[0]
        allLibraryMembers.value = response.data
        console.log('[Loans] User: loaded current member:', currentMember.value)
      }
    } else {
      console.warn('[Loans] No library members found')
      if (!isAdmin.value) {
        showNotification('Не найден профиль читателя. Обратитесь к администратору.', 'danger', 4000)
      }
    }
  } catch (error) {
    handleApiError(error, 'Не удалось загрузить читателей')
  }
}

async function fetchLibraries() {
  try {
    libraries.value = (await axios.get('/libraries/')).data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить библиотеки')
  }
}

async function fetchBooks() {
  try {
    books.value = (await axios.get('/books/')).data
    console.log('[Loans] Books loaded:', books.value)
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить книги')
  }
}

async function fetchLoans() {
  try {
    const r = await axios.get('/loans/')
    loans.value = r.data
    console.log('[Loans] Loans loaded:', loans.value)
    filterLoans()
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить выдачи')
  }
}

async function fetchLoanStats() {
  try {
    loanStats.value = (await axios.get('/loans/stats/')).data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить статистику')
  }
}

// --- Watchers ---
watch([loans, books, selectedLibrary], filterLoans, { deep: true })

// --- Filter/Sort ---
function filterLoans() {
  const query = searchQuery.value.toLowerCase()
  filteredLoans.value = loans.value.filter(l => {
    const bookTitle = booksById.value[l.book]?.title?.toLowerCase() || ''
    const memberName = getMemberName(l.member).toLowerCase()
    const libraryMatch = selectedLibrary.value ? booksById.value[l.book]?.library === Number(selectedLibrary.value) : true
    return (bookTitle.includes(query) || memberName.includes(query)) && libraryMatch
  })
  sortLoans()
}

function sortLoans() {
  filteredLoans.value.sort((a, b) => {
    const bookA = booksById.value[a.book]?.title?.toLowerCase() || ''
    const bookB = booksById.value[b.book]?.title?.toLowerCase() || ''
    return sortOrder.value === 'asc' ? bookA.localeCompare(bookB) : bookB.localeCompare(bookA)
  })
}

function onLibraryChange() { loanToAdd.book = null }
function onEditLibraryChange() { loanToEdit.book = null }

// --- CRUD ---
async function onAddLoan() {
  if (!loanToAdd.book || !loanToAdd.loan_date) {
    showNotification('Заполните все поля', 'warning')
    return
  }

  if (!currentMember.value || !currentMember.value.id) {
    showNotification('У вас нет профиля читателя библиотеки. Обратитесь к администратору.', 'danger', 4000)
    console.error('[Loans] currentMember is null or has no id:', currentMember.value)
    return
  }

  const data = {
    book: loanToAdd.book,
    member: currentMember.value.id,
    loan_date: loanToAdd.loan_date
  }

  try {
    console.log('[Loans] Creating loan:', data)
    await axios.post('/loans/', data)

    loanToAdd.library = null
    loanToAdd.book = null
    loanToAdd.loan_date = ''

    await fetchBooks()
    await fetchLoans()
    await fetchLoanStats()

    showNotification('Выдача успешно добавлена', 'success')
  } catch (error) {
    console.error('[Loans] Error adding loan:', error.response?.data || error)
    handleApiError(error, 'Ошибка при добавлении выдачи')
  }
}

async function onReturnBook(loan) {
  try {
    await axios.post(`/loans/${loan.id}/return/`)

    await fetchBooks()
    await fetchLoans()
    await fetchLoanStats()

    showNotification('Книга успешно возвращена', 'success')
  } catch (error) {
    console.error('[Loans] Error returning book:', error)
    handleApiError(error, 'Ошибка при возврате книги')
  }
}

function onEditClick(l) {
  if (!isAdmin.value) return
  loanToEdit.id = l.id
  loanToEdit.library = booksById.value[l.book]?.library || null
  loanToEdit.book = l.book
  loanToEdit.member = l.member
  loanToEdit.loan_date = l.loan_date
  const modalEl = document.getElementById('editLoanModal')
  loanToEdit.modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  loanToEdit.modalInstance.show()
}

async function onUpdateLoan() {
  if (!loanToEdit.id || !isAdmin.value) return
  
  try {
    await axios.put(`/loans/${loanToEdit.id}/`, {
      book: loanToEdit.book,
      member: loanToEdit.member,
      loan_date: loanToEdit.loan_date
    })
    await fetchBooks()
    await fetchLoans()
    await fetchLoanStats()
    hideEditModal()
    showNotification('Изменения сохранены', 'warning')
  } catch (err) {
    handleApiError(err, 'Ошибка при обновлении выдачи')
  }
}

function hideEditModal() {
  if (loanToEdit.modalInstance) loanToEdit.modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  loanToEdit.id = null
  loanToEdit.library = null
  loanToEdit.book = null
  loanToEdit.member = null
  loanToEdit.loan_date = ''
}

function onRemoveClick(l) {
  if (!isAdmin.value) return
  loanToDelete.id = l.id
  loanToDelete.book = l.book
  loanToDelete.member = l.member
  loanToDelete.loan_date = l.loan_date
  const modalEl = document.getElementById('deleteLoanModal')
  deleteModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  deleteModalInstance.show()
}

async function confirmDelete() {
  if (!loanToDelete.id || !isAdmin.value) return
  
  try {
    await axios.delete(`/loans/${loanToDelete.id}/`)
    await fetchBooks()
    await fetchLoans()
    await fetchLoanStats()
    hideDeleteModal()
    showNotification('Выдача удалена', 'danger')
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении выдачи')
  }
}

function hideDeleteModal() {
  if (deleteModalInstance) deleteModalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  loanToDelete.id = null
  loanToDelete.book = null
  loanToDelete.member = null
  loanToDelete.loan_date = ''
}

function toggleSelection(id) {
  if (!isAdmin.value) return
  if (selectedLoans.value.includes(id)) selectedLoans.value = selectedLoans.value.filter(x => x !== id)
  else selectedLoans.value.push(id)
}

function showDeleteSelectedModal() {
  if (!isAdmin.value) return
  const modalEl = document.getElementById('deleteSelectedModal')
  deleteSelectedModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  deleteSelectedModalInstance.show()
}

function hideDeleteSelectedModal() {
  if (deleteSelectedModalInstance) deleteSelectedModalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

async function confirmDeleteSelected() {
  if (!isAdmin.value || !selectedLoans.value.length) return
  
  try {
    await Promise.all(selectedLoans.value.map(id => axios.delete(`/loans/${id}/`)))
    selectedLoans.value = []
    await fetchBooks()
    await fetchLoans()
    await fetchLoanStats()
    hideDeleteSelectedModal()
    showNotification('Выбранные выдачи удалены', 'danger')
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении выбранных выдач')
  }
}

// --- Export ---
function exportLoans(type = 'excel') {
  axios({
    url: `/loans/export/?type=${type}`,
    method: 'GET',
    responseType: 'blob'
  }).then(res => {
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', type === 'excel' ? 'loans.xlsx' : 'loans.docx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    showNotification('Файл сформирован, скачивание началось', 'success')
  }).catch(err => {
    handleApiError(err, 'Ошибка при скачивании файла')
  })
}

// --- Init ---
onMounted(async () => {
  await fetchProfile()
  await Promise.all([
    fetchLibraries(),
    fetchBooks(),
    fetchLoans(),
    fetchLoanStats()
  ])
  await fetchCurrentMember()
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

.list-group-item.selected {
  background-color: #d1e7dd;
  border-color: #0f5132;
  color: #0f5132;
}

.list-group-item.returned {
  opacity: 0.7;
  background-color: #f8f9fa;
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