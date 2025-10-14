<template>
  <h2>Библиотеки</h2>

  <!-- Форма добавления -->
  <form class="mb-3" @submit.prevent="onAddLibrary">
    <div class="row g-2 align-items-center">
      <div class="col">
        <input
          v-model="libraryToAdd.name"
          class="form-control"
          placeholder="Название библиотеки"
          required
        />
      </div>
      <div class="col">
        <input
          v-model="libraryToAdd.address"
          class="form-control"
          placeholder="Адрес"
          required
        />
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Список -->
  <ul class="list-group">
    <li
      v-for="l in libraries"
      :key="l.id"
      class="list-group-item d-flex justify-content-between align-items-center"
    >
      <div>
        <strong>{{ l.name }}</strong><br />
        <span class="text-muted small">{{ l.address }}</span>
      </div>
      <div>
        <button
          class="btn btn-sm btn-success me-2"
          @click="onEditClick(l)"
          data-bs-toggle="modal"
          data-bs-target="#editLibraryModal"
        >
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(l)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модал редактирования -->
  <div class="modal fade" id="editLibraryModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать библиотеку</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input
            v-model="libraryToEdit.name"
            class="form-control mb-2"
            placeholder="Название"
          />
          <input
            v-model="libraryToEdit.address"
            class="form-control"
            placeholder="Адрес"
          />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button
            class="btn btn-primary"
            data-bs-dismiss="modal"
            @click="onUpdateLibrary"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeMount, computed } from 'vue'
import axios from 'axios'
import { onMounted } from 'vue'



const libraries = ref([])
const libraryToAdd = ref({ name: '', address: '' })
const libraryToEdit = ref({ id: null, name: '', address: '' })
const isLoading = ref(true)

async function fetchLibraries() {
  try {
    const res = await axios.get('/libraries/')
    libraries.value = res.data
  } catch (error) {
    console.error('Ошибка при получении библиотек:', error)
  } finally {
    isLoading.value = false
  }
}

async function onAddLibrary() {
  await axios.post('/libraries/', { ...libraryToAdd.value })
  libraryToAdd.value = { name: '', address: '' }
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
  await fetchLibraries() // Обновляем библиотеки после редактирования
}

onMounted(async () => {
  try {
    await Promise.all([fetchLibraries()])
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error)
  }
});
</script>
