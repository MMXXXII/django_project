<template>
  <h2>Книги 
    <span style="font-size: 0.9em; color: #6c757d;">
      count ({{ bookStats ? bookStats.count : 0 }}), 
      avg ({{ bookStats ? bookStats.avg : 0 }}), 
      max ({{ bookStats ? bookStats.max : 0 }}), 
      min ({{ bookStats ? bookStats.min : 0 }})
    </span>
  </h2>

  <!-- Фильтрация -->
  <div class="mb-3">
    <!-- Поле для поиска по названию книги -->
    <input 
      v-model="searchQuery" 
      type="text" 
      class="form-control" 
      placeholder="Поиск по книгам" 
      @input="filterBooks"
    />
  </div>

  <!-- Фильтр по алфавиту -->
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
      <div class="col-auto">
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Список -->
  <ul class="list-group">
    <li v-for="b in filteredBooks" :key="b.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>{{ b.title }}</div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(b)" data-bs-toggle="modal" data-bs-target="#editBookModal">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(b)"><i class="bi bi-x"></i></button>
      </div>
    </li>
  </ul>

  <!-- Модал для редактирования -->
  <div class="modal fade" id="editBookModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать книгу</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input v-model="bookToEdit.title" class="form-control" />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button class="btn btn-primary" @click="onUpdateBook" data-bs-dismiss="modal">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const books = ref([]) // Храним все книги
const filteredBooks = ref([]) // Храним фильтрованные книги
const bookStats = ref(null)
const bookToAdd = ref({ title: '' })
const bookToEdit = ref({ id: null, title: '' })
const searchQuery = ref("") // Состояние для поиска по названию книги
const sortOrder = ref("asc") // Состояние для сортировки (по умолчанию от A до Я)

async function fetchBooks() {
  try {
    const res = await axios.get('/books/')
    books.value = res.data
    filteredBooks.value = books.value
  } catch (error) {
    console.error('Ошибка при получении книг:', error)
  }
}

function filterBooks() {
  // Фильтруем книги по названию
  filteredBooks.value = books.value.filter(book => 
    book.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
  sortBooks() // После фильтрации, сортируем книги
}

function sortBooks() {
  // Сортируем книги по названию (по алфавиту)
  filteredBooks.value.sort((a, b) => {
    const nameA = a.title.toLowerCase()
    const nameB = b.title.toLowerCase()

    if (sortOrder.value === "asc") {
      return nameA.localeCompare(nameB)
    } else {
      return nameB.localeCompare(nameA)
    }
  })
}

async function fetchBooksStats() {
  try {
    const response = await axios.get('/books/stats') // Эндпоинт для статистики
    bookStats.value = response.data // Сохраняем статистику книг в переменной bookStats
  } catch (error) {
    console.error('Ошибка при получении статистики по книгам:', error)
  }
}

async function onAddBook() {
  await axios.post('/books/', { ...bookToAdd.value })
  bookToAdd.value = { title: '' }
  await fetchBooks() // Обновляем книги после добавления
}

async function onRemove(b) {
  if (!confirm(`Удалить книгу "${b.title}"?`)) return
  await axios.delete(`/books/${b.id}/`)
  await fetchBooks() // Обновляем список после удаления
}

function onEditClick(b) {
  bookToEdit.value = { ...b }
}

async function onUpdateBook() {
  await axios.put(`/books/${bookToEdit.value.id}/`, { ...bookToEdit.value })
  await fetchBooks() // Обновляем список книг после редактирования
  await fetchBooksStats() // Обновляем статистику по книгам
}

onMounted(async () => {
  try {
    await Promise.all([fetchBooks(), fetchBooksStats()])
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error)
  }
})
</script>
