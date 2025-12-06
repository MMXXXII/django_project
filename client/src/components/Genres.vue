<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { showNotification, handleApiError } from '../utils'

const user = ref(null)
const isAdmin = computed(() => !!user.value?.is_superuser)
const genres = ref([])
const genreStats = ref(null)
const searchQuery = ref('')
const sortOrder = ref('asc')

const dialogs = reactive({ edit: false, delete: false })
const form = reactive({ id: null, name: '' })

const filteredGenres = computed(() => {
  let list = genres.value.slice()
  const q = searchQuery.value.trim().toLowerCase()
  if (q) list = list.filter(g => (g.name || '').toLowerCase().includes(q))
  return list.sort((a, b) =>
    sortOrder.value === 'asc'
      ? a.name.localeCompare(b.name)
      : b.name.localeCompare(a.name)
  )
})

async function loadData() {
  try {
    const [userRes, genresRes, statsRes] = await Promise.all([
      axios.get('/userprofile/info/'),
      axios.get('/genres/'),
      axios.get('/genres/stats/')
    ])
    user.value = userRes.data
    genres.value = genresRes.data
    genreStats.value = statsRes.data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить данные', showNotification)
  }
}

function resetForm() {
  Object.assign(form, { id: null, name: '' })
}
function openEdit(genre) {
  if (!isAdmin.value) return
  Object.assign(form, { id: genre.id, name: genre.name || '' })
  dialogs.edit = true
}
function openDelete(genre) {
  if (!isAdmin.value) return
  Object.assign(form, { id: genre.id, name: genre.name || '' })
  dialogs.delete = true
}
async function saveForm() {
  const name = form.name.trim()
  if (!name || !isAdmin.value) {
    showNotification({ visible: true, message: 'Введите название жанра', type: 'warning' })
    return
  }
  try {
    const url = form.id ? `/genres/${form.id}/` : '/genres/'
    const method = form.id ? axios.put : axios.post
    await method(url, { name })
    dialogs.edit = false
    resetForm()
    await loadData()
    showNotification({ visible: true, message: form.id ? 'Сохранено' : 'Добавлено', type: 'success' })
  } catch (err) {
    handleApiError(err, 'Ошибка сохранения', showNotification)
  }
}
async function deleteGenre() {
  if (!isAdmin.value || !form.id) return
  try {
    await axios.delete(`/genres/${form.id}/`)
    dialogs.delete = false
    resetForm()
    await loadData()
    showNotification({ visible: true, message: 'Удалено', type: 'danger' })
  } catch (err) {
    handleApiError(err, 'Ошибка удаления', showNotification)
  }
}

async function exportFile(type) {
  if (!isAdmin.value) return
  try {
    const res = await axios.get('/genres/export/', { params: { type }, responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `genres.${type === 'excel' ? 'xlsx' : 'docx'}`
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    handleApiError(err, 'Ошибка экспорта', showNotification)
  }
}

onMounted(loadData)
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card class="pa-4" elevation="2">
          <div class="d-flex justify-space-between align-center mb-4">
            <div>
              <h2>Жанры</h2>
              <div class="text-body-2 text-medium-emphasis">
                Всего жанров: {{ genreStats?.count || 0 }},
                самый популярный: {{ genreStats?.top || 'нет данных' }}
              </div>
            </div>
            <div class="d-flex gap-2" v-if="isAdmin">
              <v-btn @click="exportFile('excel')" color="success" variant="outlined" prepend-icon="mdi-microsoft-excel">
                Excel
              </v-btn>
              <v-btn @click="exportFile('word')" color="indigo" variant="outlined" prepend-icon="mdi-file-word">
                Word
              </v-btn>
            </div>
          </div>

          <v-row class="mb-4" align="center">
            <v-col cols="12" md="4">
              <v-text-field v-model="searchQuery" label="Поиск по жанрам" variant="outlined" clearable 
                prepend-inner-icon="mdi-magnify" density="comfortable" />
            </v-col>
            <v-col cols="12" md="3">
              <v-select v-model="sortOrder"
                :items="[{ title: 'От A до Я', value: 'asc' }, { title: 'От Я до A', value: 'desc' }]"
                item-title="title" item-value="value" label="Сортировка" variant="outlined" density="comfortable" />
            </v-col>
            <v-col cols="12" md="5" v-if="isAdmin" class="d-flex gap-2">
              <v-text-field v-model="form.name" label="Новый жанр" variant="outlined" density="comfortable"
                @keyup.enter="saveForm" />
              <v-btn color="primary" prepend-icon="mdi-plus" @click="saveForm" height="48">Добавить жанр</v-btn>
            </v-col>
          </v-row>


          <v-list lines="one">
            <v-list-item v-for="genre in filteredGenres" :key="genre.id" :title="genre.name">
              <template #append>
                <div v-if="isAdmin" class="d-flex gap-2">
                  <v-btn icon size="small" variant="text" color="primary" @click.stop="openEdit(genre)">
                    <v-icon icon="mdi-pencil" />
                  </v-btn>
                  <v-btn icon size="small" variant="text" color="error" @click.stop="openDelete(genre)">
                    <v-icon icon="mdi-delete" />
                  </v-btn>
                </div>
              </template>
            </v-list-item>
            <v-list-item v-if="!filteredGenres.length" title="Жанров пока нет"
              subtitle="Добавьте первый жанр, чтобы начать." />
          </v-list>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="dialogs.edit" max-width="420" v-if="isAdmin">
      <v-card>
        <v-card-title>Редактировать жанр</v-card-title>
        <v-card-text>
          <v-text-field v-model="form.name" label="Название жанра" variant="outlined" density="comfortable" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="dialogs.edit = false">Отмена</v-btn>
          <v-btn color="primary" @click="saveForm">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialogs.delete" max-width="420" v-if="isAdmin">
      <v-card>
        <v-card-title>Удалить жанр</v-card-title>
        <v-card-text>
          Вы уверены, что хотите удалить жанр <strong>{{ form.name }}</strong>?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="dialogs.delete = false">Отмена</v-btn>
          <v-btn color="error" @click="deleteGenre">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
