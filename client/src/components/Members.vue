<template>
  <h2>Читатели</h2>

  <!-- Статистика -->
  <div class="stats-line">
    <div class="stat">Количество: {{ memberStats?.count || 0 }}</div>
    <div class="stat">Среднее: {{ memberStats?.avg || 0 }}</div>
    <div class="stat">Максимум: {{ memberStats?.max || 0 }}</div>
    <div class="stat">Минимум: {{ memberStats?.min || 0 }}</div>
  </div>

  <!-- Поиск -->
  <div class="mb-3">
    <input 
      v-model="searchQuery" 
      type="text" 
      class="form-control" 
      placeholder="Поиск по читателям" 
      @input="filterMembers"
    />
  </div>

  <!-- Сортировка -->
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
        <input 
          v-model="memberToAdd.first_name" 
          class="form-control" 
          placeholder="Имя" 
          required 
        />
      </div>

      <div class="col-auto">
        <select v-model="memberToAdd.library" class="form-select" required>
          <option value="">Выберите библиотеку</option>
          <option v-for="l in libraries" :key="l.id" :value="Number(l.id)">
            {{ l.name }}
          </option>
        </select>
      </div>

      <div class="col-auto">
        <button type="button" class="btn btn-outline-success">Успех</button>
      </div>
    </div>
  </form>

  <!-- Список читателей -->
  <ul class="list-group">
    <li 
      v-for="m in filteredMembers" 
      :key="m.id" 
      class="list-group-item d-flex justify-content-between align-items-center"
    >
      <div>
        <strong>{{ m.first_name }}</strong>
        <div class="text-muted small">
          {{ librariesById[m.library]?.name ?? 'Нет библиотеки' }}
        </div>
      </div>
      <div>
        <!-- Редактировать -->
        <button 
          class="btn btn-sm btn-success me-2" 
          @click="onEditClick(m)"
          data-bs-toggle="modal" 
          data-bs-target="#editMemberModal"
        >
          <i class="bi bi-pen-fill"></i>
        </button>

        <!-- Удалить -->
        <button 
          class="btn btn-sm btn-danger" 
          @click="onRemoveClick(m)"
          data-bs-toggle="modal"
          data-bs-target="#deleteMemberModal"
        >
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модалка редактирования -->
  <div class="modal fade" id="editMemberModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактирование читателя</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input v-model="memberToEdit.first_name" class="form-control mb-2" placeholder="Имя" />
          <select v-model="memberToEdit.library" class="form-select">
            <option v-for="l in libraries" :key="l.id" :value="Number(l.id)">
              {{ l.name }}
            </option>
          </select>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button type="button" class="btn btn-success" @click="onUpdateMember">Сохранить</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Модалка удаления -->
  <div class="modal fade" id="deleteMemberModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Удаление читателя</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          Вы действительно хотите удалить <strong>{{ memberToDelete.first_name }}</strong>?
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button type="button" class="btn btn-danger" @click="confirmDelete">Удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import * as bootstrap from 'bootstrap'

// Данные
const members = ref([])
const filteredMembers = ref([])
const libraries = ref([])
const memberStats = ref(null)

// Добавление и редактирование
const memberToAdd = reactive({ first_name: '', library: '' })
const memberToEdit = reactive({ id: null, first_name: '', library: '' })

// Удаление
const memberToDelete = reactive({ id: null, first_name: '' })
let deleteModalInstance = null

// Поиск и сортировка
const searchQuery = ref('')
const sortOrder = ref('asc')

const librariesById = computed(() =>
  Object.fromEntries(libraries.value.map(l => [l.id, l]))
)

// Получение данных с API
async function fetchMembers() {
  const r = await axios.get('/members/')
  members.value = r.data
  filterMembers()
}

async function fetchLibraries() {
  const r = await axios.get('/libraries/')
  libraries.value = r.data
}

async function fetchMemberStats() {
  const r = await axios.get('/members/stats/')
  memberStats.value = r.data
}

// Фильтр и сортировка
function filterMembers() {
  filteredMembers.value = members.value.filter(m =>
    m.first_name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
  sortMembers()
}

function sortMembers() {
  filteredMembers.value.sort((a, b) => {
    const A = a.first_name.toLowerCase()
    const B = b.first_name.toLowerCase()
    return sortOrder.value === 'asc' ? A.localeCompare(B) : B.localeCompare(A)
  })
}

// Добавление
async function onAddMember() {
  const payload = { 
    first_name: memberToAdd.first_name, 
    library: Number(memberToAdd.library) 
  }
  await axios.post('/members/', payload)
  memberToAdd.first_name = ''
  memberToAdd.library = ''
  await fetchMembers()
  await fetchMemberStats()
}

// Редактирование
function onEditClick(m) {
  memberToEdit.id = m.id
  memberToEdit.first_name = m.first_name
  memberToEdit.library = m.library

  const modalEl = document.getElementById('editMemberModal')
  const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  modalInstance.show()
}

async function onUpdateMember() {
  const payload = { 
    first_name: memberToEdit.first_name, 
    library: Number(memberToEdit.library) 
  }
  await axios.put(`/members/${memberToEdit.id}/`, payload)
  await fetchMembers()
  await fetchMemberStats()
  // закрываем модалку вручную
  const modalEl = document.getElementById('editMemberModal')
  bootstrap.Modal.getInstance(modalEl).hide()
}

// Удаление
function onRemoveClick(m) {
  memberToDelete.id = m.id
  memberToDelete.first_name = m.first_name

  const modalEl = document.getElementById('deleteMemberModal')
  deleteModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  deleteModalInstance.show()
}

async function confirmDelete() {
  if (!memberToDelete.id) return
  await axios.delete(`/members/${memberToDelete.id}/`)
  await fetchMembers()
  await fetchMemberStats()
  deleteModalInstance.hide()
  memberToDelete.id = null
  memberToDelete.first_name = ''
}

// Инициализация
onMounted(async () => {
  await fetchMembers()
  await fetchLibraries()
  await fetchMemberStats()
})
</script>

<style scoped>
.stats-line {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
  font-size: 0.9em;
}

.stat {
  background: #fafafa;
  border: 1px solid #ddd;
  padding: 4px 10px;
  border-radius: 6px;
  color: #333;
}
</style>
  