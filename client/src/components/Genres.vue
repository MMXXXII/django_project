<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { showNotification, handleApiError } from '../utils'

// данные
const genres = ref([])
const filteredGenres = ref([])
const genreStats = ref(null)
const user = ref(null)

// состояние формы и интерфейса
const searchQuery = ref('')
const sortOrder = ref('asc')

const isAdmin = computed(() => !!user.value?.is_superuser)

const notification = reactive({
  visible: false,
  message: '',
  type: 'success',
  _timeoutId: null,
})

const showEditDialog = ref(false)
const showDeleteDialog = ref(false)

const genreToAdd = reactive({
  name: '',
})

const genreToEdit = reactive({
  id: null,
  name: '',
})

const genreToDelete = reactive({
  id: null,
  name: '',
})

// загрузка пользователя
async function loadUser() {
  try {
    const r = await axios.get('/userprofile/info/')
    user.value = r.data
  } catch (err) {
    handleApiError(
      err,
      'Не удалось получить информацию о пользователе',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

// загрузка жанров
async function loadGenres() {
  try {
    const r = await axios.get('/genres/')
    genres.value = r.data
    applyFilter()
  } catch (err) {
    handleApiError(
      err,
      'Не удалось загрузить список жанров',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

// загрузка статистики
async function loadGenreStats() {
  try {
    const r = await axios.get('/genres/stats/')
    genreStats.value = r.data
  } catch (err) {
    handleApiError(
      err,
      'Не удалось загрузить статистику',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

// фильтрация и сортировка
function applyFilter() {
  const q = searchQuery.value.trim().toLowerCase()

  let list = genres.value

  if (q) {
    list = list.filter((g) => (g.name || '').toLowerCase().includes(q))
  }

  list = list.slice().sort((a, b) => {
    if (sortOrder.value === 'asc') {
      return a.name.localeCompare(b.name)
    } else {
      return b.name.localeCompare(a.name)
    }
  })

  filteredGenres.value = list
}

// добавление жанра
async function addGenre() {
  if (!isAdmin.value) return

  const name = genreToAdd.name.trim()
  if (!name) {
    showNotification(notification, 'Введите название жанра', 'warning')
    return
  }

  try {
    await axios.post('/genres/', { name })
    genreToAdd.name = ''
    await loadGenres()
    await loadGenreStats()
    showNotification(notification, 'Жанр добавлен', 'success')
  } catch (err) {
    handleApiError(
      err,
      'Ошибка при добавлении жанра',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

// редактирование жанра
function openEditDialog(genre) {
  if (!isAdmin.value) return
  genreToEdit.id = genre.id
  genreToEdit.name = genre.name || ''
  showEditDialog.value = true
}

async function updateGenre() {
  if (!isAdmin.value || !genreToEdit.id) return

  const name = genreToEdit.name.trim()
  if (!name) {
    showNotification(notification, 'Название жанра не может быть пустым', 'warning')
    return
  }

  try {
    await axios.put(`/genres/${genreToEdit.id}/`, { name })
    showEditDialog.value = false
    await loadGenres()
    await loadGenreStats()
    showNotification(notification, 'Изменения сохранены', 'warning')
  } catch (err) {
    handleApiError(
      err,
      'Ошибка при обновлении жанра',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

// удаление жанра
function openDeleteDialog(genre) {
  if (!isAdmin.value) return
  genreToDelete.id = genre.id
  genreToDelete.name = genre.name || ''
  showDeleteDialog.value = true
}

async function deleteGenre() {
  if (!isAdmin.value || !genreToDelete.id) return

  try {
    await axios.delete(`/genres/${genreToDelete.id}/`)
    showDeleteDialog.value = false
    await loadGenres()
    await loadGenreStats()
    showNotification(notification, 'Жанр удалён', 'danger')
  } catch (err) {
    handleApiError(
      err,
      'Ошибка при удалении жанра',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

// экспорт жанров
async function exportGenres(type = 'excel') {
  if (!isAdmin.value) return

  try {
    const response = await axios.get('/genres/export/', {
      params: { type },
      responseType: 'blob',
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', type === 'excel' ? 'genres.xlsx' : 'genres.docx')
    document.body.appendChild(link)
    link.click()
    link.remove()

    showNotification(notification, 'Файл сформирован, скачивание началось', 'success')
  } catch (err) {
    handleApiError(
      err,
      'Ошибка при скачивании файла',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

onMounted(async () => {
  await loadUser()
  await loadGenres()
  await loadGenreStats()
})
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card class="pa-4" elevation="2">
          <!-- заголовок и статистика -->
          <div class="d-flex justify-space-between align-center mb-4">
            <div>
              <h2 class="mb-1">Жанры</h2>
              <div class="text-body-2 text-medium-emphasis">
                Всего жанров: {{ genreStats?.count || 0 }},
                самый популярный: {{ genreStats?.top || 'нет данных' }}
              </div>
            </div>

            <div class="d-flex gap-2" v-if="isAdmin">
              <v-btn
                color="success"
                variant="outlined"
                prepend-icon="mdi-microsoft-excel"
                @click="exportGenres('excel')"
              >
                Excel
              </v-btn>
              <v-btn
                color="indigo"
                variant="outlined"
                prepend-icon="mdi-file-word"
                @click="exportGenres('word')"
              >
                Word
              </v-btn>
            </div>
          </div>

          <!-- уведомление -->
          <v-alert
            v-if="notification.visible"
            :type="notification.type"
            class="mb-4"
            variant="tonal"
            closable
          >
            {{ notification.message }}
          </v-alert>

          <!-- поиск и сортировка -->
          <v-row class="mb-4" align="center">
            <v-col cols="12" md="6">
              <v-text-field
                v-model="searchQuery"
                label="Поиск по жанрам"
                variant="outlined"
                density="comfortable"
                clearable
                prepend-inner-icon="mdi-magnify"
                @input="applyFilter"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="sortOrder"
                :items="[
                  { title: 'От A до Я', value: 'asc' },
                  { title: 'От Я до A', value: 'desc' },
                ]"
                item-title="title"
                item-value="value"
                label="Сортировка"
                variant="outlined"
                density="comfortable"
                @update:model-value="applyFilter"
              />
            </v-col>
          </v-row>

          <!-- добавление жанра (только админ) -->
          <v-row v-if="isAdmin" class="mb-4" align="end">
            <v-col cols="8">
              <v-text-field
                v-model="genreToAdd.name"
                label="Новый жанр"
                variant="outlined"
                density="comfortable"
                hide-details
                @keyup.enter="addGenre"
              />
            </v-col>
            <v-col cols="4">
              <v-btn
                color="primary"
                block
                size="large"
                prepend-icon="mdi-plus"
                height="48"
                @click="addGenre"
              >
                Добавить жанр
              </v-btn>
            </v-col>
          </v-row>

          <!-- список жанров -->
          <v-list lines="one">
            <v-list-item
              v-for="genre in filteredGenres"
              :key="genre.id"
              :title="genre.name"
            >
              <template #append>
                <div v-if="isAdmin" class="d-flex gap-2">
                  <v-btn
                    icon
                    size="small"
                    variant="text"
                    color="primary"
                    @click.stop="openEditDialog(genre)"
                  >
                    <v-icon icon="mdi-pencil" />
                  </v-btn>
                  <v-btn
                    icon
                    size="small"
                    variant="text"
                    color="error"
                    @click.stop="openDeleteDialog(genre)"
                  >
                    <v-icon icon="mdi-delete" />
                  </v-btn>
                </div>
              </template>
            </v-list-item>

            <v-list-item
              v-if="!filteredGenres.length"
              title="Жанров пока нет"
              subtitle="Добавьте первый жанр, чтобы начать."
            />
          </v-list>
        </v-card>
      </v-col>
    </v-row>

    <!-- диалог редактирования -->
    <v-dialog v-if="isAdmin" v-model="showEditDialog" max-width="420">
      <v-card>
        <v-card-title>Редактировать жанр</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="genreToEdit.name"
            label="Название жанра"
            variant="outlined"
            density="comfortable"
          />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="showEditDialog = false">
            Отмена
          </v-btn>
          <v-btn color="primary" @click="updateGenre">
            Сохранить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- диалог удаления -->
    <v-dialog v-if="isAdmin" v-model="showDeleteDialog" max-width="420">
      <v-card>
        <v-card-title class="text-h6">
          Удалить жанр
        </v-card-title>
        <v-card-text>
          Вы уверены, что хотите удалить жанр
          <strong>{{ genreToDelete.name }}</strong>?
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="showDeleteDialog = false">
            Отмена
          </v-btn>
          <v-btn color="error" @click="deleteGenre">
            Удалить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
