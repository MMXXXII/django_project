<template>
  <h2>Жанры</h2>

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
    <li v-for="g in genres" :key="g.id" class="list-group-item d-flex justify-content-between align-items-center">
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
import { ref, onBeforeMount, computed } from 'vue'
import axios from 'axios'
import { onMounted } from 'vue'

const genres = ref([])
const genreToAdd = ref({ name: '' })
const genreToEdit = ref({ id: null, name: '' })
const isLoading = ref(true)  // Флаг для отображения загрузки

async function fetchGenres() {
  try {
    const res = await axios.get('/genres/')
    genres.value = res.data
  } catch (error) {
    console.error('Ошибка при получении жанров:', error)
  } finally {
    isLoading.value = false
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
  await fetchGenres() // Обновляем жанры после редактирования
}

onMounted(async () => {
  // Делаем все запросы сразу, чтобы избежать многократных запросов
  try {
    await Promise.all([fetchGenres()])
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error)
  }
});
</script>
