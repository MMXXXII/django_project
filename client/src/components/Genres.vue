<template>
  <h2>Жанры 
    <span style="font-size: 0.9em; color: #6c757d;">
      count ({{ genreStats ? genreStats.count : 0 }}), 
      avg ({{ genreStats ? genreStats.avg : 0 }}), 
      max ({{ genreStats ? genreStats.max : 0 }}), 
      min ({{ genreStats ? genreStats.min : 0 }})
    </span>
  </h2>

  <!-- Фильтрация -->
  <div class="mb-3">
    <!-- Поле для поиска по имени жанра -->
    <input 
      v-model="searchQuery" 
      type="text" 
      class="form-control" 
      placeholder="Поиск по жанрам" 
      @input="filterGenres"
    />
  </div>

  <!-- Фильтр по алфавиту -->
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
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Список -->
  <ul class="list-group">
    <li v-for="g in filteredGenres" :key="g.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>{{ g.name }}</div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(g)" data-bs-toggle="modal" data-bs-target="#editGenreModal">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(g)"><i class="bi bi-x"></i></button>
      </div>
    </li>
  </ul>

  <!-- Модал для редактирования -->
  <div class="modal fade" id="editGenreModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать жанр</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input v-model="genreToEdit.name" class="form-control" />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button class="btn btn-primary" @click="onUpdateGenre" data-bs-dismiss="modal">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const genres = ref([]) // Храним все жанры
const filteredGenres = ref([]) // Храним фильтрованные жанры
const genreStats = ref(null)
const genreToAdd = ref({ name: '' })
const genreToEdit = ref({ id: null, name: '' })
const searchQuery = ref("") // Состояние для поиска по имени жанра
const sortOrder = ref("asc") // Состояние для сортировки (по умолчанию от A до Я)

async function fetchGenres() {
  try {
    const res = await axios.get('/genres/')
    genres.value = res.data
    filteredGenres.value = genres.value
  } catch (error) {
    console.error('Ошибка при получении жанров:', error)
  }
}

function filterGenres() {
  // Фильтруем жанры по имени
  filteredGenres.value = genres.value.filter(genre => 
    genre.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
  sortGenres() // После фильтрации, сортируем жанры
}

function sortGenres() {
  // Сортируем жанры по имени (по алфавиту)
  filteredGenres.value.sort((a, b) => {
    const nameA = a.name.toLowerCase()
    const nameB = b.name.toLowerCase()

    if (sortOrder.value === "asc") {
      return nameA.localeCompare(nameB)
    } else {
      return nameB.localeCompare(nameA)
    }
  })
}

async function fetchGenresStats() {
  try {
    const response = await axios.get('/genres/stats') // Эндпоинт для статистики
    genreStats.value = response.data // Сохраняем статистику жанров в переменной genreStats
  } catch (error) {
    console.error('Ошибка при получении статистики по жанрам:', error)
  }
}

async function onAddGenre() {
  await axios.post('/genres/', { ...genreToAdd.value })
  genreToAdd.value = { name: '' }
  await fetchGenres() // Обновляем жанры после добавления
}

async function onRemove(g) {
  if (!confirm(`Удалить жанр "${g.name}"?`)) return
  await axios.delete(`/genres/${g.id}/`)
  await fetchGenres() // Обновляем список после удаления
}

function onEditClick(g) {
  genreToEdit.value = { ...g }
}

async function onUpdateGenre() {
  await axios.put(`/genres/${genreToEdit.value.id}/`, { ...genreToEdit.value })
  await fetchGenres() // Обновляем список жанров после редактирования
  await fetchGenresStats() // Обновляем статистику по жанрам
}

onMounted(async () => {
  try {
    await Promise.all([fetchGenres(), fetchGenresStats()])
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error)
  }
})
</script>
