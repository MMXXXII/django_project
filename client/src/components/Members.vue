<template>
  <h2>Читатели 
    <span style="font-size: 0.9em; color: #6c757d;">
      count ({{ memberStats ? memberStats.count : 0 }}), 
      avg ({{ memberStats ? memberStats.avg : 0 }}), 
      max ({{ memberStats ? memberStats.max : 0 }}), 
      min ({{ memberStats ? memberStats.min : 0 }})
    </span>
  </h2>

  <!-- Фильтрация -->
  <div class="mb-3">
    <input 
      v-model="searchQuery" 
      type="text" 
      class="form-control" 
      placeholder="Поиск по читателям" 
      @input="filterMembers"
    />
  </div>

  <!-- Фильтр по алфавиту -->
  <div class="mb-3">
    <select v-model="sortOrder" @change="sortMembers" class="form-select">
      <option value="asc">От A до Я</option>
      <option value="desc">От Я до A</option>
    </select>
  </div>

  <!-- Форма добавления -->
  <form class="mb-3" @submit.prevent="onAddMember">
    <div class="row g-2 align-items-center">
      <div class="col">
        <input v-model="memberToAdd.first_name" class="form-control" placeholder="Имя" required />
      </div>
      <div class="col-auto">
        <select v-model="memberToAdd.library" class="form-select" required>
          <option v-for="l in libraries" :value="l.id" :key="l.id">{{ l.name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Список -->
  <ul class="list-group">
    <li v-for="m in filteredMembers" :key="m.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>
        <strong>{{ m.first_name }}</strong>
        <div class="text-muted small">
          {{ librariesById[m.library]?.name }}
        </div>
      </div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(m)" data-bs-toggle="modal" data-bs-target="#editMemberModal">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(m)"><i class="bi bi-x"></i></button>
      </div>
    </li>
  </ul>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// Состояния и переменные
const members = ref([]) // Храним всех читателей
const filteredMembers = ref([]) // Храним фильтрованных читателей
const libraries = ref([]) // Библиотеки
const memberStats = ref(null) // Статистика
const memberToAdd = ref({ first_name: '', library: null })
const memberToEdit = ref({ id: null, first_name: '', library: null })
const searchQuery = ref("") // Состояние для поиска по имени читателя
const sortOrder = ref("asc") // Состояние для сортировки (по умолчанию от A до Я)

const librariesById = computed(() => Object.fromEntries(libraries.value.map(l => [l.id, l])))

async function fetchMembers() {
  try {
    const res = await axios.get('/members/')
    members.value = res.data
    filteredMembers.value = members.value
  } catch (error) {
    console.error('Ошибка при получении читателей:', error)
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

async function fetchMemberStats() {
  try {
    const response = await axios.get('/members/stats') // Эндпоинт для статистики
    memberStats.value = response.data // Сохраняем статистику по читателям в переменной
  } catch (error) {
    console.error('Ошибка при получении статистики читателей:', error)
  }
}

// Фильтрация по имени
function filterMembers() {
  filteredMembers.value = members.value.filter(member =>
    member.first_name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
  sortMembers() // После фильтрации, сортируем
}

// Сортировка по алфавиту
function sortMembers() {
  filteredMembers.value.sort((a, b) => {
    const nameA = a.first_name.toLowerCase()
    const nameB = b.first_name.toLowerCase()

    if (sortOrder.value === "asc") {
      return nameA.localeCompare(nameB)
    } else {
      return nameB.localeCompare(nameA)
    }
  })
}

async function onAddMember() {
  await axios.post('/members/', { ...memberToAdd.value })
  memberToAdd.value = { first_name: '', library: null }
  await fetchMembers() // Обновляем список после добавления
}

async function onRemove(m) {
  if (!confirm(`Удалить читателя "${m.first_name}"?`)) return
  await axios.delete(`/members/${m.id}/`)
  await fetchMembers() // Обновляем список после удаления
}

function onEditClick(m) {
  memberToEdit.value = { ...m }
}

async function onUpdateMember() {
  await axios.put(`/members/${memberToEdit.value.id}/`, { ...memberToEdit.value })
  await fetchMembers() // Обновляем список после редактирования
  await fetchMemberStats() // Обновляем статистику по читателям
}

onMounted(async () => {
  try {
    await Promise.all([fetchMembers(), fetchLibraries(), fetchMemberStats()])
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error)
  }
})
</script>
