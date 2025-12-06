<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { showNotification, handleApiError } from '../utils'
import { useUserStore } from '../stores/userStore'

const members = ref([])
const filteredMembers = ref([])
const memberStats = ref(null)
const userStore = useUserStore()

const searchQuery = ref('')
const isAdmin = computed(() => userStore.isSuperUser)

const notification = reactive({ visible: false, message: '', type: 'success' })

const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)

const headers = [
  { title: 'Имя', value: 'username' },
  { title: 'Email', value: 'email' },
  { title: 'Возраст', value: 'age' },
  { title: 'Роль', value: 'role' },
  { title: 'Действия', value: 'actions', align: 'end' },
]

const memberToAdd = reactive({
  username: '',
  email: '',
  password: '',
  age: null,
  is_superuser: false,
  is_staff: false,
})

const memberToEdit = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  age: null,
  is_superuser: false,
  is_staff: false,
})

const memberToDelete = reactive({
  id: null,
  username: '',
})

async function loadMembers() {
  try {
    const r = await axios.get('/members/')
    members.value = r.data
    applyFilter()
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить список читателей', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

async function loadMemberStats() {
  try {
    const r = await axios.get('/members/stats/', {
      headers: { Authorization: `Bearer ${localStorage.getItem('authToken')}` },
    })
    memberStats.value = r.data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить статистику', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

function applyFilter() {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) {
    filteredMembers.value = members.value.slice()
    return
  }
  filteredMembers.value = members.value.filter(m =>
    (m.username || '').toLowerCase().includes(q)
  )
}

async function addMember() {
  if (!isAdmin.value) return
  if (!memberToAdd.username || !memberToAdd.email || !memberToAdd.password) {
    showNotification(notification, 'Заполните имя, email и пароль', 'warning')
    return
  }
  try {
    await axios.post('/members/', memberToAdd)
    Object.assign(memberToAdd, {
      username: '', email: '', password: '', age: null, is_superuser: false, is_staff: false
    })
    showAddDialog.value = false
    await loadMembers()
    await loadMemberStats()
    showNotification(notification, 'Читатель добавлен', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при добавлении читателя', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

function openEditDialog(member) {
  if (!isAdmin.value) return
  Object.assign(memberToEdit, {
    id: member.id,
    username: member.username || '',
    email: member.email || '',
    password: '',
    age: member.age || null,
    is_superuser: member.is_superuser || false,
    is_staff: member.is_staff || false,
  })
  showEditDialog.value = true
}

async function updateMember() {
  if (!isAdmin.value || !memberToEdit.id) return
  try {
    await axios.put(`/members/${memberToEdit.id}/`, memberToEdit)

    if (!memberToEdit.is_superuser && userStore.isSuperUser) {
      userStore.isSuperUser = false
      localStorage.setItem('is_superuser', 'false')
      window.location.href = '/no-access'
      return
    }

    showEditDialog.value = false
    await loadMembers()
    await loadMemberStats()
    showNotification(notification, 'Изменения сохранены', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при обновлении читателя', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

function openDeleteDialog(member) {
  if (!isAdmin.value) return
  memberToDelete.id = member.id
  memberToDelete.username = member.username || ''
  showDeleteDialog.value = true
}

async function deleteMember() {
  if (!isAdmin.value || !memberToDelete.id) return
  try {
    await axios.delete(`/members/${memberToDelete.id}/`)
    showDeleteDialog.value = false
    await loadMembers()
    await loadMemberStats()
    showNotification(notification, 'Читатель удалён', 'danger')
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении читателя', (msg, type = 'danger') =>
      showNotification(notification, msg, type),
    )
  }
}

async function exportExcel() {
  if (!isAdmin.value) return
  try {
    const response = await axios.get('/members/export/excel/', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'members.xlsx')
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
    const response = await axios.get('/members/export/word/', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'members.docx')
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
  await loadMembers()
  await loadMemberStats()
})
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card class="pa-4" elevation="2">
          <div class="d-flex justify-space-between align-center mb-4">
            <div>
              <h2 class="mb-1">Читатели</h2>
              <div class="text-body-2 text-medium-emphasis">
                Всего: {{ memberStats?.count_users || 0 }},
                админов: {{ memberStats?.count_admins || 0 }}
              </div>
            </div>
            <div class="d-flex gap-2" v-if="isAdmin">
              <v-btn color="success" variant="outlined" @click="exportExcel" prepend-icon="mdi-microsoft-excel">Excel</v-btn>
              <v-btn color="indigo" variant="outlined" @click="exportWord" prepend-icon="mdi-file-word">Word</v-btn>
            </div>
          </div>

          <v-alert v-if="notification.visible" :type="notification.type" class="mb-4" variant="tonal" closable>
            {{ notification.message }}
          </v-alert>

          <v-row class="mb-4" align="center">
            <v-col cols="12" md="6">
              <v-text-field v-model="searchQuery" label="Поиск по читателям"
                variant="outlined" density="comfortable" clearable prepend-inner-icon="mdi-magnify"
                @input="applyFilter" />
            </v-col>
            <v-col cols="12" md="6" class="d-flex justify-end">
              <v-btn v-if="isAdmin" color="primary" prepend-icon="mdi-plus" @click="showAddDialog = true">
                Добавить читателя
              </v-btn>
            </v-col>
          </v-row>

          <v-data-table :headers="headers" :items="filteredMembers" item-key="id" :items-per-page="10" class="elevation-1">
            <template #item.role="{ item }">
              <v-chip :color="item.is_superuser ? 'error' : 'secondary'" variant="flat" size="small">
                {{ item.is_superuser ? 'Администратор' : 'Читатель' }}
              </v-chip>
            </template>

            <template #item.actions="{ item }">
              <div v-if="isAdmin">
                <v-btn variant="text" color="primary" prepend-icon="mdi-pencil" @click="openEditDialog(item)"></v-btn>
                <v-btn variant="text" color="error" prepend-icon="mdi-delete" @click="openDeleteDialog(item)"></v-btn>
              </div>
            </template>

            <template #no-data>
              <div class="text-center pa-6">
                <div class="mb-2">Нет читателей</div>
                <div class="text-body-2 mb-3">Добавьте первого читателя, чтобы начать.</div>
                <v-btn v-if="isAdmin" color="primary" prepend-icon="mdi-plus" @click="showAddDialog = true">
                  Добавить читателя
                </v-btn>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-if="isAdmin" v-model="showAddDialog" max-width="520">
      <v-card>
        <v-card-title>Добавить читателя</v-card-title>
        <v-card-text>
          <v-text-field v-model="memberToAdd.username" label="Имя пользователя" variant="outlined" density="comfortable" class="mb-3" />
          <v-text-field v-model="memberToAdd.email" label="Email" variant="outlined" density="comfortable" class="mb-3" />
          <v-text-field v-model="memberToAdd.password" label="Пароль" type="password" variant="outlined" density="comfortable" class="mb-3" />
          <v-text-field v-model.number="memberToAdd.age" label="Возраст" type="number" variant="outlined" density="comfortable" class="mb-3" />
          <v-switch v-model="memberToAdd.is_superuser" label="Сделать администратором" color="primary" inset />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="showAddDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="addMember">Добавить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-if="isAdmin" v-model="showEditDialog" max-width="520">
      <v-card>
        <v-card-title>Редактировать читателя</v-card-title>
        <v-card-text>
          <v-text-field v-model="memberToEdit.username" label="Имя пользователя" variant="outlined" density="comfortable" class="mb-3" />
          <v-text-field v-model="memberToEdit.email" label="Email" variant="outlined" density="comfortable" class="mb-3" />
          <v-text-field v-model="memberToEdit.password" label="Новый пароль (оставьте пустым, чтобы не менять)" type="password" variant="outlined" density="comfortable" class="mb-3"/>
          <v-text-field v-model.number="memberToEdit.age" label="Возраст" type="number" variant="outlined" density="comfortable" class="mb-3" />
          <v-switch v-model="memberToEdit.is_superuser" label="Администратор" color="primary" inset />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="showEditDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="updateMember">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-if="isAdmin" v-model="showDeleteDialog" max-width="420">
      <v-card>
        <v-card-title class="text-h6">Удалить читателя</v-card-title>
        <v-card-text>Вы уверены, что хотите удалить читателя <strong>{{ memberToDelete.username }}</strong>?</v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="showDeleteDialog = false">Отмена</v-btn>
          <v-btn color="error" @click="deleteMember">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
