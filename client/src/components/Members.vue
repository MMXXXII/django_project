<template>
  <h2>Читатели <span style="font-size: 0.9em; color: #6c757d;">count ({{ memberStats ? memberStats.count : 0 }}), avg ({{ memberStats ? memberStats.avg : 0 }}), max ({{ memberStats ? memberStats.max : 0 }}), min ({{ memberStats ? memberStats.min : 0 }})</span></h2>


  <!-- Форма добавления -->
  <form class="mb-3" @submit.prevent="onAddMember">
    <div class="row g-2 align-items-center">
      <div class="col">
        <input
          v-model="memberToAdd.first_name"
          class="form-control"
          placeholder="Имя"
          required
        />
      </div>
      <div class="col-auto">
        <select v-model="memberToAdd.library" class="form-select" required>
          <option v-for="l in libraries" :value="l.id" :key="l.id">
            {{ l.name }}
          </option>
        </select>
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Список -->
  <ul class="list-group">
    <li
      v-for="m in members"
      :key="m.id"
      class="list-group-item d-flex justify-content-between align-items-center"
    >
      <div>
        <strong>{{ m.first_name }}</strong>
        <div class="text-muted small">
          {{ librariesById[m.library]?.name }}
        </div>
      </div>
      <div>
        <button
          class="btn btn-sm btn-success me-2"
          @click="onEditClick(m)"
          data-bs-toggle="modal"
          data-bs-target="#editMemberModal"
        >
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(m)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модал редактирования -->
  <div class="modal fade" id="editMemberModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать читателя</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input
            v-model="memberToEdit.first_name"
            class="form-control mb-2"
            placeholder="Имя"
          />
          <select v-model="memberToEdit.library" class="form-select">
            <option v-for="l in libraries" :value="l.id" :key="l.id">
              {{ l.name }}
            </option>
          </select>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button
            class="btn btn-primary"
            data-bs-dismiss="modal"
            @click="onUpdateMember"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// Состояния и переменные
const members = ref([])
const libraries = ref([])
const memberStats = ref(null) // Статистика
const memberToAdd = ref({ first_name: '', library: null })
const memberToEdit = ref({ id: null, first_name: '', library: null })
const isLoading = ref(true)  // Флаг для отображения загрузки

// Сопоставление библиотек по ID
const librariesById = computed(() => Object.fromEntries(libraries.value.map(l => [l.id, l])))

// Функции для получения данных
async function fetchMembers() {
  try {
    const res = await axios.get('/members/')
    members.value = res.data
  } catch (error) {
    console.error('Ошибка при получении читателей:', error)
  } finally {
    isLoading.value = false
  }
}

async function fetchLibraries() {
  try {
    const res = await axios.get('/libraries/')
    libraries.value = res.data
  } catch (error) {
    console.error('Ошибка при получении библиотек:', error)
  }
}

// Получение статистики по читателям
async function fetchMemberStats() {
  try {
    const response = await axios.get('/members/stats') // Эндпоинт для статистики
    memberStats.value = response.data // Сохраняем количество читателей в переменной
  } catch (error) {
    console.error('Ошибка при получении статистики читателей:', error)
  }
}

// Функция для добавления читателя
async function onAddMember() {
  await axios.post('/members/', { ...memberToAdd.value })
  memberToAdd.value = { first_name: '', library: null }
  await fetchMembers() // Обновляем список после добавления
}

// Функция для удаления читателя
async function onRemove(m) {
  if (!confirm(`Удалить читателя "${m.first_name}"?`)) return
  await axios.delete(`/members/${m.id}/`)
  await fetchMembers() // Обновляем список после удаления
}

// Функция для редактирования читателя
function onEditClick(m) {
  memberToEdit.value = { ...m }
}

// Функция для обновления данных читателя
async function onUpdateMember() {
  await axios.put(`/members/${memberToEdit.value.id}/`, { ...memberToEdit.value })
  await fetchMembers() // Обновляем читателей после редактирования
}

// Монтирование компонента
onMounted(async () => {
  await Promise.all([fetchMembers(), fetchLibraries(), fetchMemberStats()])
})
</script>
