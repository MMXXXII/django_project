<template>
  <h2>Книги <span style="font-size: 0.9em; color: #6c757d;">count ({{ bookStats ? bookStats.count : 0 }}), avg ({{ bookStats ? bookStats.avg : 0 }}), max ({{ bookStats ? bookStats.max : 0 }}), min ({{ bookStats ? bookStats.min : 0 }})</span></h2>


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
        <input type="file" ref="bookCoverRef" @change="onCoverChange" class="form-control" />
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
      <div class="d-flex align-items-center">
        <img 
          v-if="b.cover" 
          :src="b.cover" 
          alt="Обложка" 
          class="book-cover me-3" 
          @click="openCoverModal(b.cover)" 
          style="max-width: 80px; cursor: pointer;"
        />
        <div>
          <button class="btn btn-sm btn-success me-2" @click="onEditClick(b)" data-bs-toggle="modal" data-bs-target="#editBookModal">
            <i class="bi bi-pen-fill"></i>
          </button>
          <button class="btn btn-sm btn-danger" @click="onRemove(b)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
    </li>
  </ul>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const books = ref([])
const genres = ref([])
const libraries = ref([])
const bookStats = ref(null)

const bookToAdd = ref({ title: '', genre: null, library: null })
const bookToEdit = ref({ id: null, title: '', genre: null, library: null })

const bookCoverRef = ref(null)
const bookEditCoverRef = ref(null)

const genresById = computed(() => Object.fromEntries(genres.value.map(g => [g.id, g])))
const librariesById = computed(() => Object.fromEntries(libraries.value.map(l => [l.id, l])))

async function fetchBooks() { books.value = (await axios.get('/books/')).data }
async function fetchGenres() { genres.value = (await axios.get('/genres/')).data }
async function fetchLibraries() { libraries.value = (await axios.get('/libraries/')).data }

async function fetchBookStats() {
  try {
    const response = await axios.get('/books/stats')
    bookStats.value = response.data
  } catch (error) {
    console.error('Ошибка при получении статистики по книгам:', error)
  }
}

function onCoverChange(event) {
  const file = event.target.files[0]
  if (file) bookToAdd.value.cover = file
}

async function onAddBook() {
  const formData = new FormData()
  formData.append('title', bookToAdd.value.title)
  formData.append('genre', bookToAdd.value.genre)
  formData.append('library', bookToAdd.value.library)
  if (bookToAdd.value.cover) formData.append('cover', bookToAdd.value.cover)

  await axios.post('/books/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  bookToAdd.value = { title: '', genre: null, library: null }
  bookCoverRef.value.value = null
  await fetchBooks()
}

function onEditClick(book) {
  bookToEdit.value = { ...book }
  bookEditCoverRef.value.value = null
}

async function onUpdateBook() {
  const formData = new FormData()
  formData.append('title', bookToEdit.value.title)
  formData.append('genre', bookToEdit.value.genre)
  formData.append('library', bookToEdit.value.library)
  if (bookToEdit.value.cover instanceof File) formData.append('cover', bookToEdit.value.cover)

  await axios.put(`/books/${bookToEdit.value.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  await fetchBooks()
}

async function onRemove(book) {
  if (!confirm(`Удалить книгу "${book.title}"?`)) return
  await axios.delete(`/books/${book.id}/`)
  await fetchBooks()
}

function openCoverModal(coverUrl) {
  coverModal.value = coverUrl
}

onMounted(async () => {
  await Promise.all([fetchBooks(), fetchGenres(), fetchLibraries(), fetchBookStats()])
})
</script>


<style scoped>
.cover-modal {
  position: fixed;
  top:0; left:0; right:0; bottom:0;
  background: rgba(0,0,0,0.7);
  display:flex;
  justify-content:center;
  align-items:center;
  z-index: 1050;
}
.cover-modal-img {
  max-width:90%;
  max-height:90%;
}
.book-cover {
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
