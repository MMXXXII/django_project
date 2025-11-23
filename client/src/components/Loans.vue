<template>
  <h2>Выдачи</h2>

  <!-- Статистика + кнопки -->
  <div class="stats-line mb-3">
    <div class="stats-left">
      <div class="stat">Количество: {{ loanStats?.count || 0 }}</div>
      <div class="stat">Среднее: {{ loanStats?.avg || 0 }}</div>
      <div class="stat">Максимум: {{ loanStats?.max || 0 }}</div>
      <div class="stat">Минимум: {{ loanStats?.min || 0 }}</div>
    </div>
    <div class="stats-right">
      <button class="btn btn-success btn-sm me-2" @click="exportLoansExcel">Excel</button>
      <button class="btn btn-primary btn-sm" @click="exportLoansWord">Word</button>
    </div>
  </div>

  <!-- Поиск -->
  <div class="mb-3">
    <input 
      v-model="searchQuery" 
      type="text" 
      class="form-control" 
      placeholder="Поиск по книгам или читателям" 
      @input="filterLoans"
    />
  </div>

  <!-- Сортировка -->
  <div class="mb-3">
    <select v-model="sortOrder" @change="sortLoans" class="form-select">
      <option value="asc">От A до Я</option>
      <option value="desc">От Я до A</option>
    </select>
  </div>

  <!-- Форма добавления -->
  <form class="mb-3" @submit.prevent="onAddLoan">
    <div class="row g-2 align-items-center">
      <div class="col">
        <select v-model="loanToAdd.book" class="form-select" required>
          <option v-for="b in books" :key="b.id" :value="b.id">{{ b.title }}</option>
        </select>
      </div>
      <div class="col">
        <select v-model="loanToAdd.member" class="form-select" required>
          <option v-for="m in members" :key="m.id" :value="m.id">{{ m.first_name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <input type="date" v-model="loanToAdd.loan_date" class="form-control" required />
      </div>
      <div class="col-auto">
        <button type="button" class="btn btn-outline-success" @click="onAddLoan">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Кнопка массового удаления -->
  <div v-if="selectedLoans.length" class="mb-3">
    <button class="btn btn-danger" @click="showDeleteSelectedModal">
      Удалить выбранные ({{ selectedLoans.length }})
    </button>
  </div>

  <!-- Список выдач -->
  <ul class="list-group">
    <li 
      v-for="l in filteredLoans" 
      :key="l.id" 
      class="list-group-item d-flex justify-content-between align-items-center"
      :class="{ 'selected': selectedLoans.includes(l.id) }"
      @click="toggleSelection(l.id)"
    >
      <div>
        <div><strong>{{ booksById[l.book]?.title }}</strong> → {{ membersById[l.member]?.first_name }}</div>
        <div class="small text-muted">{{ l.loan_date }}</div>
      </div>
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

  <!-- Модалки редактирования и удаления одного -->
  <div class="modal fade" id="editLoanModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактирование выдачи</h5>
          <button type="button" class="btn-close" @click="hideEditModal"></button>
        </div>
        <div class="modal-body">
          <select v-model="loanToEdit.book" class="form-select mb-2">
            <option v-for="b in books" :key="b.id" :value="b.id">{{ b.title }}</option>
          </select>
          <select v-model="loanToEdit.member" class="form-select mb-2">
            <option v-for="m in members" :key="m.id" :value="m.id">{{ m.first_name }}</option>
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
      <div class="modal-content">
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

  <!-- Модалка массового удаления -->
  <div class="modal fade" id="deleteSelectedModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
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
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import * as bootstrap from 'bootstrap'

const loans = ref([])
const filteredLoans = ref([])
const books = ref([])
const members = ref([])
const loanStats = ref(null)

const loanToAdd = reactive({ book: null, member: null, loan_date: '' })
const loanToEdit = reactive({ id: null, book: null, member: null, loan_date: '', modalInstance: null })
const loanToDelete = reactive({ id: null, book: null, member: null, loan_date: '' })
const selectedLoans = ref([])

let deleteModalInstance = null
let deleteSelectedModalInstance = null

const searchQuery = ref('')
const sortOrder = ref('asc')

const booksById = computed(() => Object.fromEntries(books.value.map(b => [b.id, b])))
const membersById = computed(() => Object.fromEntries(members.value.map(m => [m.id, m])))

const loanToDeleteDisplay = computed(() => {
  return `${booksById.value[loanToDelete.book]?.title || ''} → ${membersById.value[loanToDelete.member]?.first_name || ''}`
})

// --- Получение данных ---
async function fetchLoans() {
  const r = await axios.get('/loans/')
  loans.value = r.data
  filterLoans()
}
async function fetchBooks() { books.value = (await axios.get('/books/')).data }
async function fetchMembers() { members.value = (await axios.get('/members/')).data }
async function fetchLoanStats() { loanStats.value = (await axios.get('/loans/stats/')).data }

watch([loans, books, members], filterLoans, { deep: true })

function filterLoans() {
  const query = searchQuery.value.toLowerCase()
  filteredLoans.value = loans.value.filter(l => {
    const bookTitle = booksById.value[l.book]?.title?.toLowerCase() || ''
    const memberName = membersById.value[l.member]?.first_name?.toLowerCase() || ''
    return bookTitle.includes(query) || memberName.includes(query)
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

// --- Добавление ---
async function onAddLoan() {
  if (!loanToAdd.book || !loanToAdd.member || !loanToAdd.loan_date) return
  await axios.post('/loans/', { ...loanToAdd })
  loanToAdd.book = null
  loanToAdd.member = null
  loanToAdd.loan_date = ''
  await fetchLoans()
  await fetchLoanStats()
}

// --- Редактирование ---
function onEditClick(l) {
  loanToEdit.id = l.id
  loanToEdit.book = l.book
  loanToEdit.member = l.member
  loanToEdit.loan_date = l.loan_date
  const modalEl = document.getElementById('editLoanModal')
  loanToEdit.modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  loanToEdit.modalInstance.show()
}

async function onUpdateLoan() {
  if (!loanToEdit.id) return
  await axios.put(`/loans/${loanToEdit.id}/`, {
    book: loanToEdit.book,
    member: loanToEdit.member,
    loan_date: loanToEdit.loan_date
  })
  await fetchLoans()
  await fetchLoanStats()
  hideEditModal()
}

function hideEditModal() {
  if (loanToEdit.modalInstance) loanToEdit.modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  loanToEdit.id = null
  loanToEdit.book = null
  loanToEdit.member = null
  loanToEdit.loan_date = ''
}

// --- Удаление одного ---
function onRemoveClick(l) {
  loanToDelete.id = l.id
  loanToDelete.book = l.book
  loanToDelete.member = l.member
  loanToDelete.loan_date = l.loan_date
  const modalEl = document.getElementById('deleteLoanModal')
  deleteModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  deleteModalInstance.show()
}

async function confirmDelete() {
  if (!loanToDelete.id) return
  await axios.delete(`/loans/${loanToDelete.id}/`)
  await fetchLoans()
  await fetchLoanStats()
  hideDeleteModal()
}

function hideDeleteModal() {
  if (deleteModalInstance) deleteModalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  loanToDelete.id = null
  loanToDelete.book = null
  loanToDelete.member = null
  loanToDelete.loan_date = ''
}

// --- Выделение ---
function toggleSelection(id) {
  if (selectedLoans.value.includes(id)) {
    selectedLoans.value = selectedLoans.value.filter(x => x !== id)
  } else {
    selectedLoans.value.push(id)
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
  if (!selectedLoans.value.length) return
  await Promise.all(selectedLoans.value.map(id => axios.delete(`/loans/${id}/`)))
  selectedLoans.value = []
  await fetchLoans()
  await fetchLoanStats()
  hideDeleteSelectedModal()
}

// --- Экспорт данных ---
function exportLoansExcel() { exportLoans('excel') }
function exportLoansWord() { exportLoans('word') }
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
  }).catch(err => { console.error(err); alert('Ошибка при скачивании файла') })
}

// --- Инициализация ---
onMounted(async () => {
  await Promise.all([fetchLoans(), fetchBooks(), fetchMembers(), fetchLoanStats()])
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

/* Подсветка выделенных выдач */
.list-group-item.selected {
  background-color: #d1e7dd;
  border-color: #0f5132;
  color: #0f5132;
}
</style>
