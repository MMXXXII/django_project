<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { showNotification, handleApiError } from '../utils'

const books = ref([])
const filteredBooks = ref([])
const genres = ref([])
const libraries = ref([])
const bookStats = ref(null)
const user = ref(null)

const isAdmin = computed(() => !!user.value?.is_superuser)

const searchQuery = ref('')

const notification = reactive({
  visible: false,
  message: '',
  type: 'success',
  _timeoutId: null,
})

const showAddBookDialog = ref(false)
const showEditBookDialog = ref(false)
const showDeleteBookDialog = ref(false)

const bookToAdd = reactive({
  title: '',
  genre: '',
  library: '',
})

const bookToEdit = reactive({
  id: null,
  title: '',
  genre: '',
  library: '',
})

const bookToDelete = reactive({
  id: null,
  title: '',
})

const headers = [
  { title: 'Название', value: 'title' },
  { title: 'Жанр', value: 'genre_name' },
  { title: 'Библиотека', value: 'library_name' },
  { title: 'Статус', value: 'status' },
  { title: 'Действия', value: 'actions', align: 'end' },
]

// --- Загрузка данных ---

async function loadUser() {
  try {
    const r = await axios.get('/userprofile/info/')
    user.value = r.data
  } catch (err) {
    handleApiError(err, 'Не удалось получить информацию о пользователе', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

async function loadBooks() {
  try {
    const r = await axios.get('/books/')
    books.value = r.data.map((b) => ({
      ...b,
      genre_name: b.genre_name || (b.genre ? b.genre.name || '' : ''),
      library_name: b.library_name || (b.library ? b.library.name || '' : ''),
      status: b.is_available ? 'Доступна' : 'Выдана',
    }))
    applyFilter()
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить список книг', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

async function loadStats() {
  try {
    const r = await axios.get('/books/stats/')
    bookStats.value = r.data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить статистику', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

async function loadGenres() {
  try {
    const r = await axios.get('/genres/')
    genres.value = r.data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить жанры', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

async function loadLibraries() {
  try {
    const r = await axios.get('/libraries/')
    libraries.value = r.data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить библиотеки', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

function applyFilter() {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) {
    filteredBooks.value = books.value.slice()
    return
  }
  filteredBooks.value = books.value.filter((b) =>
    (b.title || '').toLowerCase().includes(q),
  )
}

// --- Книги: добавить / редактировать / удалить ---

async function addBook() {
  if (!isAdmin.value) return

  if (!bookToAdd.title || !bookToAdd.genre || !bookToAdd.library) {
    showNotification(notification, 'Заполните название, жанр и библиотеку', 'warning')
    return
  }

  try {
    await axios.post('/books/', {
      title: bookToAdd.title,
      genre: bookToAdd.genre,
      library: bookToAdd.library,
    })

    bookToAdd.title = ''
    bookToAdd.genre = ''
    bookToAdd.library = ''
    showAddBookDialog.value = false

    await loadBooks()
    await loadStats()
    showNotification(notification, 'Книга добавлена', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при добавлении книги', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

function openEditDialog(book) {
  if (!isAdmin.value) return

  bookToEdit.id = book.id
  bookToEdit.title = book.title || ''
  bookToEdit.genre =
    book.genre && typeof book.genre === 'object' ? book.genre.id : book.genre || ''
  bookToEdit.library =
    book.library && typeof book.library === 'object'
      ? book.library.id
      : book.library || ''

  showEditBookDialog.value = true
}

async function updateBook() {
  if (!isAdmin.value || !bookToEdit.id) return

  try {
    await axios.put(`/books/${bookToEdit.id}/`, {
      title: bookToEdit.title,
      genre: bookToEdit.genre,
      library: bookToEdit.library,
    })

    showEditBookDialog.value = false
    await loadBooks()
    await loadStats()
    showNotification(notification, 'Изменения сохранены', 'warning')
  } catch (err) {
    handleApiError(err, 'Ошибка при обновлении книги', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

function openDeleteDialog(book) {
  if (!isAdmin.value) return

  bookToDelete.id = book.id
  bookToDelete.title = book.title || ''
  showDeleteBookDialog.value = true
}

async function deleteBook() {
  if (!isAdmin.value || !bookToDelete.id) return

  try {
    await axios.delete(`/books/${bookToDelete.id}/`)

    showDeleteBookDialog.value = false
    await loadBooks()
    await loadStats()
    showNotification(notification, 'Книга удалена', 'danger')
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении книги', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

// --- Экспорт ---

async function exportExcel() {
  if (!isAdmin.value) return

  try {
    const response = await axios.get('/books/export/', {
      params: { type: 'excel' },
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'Books.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    handleApiError(err, 'Ошибка при экспорте в Excel', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

async function exportWord() {
  if (!isAdmin.value) return

  try {
    const response = await axios.get('/books/export/', {
      params: { type: 'word' },
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'Books.docx')
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    handleApiError(err, 'Ошибка при экспорте в Word', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

onMounted(async () => {
  await loadUser()
  await loadGenres()
  await loadLibraries()
  await loadBooks()
  await loadStats()
})
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card class="pa-4" elevation="2">
          <div class="d-flex justify-space-between align-center mb-4">
            <div>
              <h2 class="mb-1">Книги</h2>
              <div class="text-body-2 text-medium-emphasis">
                Всего: {{ bookStats?.total || 0 }},
                доступно: {{ bookStats?.available || 0 }},
                выдано: {{ bookStats?.loaned || 0 }}
              </div>
            </div>

            <div class="d-flex gap-2" v-if="isAdmin">
              <v-btn color="success" variant="outlined" @click="exportExcel" prepend-icon="mdi-microsoft-excel">
                Excel
              </v-btn>
              <v-btn color="indigo" variant="outlined" @click="exportWord" prepend-icon="mdi-file-word">
                Word
              </v-btn>
            </div>
          </div>

          <v-alert v-if="notification.visible" :type="notification.type" class="mb-4" variant="tonal" closable>
            {{ notification.message }}
          </v-alert>

          <v-row class="mb-4" align="center">
            <v-col cols="12" md="6">
              <v-text-field v-model="searchQuery" label="Поиск по книгам" variant="outlined" density="comfortable"
                clearable prepend-inner-icon="mdi-magnify" @input="applyFilter" />
            </v-col>
            <v-col cols="12" md="6" class="d-flex justify-end">
              <v-btn v-if="isAdmin" color="primary" prepend-icon="mdi-plus" @click="showAddBookDialog = true">
                Добавить книгу
              </v-btn>
            </v-col>
          </v-row>

          <v-data-table :headers="headers" :items="filteredBooks" item-key="id" :items-per-page="10"
            class="elevation-1">
            <template #item.status="{ item }">
              <v-chip :color="item.status === 'Доступна' ? 'success' : 'orange'" variant="flat">
                {{ item.status }}
              </v-chip>
            </template>

            <template #item.actions="{ item }">
              <div v-if="isAdmin" style="display: flex; justify-content: flex-end;">
                <v-btn variant="text" color="primary" prepend-icon="mdi-pencil" @click="openEditDialog(item)">
                </v-btn>
                <v-btn variant="text" color="error" prepend-icon="mdi-delete" @click="openDeleteDialog(item)">
                </v-btn>
              </div>
            </template> 




            <template #no-data>
              <div class="text-center pa-6">
                <div class="mb-2">Нет книг</div>
                <div class="text-body-2 mb-3">
                  Добавьте первую книгу, чтобы начать.
                </div>
                <v-btn v-if="isAdmin" color="primary" prepend-icon="mdi-plus" @click="showAddBookDialog = true">
                  Добавить книгу
                </v-btn>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Диалог добавления -->
    <v-dialog v-if="isAdmin" v-model="showAddBookDialog" max-width="520">
      <v-card>
        <v-card-title>Добавить книгу</v-card-title>
        <v-card-text>
          <v-text-field v-model="bookToAdd.title" label="Название книги" variant="outlined" density="comfortable"
            class="mb-3" />
          <v-select v-model="bookToAdd.genre" :items="genres" item-value="id" item-title="name" label="Жанр"
            variant="outlined" density="comfortable" class="mb-3" />
          <v-select v-model="bookToAdd.library" :items="libraries" item-value="id" item-title="name" label="Библиотека"
            variant="outlined" density="comfortable" />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="showAddBookDialog = false">
            Отмена
          </v-btn>
          <v-btn color="primary" @click="addBook">
            Добавить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Диалог редактирования -->
    <v-dialog v-if="isAdmin" v-model="showEditBookDialog" max-width="520">
      <v-card>
        <v-card-title>Редактировать книгу</v-card-title>
        <v-card-text>
          <v-text-field v-model="bookToEdit.title" label="Название книги" variant="outlined" density="comfortable"
            class="mb-3" />
          <v-select v-model="bookToEdit.genre" :items="genres" item-value="id" item-title="name" label="Жанр"
            variant="outlined" density="comfortable" class="mb-3" />
          <v-select v-model="bookToEdit.library" :items="libraries" item-value="id" item-title="name" label="Библиотека"
            variant="outlined" density="comfortable" />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="showEditBookDialog = false">
            Отмена
          </v-btn>
          <v-btn color="primary" @click="updateBook">
            Сохранить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Диалог удаления -->
    <v-dialog v-if="isAdmin" v-model="showDeleteBookDialog" max-width="420">
      <v-card>
        <v-card-title class="text-h6">
          Удалить книгу
        </v-card-title>
        <v-card-text>
          Вы уверены, что хотите удалить книгу
          <strong>{{ bookToDelete.title }}</strong>?
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="showDeleteBookDialog = false">
            Отмена
          </v-btn>
          <v-btn color="error" @click="deleteBook">
            Удалить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
