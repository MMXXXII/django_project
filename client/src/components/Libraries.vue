<template>
  <h2>Библиотеки 
    <span style="font-size: 0.9em; color: #6c757d;">
      count ({{ libraryStats ? libraryStats.count : 0 }}), 
      avg ({{ libraryStats ? libraryStats.avg : 0 }}), 
      max ({{ libraryStats ? libraryStats.max : 0 }}), 
      min ({{ libraryStats ? libraryStats.min : 0 }})
    </span>
  </h2>

  <!-- Фильтрация -->
  <div class="mb-3">
    <!-- Поле для поиска по названию библиотеки -->
    <input 
      v-model="searchQuery" 
      type="text" 
      class="form-control" 
      placeholder="Поиск по библиотекам" 
      @input="filterLibraries"
    />
  </div>

  <!-- Фильтр по алфавиту -->
  <div class="mb-3">
    <select v-model="sortOrder" @change="sortLibraries" class="form-select">
      <option value="asc">От A до Я</option>
      <option value="desc">От Я до A</option>
    </select>
  </div>

  <!-- Форма добавления -->
  <form class="mb-3" @submit.prevent="onAddLibrary">
    <div class="row g-2 align-items-center">
      <div class="col">
        <input v-model="libraryToAdd.name" class="form-control" placeholder="Название библиотеки" required />
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Список -->
  <ul class="list-group">
    <li v-for="l in filteredLibraries" :key="l.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>{{ l.name }}</div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(l)" data-bs-toggle="modal" data-bs-target="#editLibraryModal">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(l)"><i class="bi bi-x"></i></button>
      </div>
    </li>
  </ul>

  <!-- Модал для редактирования -->
  <div class="modal fade" id="editLibraryModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать библиотеку</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input v-model="libraryToEdit.name" class="form-control" />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button class="btn btn-primary" @click="onUpdateLibrary" data-bs-dismiss="modal">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const libraries = ref([]) // Храним все библиотеки
const filteredLibraries = ref([]) // Храним фильтрованные библиотеки
const libraryStats = ref(null)
const libraryToAdd = ref({ name: '' })
const libraryToEdit = ref({ id: null, name: '' })
const searchQuery = ref("") // Состояние для поиска по названию библиотеки
const sortOrder = ref("asc") // Состояние для сортировки (по умолчанию от A до Я)

async function fetchLibraries() {
  try {
    const res = await axios.get('/libraries/')
    libraries.value = res.data
    filteredLibraries.value = libraries.value
  } catch (error) {
    console.error('Ошибка при получении библиотек:', error)
  }
}

function filterLibraries() {
  // Фильтруем библиотеки по названию
  filteredLibraries.value = libraries.value.filter(library => 
    library.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
  sortLibraries() // После фильтрации, сортируем библиотеки
}

function sortLibraries() {
  // Сортируем библиотеки по названию (по алфавиту)
  filteredLibraries.value.sort((a, b) => {
    const nameA = a.name.toLowerCase()
    const nameB = b.name.toLowerCase()

    if (sortOrder.value === "asc") {
      return nameA.localeCompare(nameB)
    } else {
      return nameB.localeCompare(nameA)
    }
  })
}

async function fetchLibrariesStats() {
  try {
    const response = await axios.get('/libraries/stats') // Эндпоинт для статистики
    libraryStats.value = response.data // Сохраняем статистику библиотек в переменной libraryStats
  } catch (error) {
    console.error('Ошибка при получении статистики по библиотекам:', error)
  }
}

async function onAddLibrary() {
  await axios.post('/libraries/', { ...libraryToAdd.value })
  libraryToAdd.value = { name: '' }
  await fetchLibraries() // Обновляем библиотеки после добавления
}

async function onRemove(l) {
  if (!confirm(`Удалить библиотеку "${l.name}"?`)) return
  await axios.delete(`/libraries/${l.id}/`)
  await fetchLibraries() // Обновляем список после удаления
}

function onEditClick(l) {
  libraryToEdit.value = { ...l }
}

async function onUpdateLibrary() {
  await axios.put(`/libraries/${libraryToEdit.value.id}/`, { ...libraryToEdit.value })
  await fetchLibraries() // Обновляем список библиотек после редактирования
  await fetchLibrariesStats() // Обновляем статистику по библиотекам
}

onMounted(async () => {
  try {
    await Promise.all([fetchLibraries(), fetchLibrariesStats()])
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error)
  }
})
</script>
