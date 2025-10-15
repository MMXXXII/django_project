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
          <select v-model="bookToEdit.library" class="form-select mb-2">
            <option v-for="l in libraries" :value="l.id" :key="l.id">{{ l.name }}</option>
          </select>
          <input type="file" ref="bookEditCoverRef" @change="onEditCoverChange" class="form-control mt-2" />
          <img v-if="bookToEdit.cover" :src="bookToEdit.cover" alt="Обложка" class="mt-2" style="max-width:100px" />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button class="btn btn-primary" @click="onUpdateBook" data-bs-dismiss="modal">Сохранить</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно для просмотра обложки -->
  <div v-if="coverModal" class="cover-modal" @click="coverModal = null">
    <img :src="coverModal" alt="Обложка" class="cover-modal-img" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const books = ref([])
const genres = ref([])
const libraries = ref([])

const bookToAdd = ref({ title: '', genre: null, library: null })
const bookToEdit = ref({ id: null, title: '', genre: null, library: null })

const bookCoverRef = ref(null)
const bookEditCoverRef = ref(null)

const coverModal = ref(null)

const genresById = computed(() => Object.fromEntries(genres.value.map(g => [g.id, g])))
const librariesById = computed(() => Object.fromEntries(libraries.value.map(l => [l.id, l])))

async function fetchBooks() { books.value = (await axios.get('/books/')).data }
async function fetchGenres() { genres.value = (await axios.get('/genres/')).data }
async function fetchLibraries() { libraries.value = (await axios.get('/libraries/')).data }

function onCoverChange(event) {
  const file = event.target.files[0]
  if (file) bookToAdd.value.cover = file
}

function onEditCoverChange(event) {
  const file = event.target.files[0]
  if (file) bookToEdit.value.cover = file
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
  await Promise.all([fetchBooks(), fetchGenres(), fetchLibraries()])
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
