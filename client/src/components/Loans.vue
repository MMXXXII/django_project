<template>
  <h2>Выдачи 
    <span style="font-size: 0.9em; color: #6c757d;">
      count ({{ loanStats ? loanStats.count : 0 }}), 
      avg ({{ loanStats ? loanStats.avg : 0 }}), 
      max ({{ loanStats ? loanStats.max : 0 }}), 
      min ({{ loanStats ? loanStats.min : 0 }})
    </span>
  </h2>

  <!-- Фильтрация -->
  <div class="mb-3">
    <input 
      v-model="searchQuery" 
      type="text" 
      class="form-control" 
      placeholder="Поиск по книгам или читателям" 
      @input="filterLoans"
    />
  </div>

  <!-- Фильтр по алфавиту -->
  <div class="mb-3">
    <select v-model="sortOrder" @change="sortLoans" class="form-select">
      <option value="asc">От A до Я</option>
      <option value="desc">От Я до A</option>
    </select>
  </div>

  <!-- Форма добавления -->
  <form @submit.prevent="onAddLoan" class="mb-3">
    <div class="row g-2 align-items-center">
      <div class="col">
        <select v-model="loanToAdd.book" class="form-select" required>
          <option v-for="b in books" :value="b.id" :key="b.id">{{ b.title }}</option>
        </select>
      </div>
      <div class="col">
        <select v-model="loanToAdd.member" class="form-select" required>
          <option v-for="m in members" :value="m.id" :key="m.id">{{ m.first_name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <input type="date" v-model="loanToAdd.loan_date" class="form-control" required />
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить выдачу</button>
      </div>
    </div>
  </form>

  <!-- Список -->
  <ul class="list-group">
    <li v-for="l in filteredLoans" :key="l.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>
        <div><strong>{{ booksById[l.book]?.title }}</strong> → {{ membersById[l.member]?.first_name }}</div>
        <div class="small text-muted">{{ l.loan_date }}</div>
      </div>
      <div>
        <button class="btn btn-sm btn-danger" @click="onRemove(l)"><i class="bi bi-x"></i></button>
      </div>
    </li>
  </ul>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'

// Состояния и переменные
const loans = ref([]) // Храним все записи о выдачах
const filteredLoans = ref([]) // Храним фильтрованные выдачи
const books = ref([]) // Книги
const members = ref([]) // Читатели
const loanStats = ref(null) // Статистика по выдачам
const loanToAdd = ref({ book: null, member: null, loan_date: '' })
const searchQuery = ref("") // Состояние для поиска
const sortOrder = ref("asc") // Состояние для сортировки (по умолчанию от A до Я)

// Сопоставление книг и читателей по ID
const booksById = computed(() => Object.fromEntries(books.value.map(b => [b.id, b])))
const membersById = computed(() => Object.fromEntries(members.value.map(m => [m.id, m])))

// Функции для получения данных
async function fetchLoans() {
  try {
    const res = await axios.get('/loans/')
    loans.value = res.data
    filteredLoans.value = res.data // Изначально все выдачи
  } catch (error) {
    console.error('Ошибка при получении выдач:', error)
  }
}

async function fetchBooks() {
  try {
    const res = await axios.get('/books/')
    books.value = res.data
  } catch (error) {
    console.error('Ошибка при получении книг:', error)
  }
}

async function fetchMembers() {
  try {
    const res = await axios.get('/members/')
    members.value = res.data
  } catch (error) {
    console.error('Ошибка при получении читателей:', error)
  }
}

// Получение статистики по выдачам
async function fetchLoanStats() {
  try {
    const response = await axios.get('/loans/stats')
    loanStats.value = response.data
  } catch (error) {
    console.error('Ошибка при получении статистики по выдачам:', error)
  }
}

watch([loans, books, members], () => {
  filterLoans()
}, { deep: true })

function filterLoans() {
  if (!books.value?.length || !members.value?.length) {
    filteredLoans.value = []
    return
  }

  filteredLoans.value = loans.value.filter(loan => {
    const bookTitle = booksById.value[loan.book]?.title?.toLowerCase() || ""
    const memberName = membersById.value[loan.member]?.first_name?.toLowerCase() || ""
    const query = searchQuery.value.toLowerCase()
    
    return bookTitle.includes(query) || memberName.includes(query)
  })
  sortLoans()
}

function sortLoans() {
  if (!filteredLoans.value?.length) return

  filteredLoans.value.sort((a, b) => {
    const bookTitleA = booksById.value[a.book]?.title?.toLowerCase() || ""
    const bookTitleB = booksById.value[b.book]?.title?.toLowerCase() || ""

    if (sortOrder.value === "asc") {
      return bookTitleA.localeCompare(bookTitleB)
    } else {
      return bookTitleB.localeCompare(bookTitleA)
    }
  })
}

// Функция добавления выдачи
async function onAddLoan() {
  await axios.post('/loans/', { ...loanToAdd.value })
  loanToAdd.value = { book: null, member: null, loan_date: '' }
  await fetchLoans() // Обновляем список после добавления
}

// Функция удаления выдачи
async function onRemove(l) {
  if (!confirm('Удалить выдачу?')) return
  await axios.delete(`/loans/${l.id}/`)
  await fetchLoans() // Обновляем список после удаления
}

onMounted(async () => {
  try {
    await Promise.all([fetchLoans(), fetchBooks(), fetchMembers(), fetchLoanStats()])
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error)
  }
})
</script>
