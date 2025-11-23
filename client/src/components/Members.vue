<template>
  <div>
    <h2>Читатели</h2>

    <!-- Статистика и кнопки -->
    <div class="stats-line">
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
        <div class="col" v-if="libraries.length">
          <select v-model="memberToAdd.library" class="form-select" required>
            <option value="" disabled>Выберите библиотеку</option>
            <option v-for="l in libraries" :key="l.id" :value="l.id">{{ l.name }}</option>
          </select>
        </div>
        <div class="col">
          <input type="file" @change="onFileChange($event, memberToAdd)" class="form-control" />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-outline-success">Добавить</button>
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
        <div class="d-flex align-items-center gap-2">
          <img 
            v-if="m.photo_url" 
            :src="m.photo_url" 
            alt="Фото" 
            class="img-thumbnail" 
            style="height:50px; cursor:pointer;" 
            @click="showPhotoModal(m.photo_url)" 
          />
          <div>
            <strong>{{ m.first_name }}</strong>
            <div class="text-muted small">{{ librariesById[m.library]?.name || 'Нет библиотеки' }}</div>
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

    <!-- Модалки -->
    <div class="modal fade" id="editMemberModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактирование читателя</h5>
            <button type="button" class="btn-close" @click="hideEditModal"></button>
          </div>
          <div class="modal-body">
            <input v-model="memberToEdit.first_name" class="form-control mb-2" placeholder="Имя" />
            <select v-model="memberToEdit.library" class="form-select mb-2" v-if="libraries.length">
              <option v-for="l in libraries" :key="l.id" :value="l.id">{{ l.name }}</option>
            </select>
            <input type="file" @change="onFileChange($event, memberToEdit)" class="form-control mb-2" />
            <div v-if="memberToEdit.photo_url" class="mt-2">
              <img :src="memberToEdit.photo_url" alt="Фото" class="img-thumbnail" style="height:100px; cursor:pointer;" @click="showPhotoModal(memberToEdit.photo_url)" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideEditModal">Отмена</button>
            <button type="button" class="btn btn-success" @click="onUpdateMember">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="deleteMemberModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Удаление читателя</h5>
            <button type="button" class="btn-close" @click="hideDeleteModal"></button>
          </div>
          <div class="modal-body">
            Вы действительно хотите удалить <strong>{{ memberToDelete.first_name }}</strong>?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideDeleteModal">Отмена</button>
            <button type="button" class="btn btn-danger" @click="confirmDelete">Удалить</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="photoModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-body text-center">
            <img :src="photoModalUrl" alt="Фото читателя" class="img-fluid" />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          </div>
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
const memberStats = ref([])
const libraries = ref([])

const memberToAdd = reactive({ first_name: '', library: null, photoFile: null })
const memberToEdit = reactive({ id: null, first_name: '', library: null, photoFile: null, photo_url: null, modalInstance: null })
const memberToDelete = reactive({ id: null, first_name: '' })

const searchQuery = ref('')
const sortOrder = ref('asc')
const photoModalUrl = ref(null)
let photoModalInstance = null
let deleteModalInstance = null

const librariesById = computed(() => Object.fromEntries(libraries.value.map(l => [l.id, l])))

// --- API ---
async function fetchMembers() {
  const r = await axios.get('/members/')
  members.value = r.data.map(m => ({
    ...m,
    photo_url: m.photo_url || null
  }))
  filterMembers()
}
async function fetchLibraries() { libraries.value = (await axios.get('/libraries/')).data }
async function fetchMemberStats() { memberStats.value = (await axios.get('/members/stats/')).data }

// --- Фильтр / сортировка ---
function filterMembers() {
  filteredMembers.value = members.value.filter(m => m.first_name.toLowerCase().includes(searchQuery.value.toLowerCase()))
  sortMembers()
}
function sortMembers() {
  filteredMembers.value.sort((a, b) => {
    const A = a.first_name.toLowerCase()
    const B = b.first_name.toLowerCase()
    return sortOrder.value === 'asc' ? A.localeCompare(B) : B.localeCompare(A)
  })
}

// --- Файлы ---
function onFileChange(e, memberObj) {
  const file = e.target.files[0]
  if (file) memberObj.photoFile = file
}
function showPhotoModal(url) {
  photoModalUrl.value = url
  if (!photoModalInstance) {
    const modalEl = document.getElementById('photoModal')
    photoModalInstance = new bootstrap.Modal(modalEl)
  }
  photoModalInstance.show()
}

// --- CRUD ---
async function onAddMember() {
  const formData = new FormData()
  formData.append('first_name', memberToAdd.first_name)
  formData.append('library', memberToAdd.library)
  if (memberToAdd.photoFile) formData.append('photo', memberToAdd.photoFile)
  await axios.post('/members/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  memberToAdd.first_name = ''
  memberToAdd.library = null
  memberToAdd.photoFile = null
  await fetchMembers()
  await fetchMemberStats()
}

function onEditClick(m) {
  memberToEdit.id = m.id
  memberToEdit.first_name = m.first_name
  memberToEdit.library = m.library
  memberToEdit.photo_url = m.photo_url
  memberToEdit.photoFile = null
  const modalEl = document.getElementById('editMemberModal')
  memberToEdit.modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  memberToEdit.modalInstance.show()
}
async function onUpdateMember() {
  const formData = new FormData()
  formData.append('first_name', memberToEdit.first_name)
  formData.append('library', memberToEdit.library)
  if (memberToEdit.photoFile) formData.append('photo', memberToEdit.photoFile)
  await axios.put(`/members/${memberToEdit.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  hideEditModal()
  await fetchMembers()
  await fetchMemberStats()
}
function hideEditModal() {
  if (memberToEdit.modalInstance) memberToEdit.modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  memberToEdit.id = null
  memberToEdit.first_name = ''
  memberToEdit.library = null
  memberToEdit.photoFile = null
  memberToEdit.photo_url = null
}

// --- Удаление ---
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
  hideDeleteModal()
  await fetchMembers()
  await fetchMemberStats()
}
function hideDeleteModal() {
  if (deleteModalInstance) deleteModalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
  memberToDelete.id = null
  memberToDelete.first_name = ''
}

// --- Экспорт ---
function exportMembersExcel() { exportData('excel') }
function exportMembersWord() { exportData('word') }
function exportData(type) {
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
  await fetchLibraries()
  await fetchMembers()
  await fetchMemberStats()
})
</script>

<style scoped>
.stats-line { display:flex; justify-content:space-between; gap:12px; margin-bottom:14px; font-size:0.9em; }
.stats-left { display:flex; gap:12px; }
.stats-right { display:flex; gap:6px; }
.stat { background:#fafafa; border:1px solid #ddd; padding:4px 10px; border-radius:6px; color:#333; }
.img-thumbnail { border-radius:4px; }
</style>
