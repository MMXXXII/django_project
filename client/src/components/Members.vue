<template>
  <h2>Читатели</h2>

  <!-- Статистика + кнопки экспорта -->
  <div class="stats-line mb-3">
    <div class="stats-left">
      <div class="stat">Количество: {{ memberStats?.count || 0 }}</div>
      <div class="stat">Среднее: {{ memberStats?.avg || 0 }}</div>
      <div class="stat">Максимум: {{ memberStats?.max || 0 }}</div>
      <div class="stat">Минимум: {{ memberStats?.min || 0 }}</div>
    </div>
    <div class="stats-right">
      <button class="btn btn-success btn-sm me-2" @click="exportMembersExcel">Excel</button>
      <button class="btn btn-primary btn-sm" @click="exportMembersWord">Word</button>
    </div>
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
        <input v-model="memberToAdd.first_name" class="form-control" placeholder="Имя" required />
      </div>
      <div class="col-auto">
        <select v-model="memberToAdd.library" class="form-select" required>
          <option value="">Выберите библиотеку</option>
          <option v-for="l in libraries" :key="l.id" :value="Number(l.id)">{{ l.name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <button type="submit" class="btn btn-outline-success">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Список читателей -->
  <ul class="list-group">
    <li v-for="m in filteredMembers" :key="m.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>
        <strong>{{ m.first_name }}</strong>
        <div class="text-muted small">
          {{ librariesById[m.library]?.name ?? 'Нет библиотеки' }}
        </div>
      </div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(m)">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemoveClick(m)">
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
            <option v-for="l in libraries" :key="l.id" :value="Number(l.id)">{{ l.name }}</option>
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

const members = ref([])
const filteredMembers = ref([])
const libraries = ref([])
const memberStats = ref(null)

const memberToAdd = reactive({ first_name: '', library: '' })
const memberToEdit = reactive({ id: null, first_name: '', library: '' })
const memberToDelete = reactive({ id: null, first_name: '' })

let editModalInstance = null
let deleteModalInstance = null

const searchQuery = ref('')
const sortOrder = ref('asc')

const librariesById = computed(() => Object.fromEntries(libraries.value.map(l => [l.id, l])))

// --- API ---
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

// --- Фильтр и сортировка ---
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

// --- CRUD ---
async function onAddMember() {
  if (!memberToAdd.first_name || !memberToAdd.library) return
  await axios.post('/members/', { first_name: memberToAdd.first_name, library: Number(memberToAdd.library) })
  memberToAdd.first_name = ''
  memberToAdd.library = ''
  await fetchMembers()
  await fetchMemberStats()
}

function onEditClick(m) {
  memberToEdit.id = m.id
  memberToEdit.first_name = m.first_name
  memberToEdit.library = m.library
  editModalInstance.show()
}

async function onUpdateMember() {
  if (!memberToEdit.first_name || !memberToEdit.library) return
  await axios.put(`/members/${memberToEdit.id}/`, { first_name: memberToEdit.first_name, library: Number(memberToEdit.library) })
  await fetchMembers()
  await fetchMemberStats()
  editModalInstance.hide()
}

function onRemoveClick(m) {
  memberToDelete.id = m.id
  memberToDelete.first_name = m.first_name
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

// --- Экспорт ---
function exportMembersExcel() { exportMembers('excel') }
function exportMembersWord() { exportMembers('word') }

function exportMembers(type) {
  axios({ url: `/members/export/?type=${type}`, method: 'GET', responseType: 'blob' })
    .then(res => {
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', type === 'excel' ? 'members.xlsx' : 'members.docx')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    })
    .catch(err => { console.error(err); alert('Ошибка при скачивании файла') })
}

// --- Инициализация ---
onMounted(async () => {
  await fetchMembers()
  await fetchLibraries()
  await fetchMemberStats()
  editModalInstance = new bootstrap.Modal(document.getElementById('editMemberModal'))
  deleteModalInstance = new bootstrap.Modal(document.getElementById('deleteMemberModal'))
})
</script>

<style scoped>
.stats-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  font-size: 0.9em;
}
.stats-left { display: flex; gap: 12px; }
.stats-right { display: flex; gap: 6px; }
.stat {
  background: #fafafa;
  border: 1px solid #ddd;
  padding: 4px 10px;
  border-radius: 6px;
  color: #333;
}
</style>
