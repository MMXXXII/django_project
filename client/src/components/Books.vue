<template>
  <h2>Книги</h2>

  <!-- Форма добавления -->
  <form @submit.prevent="onAddBook" class="mb-3">
    <div class="row g-2 align-items-center">
      <div class="col">
        <input v-model="bookToAdd.title" class="form-control" placeholder="Название" required />
      </div>
      <div class="col-auto">
        <select v-model="bookToAdd.genre" class="form-select" required>
          <option v-for="g in genres" :value="g.id" :key="g.id">{{ g.name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <select v-model="bookToAdd.library" class="form-select" required>
          <option v-for="l in libraries" :value="l.id" :key="l.id">{{ l.name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Список книг -->
  <ul class="list-group">
    <li v-for="b in books" :key="b.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>
        <strong>{{ b.title }}</strong><br>
        <small class="text-muted">{{ genresById[b.genre]?.name }} — {{ librariesById[b.library]?.name }}</small>
      </div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(b)" data-bs-toggle="modal" data-bs-target="#editBookModal">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(b)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модал редактирования -->
  <div class="modal fade" id="editBookModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать книгу</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input v-model="bookToEdit.title" class="form-control mb-2" />
          <select v-model="bookToEdit.genre" class="form-select mb-2">
            <option v-for="g in genres" :value="g.id" :key="g.id">{{ g.name }}</option>
          </select>
          <select v-model="bookToEdit.library" class="form-select">
            <option v-for="l in libraries" :value="l.id" :key="l.id">{{ l.name }}</option>
          </select>
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
import { ref, onBeforeMount, computed } from 'vue'
import axios from 'axios'
import { onMounted } from 'vue'


// 

const books = ref([])
const genres = ref([])
const libraries = ref([])

const bookToAdd = ref({ title: '', genre: null, library: null })
const bookToEdit = ref({ id: null, title: '', genre: null, library: null })

const genresById = computed(() => Object.fromEntries(genres.value.map(g => [g.id, g])))
const librariesById = computed(() => Object.fromEntries(libraries.value.map(l => [l.id, l])))

async function fetchBooks() { books.value = (await axios.get('/books/')).data }
async function fetchGenres() { genres.value = (await axios.get('/genres/')).data }
async function fetchLibraries() { libraries.value = (await axios.get('/libraries/')).data }

async function onAddBook() {
  await axios.post('/books/', { ...bookToAdd.value })
  bookToAdd.value = { title: '', genre: null, library: null }
  await fetchBooks()
}

async function onRemove(book) {
  if (!confirm(`Удалить книгу "${book.title}"?`)) return
  await axios.delete(`/books/${book.id}/`)
  await fetchBooks()
}

function onEditClick(book) {
  bookToEdit.value = { ...book }
}

async function onUpdateBook() {
  await axios.put(`/books/${bookToEdit.value.id}/`, { ...bookToEdit.value })
  await fetchBooks()
}

const isLoading = ref(true); // Флаг загрузки данных

onMounted(async () => {
  // Делаем все запросы сразу, чтобы избежать многократных запросов
  try {
    await Promise.all([
      fetchBooks(),
      fetchGenres(),
      fetchLibraries()
    ]);
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error);
  }
});



</script>
