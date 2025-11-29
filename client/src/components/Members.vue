<template>
  <div>
    <h2>Читатели</h2>
    <!-- Статистика + кнопки -->
    <div class="stats-line">
      <div class="stats-left">
        <div class="stat">Читателей: {{ memberStats?.count_users || 0 }}</div>
        <div class="stat">Администраторов: {{ memberStats?.count_admins || 0 }}</div>
        <div class="stat">Средний возраст польз-ей: {{ memberStats?.avg_age_users || 0 }} лет</div>
        <div class="stat">Средний возраст админ-ов: {{ memberStats?.avg_age_admins || 0 }} лет</div>
        <div class="stat">Среднее кол-во книг, взятых читателями: {{ memberStats?.avg_books || 0 }}</div>
      </div>
      <div class="stats-right">
        <button class="btn btn-success btn-sm me-2" @click="exportMembersExcel">Excel</button>
        <button class="btn btn-primary btn-sm" @click="exportMembersWord">Word</button>
      </div>
    </div>

    <!-- Поиск -->
    <div class="mb-3">
      <input v-model="searchQuery" type="text" class="form-control" placeholder="Поиск по читателям"
        @input="filterMembers" />
    </div>

    <!-- Сортировка + Кнопка Добавить -->
    <div class="mb-3 d-flex gap-3 align-items-stretch">
      <select v-model="sortOrder" @change="sortMembers" class="form-select flex-grow-1">
        <option value="asc">От A до Я</option>
        <option value="desc">От Я до A</option>
        <option value="admin_first">Администратор → Пользователь</option>
        <option value="user_first">Пользователь → Администратор</option>
      </select>
      <button class="btn btn-outline-success" @click="showAddModal" style="white-space: nowrap;">Добавить
        читателя</button>
    </div>

    <!-- Массовое удаление -->
    <div v-if="selectedMembers.length" class="mb-3">
      <button class="btn btn-danger" @click="showDeleteSelectedModal">
        Удалить выбранные ({{ selectedMembers.length }})
      </button>
    </div>

    <!-- Список читателей -->
    <ul class="list-group">
      <li v-for="m in filteredMembers" :key="m.id"
        class="list-group-item d-flex justify-content-between align-items-center"
        :class="{ 'selected': selectedMembers.includes(m.id) }" @click="toggleSelection(m.id)">
        <div>
          <div class="d-flex align-items-center gap-2">
            <strong>{{ m.username || m.first_name }}</strong>
            <span v-if="m.is_superuser" class="badge bg-danger">Администратор</span>
            <span v-else class="badge bg-secondary">Пользователь</span>
          </div>
          <div class="small text-muted">{{ m.email }}</div>
        </div>
        <div>
          <button class="btn btn-sm btn-success me-2" @click.stop="onEditClick(m)">
            <i class="bi bi-pen-fill"></i>
          </button>
          <button class="btn btn-sm btn-danger" @click.stop="onRemoveClick(m)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </li>
    </ul>

    <!-- Модалки -->
    <div class="modal fade" id="addMemberModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Добавление нового читателя</h5>
            <button type="button" class="btn-close" @click="hideAddModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Имя пользователя</label>
              <input v-model="memberToAdd.username" class="form-control" placeholder="Имя пользователя" />
            </div>
            <div class="mb-3">
              <label class="form-label">Электронная почта</label>
              <input v-model="memberToAdd.email" class="form-control" placeholder="Электронная почта" />
            </div>
            <div class="mb-3">
              <label class="form-label">Возраст</label>
              <input type="number" v-model="memberToAdd.age" class="form-control" placeholder="Возраст" />
            </div>
            <div class="mb-3">
              <label class="form-label">Пароль</label>
              <input type="password" v-model="memberToAdd.password" class="form-control" placeholder="Пароль" />
            </div>
            <div class="mb-3">
              <input type="checkbox" v-model="memberToAdd.is_superuser" class="form-check-input" id="addIsSuperUser" />
              <label for="addIsSuperUser" class="form-check-label ms-2">Администратор</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideAddModal">Отмена</button>
            <button type="button" class="btn btn-success" @click="onAddMember">Добавить</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editMemberModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактирование читателя</h5>
            <button type="button" class="btn-close" @click="hideEditModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Имя пользователя</label>
              <input v-model="memberToEdit.username" class="form-control" placeholder="Имя пользователя" />
            </div>
            <div class="mb-3">
              <label class="form-label">Электронная почта</label>
              <input v-model="memberToEdit.email" class="form-control" placeholder="Электронная почта" />
            </div>
            <div class="mb-3">
              <label class="form-label">Возраст</label>
              <input type="number" v-model="memberToEdit.age" class="form-control" placeholder="Возраст" />
            </div>
            <div class="mb-3">
              <label class="form-label">Новый пароль</label>
              <input type="password" v-model="memberToEdit.password" class="form-control" placeholder="Новый пароль" />
            </div>
            <div class="mb-3">
              <input type="checkbox" v-model="memberToEdit.is_superuser" class="form-check-input"
                id="editIsSuperUser" />
              <label for="editIsSuperUser" class="form-check-label ms-2">Администратор</label>
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
            Вы действительно хотите удалить <strong>{{ memberToDelete.username }}</strong>?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideDeleteModal">Отмена</button>
            <button type="button" class="btn btn-danger" @click="confirmDelete">Удалить</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="deleteSelectedModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Удаление выбранных читателей</h5>
            <button type="button" class="btn-close" @click="hideDeleteSelectedModal"></button>
          </div>
          <div class="modal-body">
            Вы действительно хотите удалить <strong>{{ selectedMembers.length }}</strong> выбранных читателей?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideDeleteSelectedModal">Отмена</button>
            <button type="button" class="btn btn-danger" @click="confirmDeleteSelected">Удалить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import * as bootstrap from 'bootstrap'
import { useUserStore } from '../stores/userStore'


const members = ref([])
const filteredMembers = ref([])
const memberStats = ref([])
const searchQuery = ref('')
const sortOrder = ref('asc')
const selectedMembers = ref([])
const memberToAdd = reactive({ username: '', email: '', password: '', age: null, is_superuser: false, is_staff: false })
const memberToEdit = reactive({ id: null, username: '', email: '', password: '', age: null, is_superuser: false, is_staff: false })
const memberToDelete = reactive({ id: null, username: '' })
const userStore = useUserStore()

let deleteSelectedModalInstance = null

onMounted(() => {
  fetchMembers();
  fetchMemberStats();
})

async function fetchMembers() {
  const response = await axios.get('/members/');
  members.value = response.data;
  filterMembers();
}

function filterMembers() {
  filteredMembers.value = members.value.filter(m => m.username.toLowerCase().includes(searchQuery.value.toLowerCase()));
  sortMembers();
}

function sortMembers() {
  filteredMembers.value.sort((a, b) => {
    if (sortOrder.value === 'admin_first') {
      if (a.is_superuser && !b.is_superuser) return -1;
      if (!a.is_superuser && b.is_superuser) return 1;
      return a.username.toLowerCase().localeCompare(b.username.toLowerCase());
    } else if (sortOrder.value === 'user_first') {
      if (!a.is_superuser && b.is_superuser) return -1;
      if (a.is_superuser && !b.is_superuser) return 1;
      return a.username.toLowerCase().localeCompare(b.username.toLowerCase());
    } else {
      const A = a.username.toLowerCase();
      const B = b.username.toLowerCase();
      return sortOrder.value === 'asc' ? A.localeCompare(B) : B.localeCompare(A);
    }
  });
}

function onEditClick(m) {
  memberToEdit.id = m.id;
  memberToEdit.username = m.username;
  memberToEdit.email = m.email;
  memberToEdit.age = m.age || null;
  memberToEdit.is_superuser = m.is_superuser;
  memberToEdit.is_staff = m.is_staff;
  const modalEl = document.getElementById('editMemberModal');
  const modalInstance = new bootstrap.Modal(modalEl);
  modalInstance.show();
}

// В методе onUpdateMember, при изменении прав администратора:
async function onUpdateMember() {
  const formData = new FormData();
  formData.append('username', memberToEdit.username);
  formData.append('email', memberToEdit.email);
  if (memberToEdit.age) formData.append('age', memberToEdit.age);
  if (memberToEdit.password) formData.append('password', memberToEdit.password);
  formData.append('is_superuser', memberToEdit.is_superuser);
  formData.append('is_staff', memberToEdit.is_staff);

  // Сохраняем данные на сервере
  await axios.put(`/members/${memberToEdit.id}/`, formData);

  // Обновляем состояние в Pinia Store и localStorage
  userStore.isSuperUser = memberToEdit.is_superuser;  // Обновляем состояние в Pinia
  localStorage.setItem('is_superuser', memberToEdit.is_superuser.toString());  // Сохраняем в localStorage

  // Если права администратора утеряны, перенаправляем на страницу с ограниченным доступом
  if (!memberToEdit.is_superuser) {
    userStore.isSuperUser = false;  // Обновляем статус в Pinia
    localStorage.setItem('is_superuser', 'false');  // Обновляем в localStorage
    window.location.href = '/no-access';  // Перенаправление на страницу с ограниченным доступом
  } else {
    // В противном случае обновляем список пользователей
    await fetchMembers();
    await fetchMemberStats();
    hideEditModal();
  }
}





function showAddModal() {
  memberToAdd.username = '';
  memberToAdd.email = '';
  memberToAdd.password = '';
  memberToAdd.age = null;
  memberToAdd.is_superuser = false;
  memberToAdd.is_staff = false;

  const modalEl = document.getElementById('addMemberModal');
  const modalInstance = new bootstrap.Modal(modalEl);
  modalInstance.show();
}

async function onAddMember() {
  const formData = new FormData();
  formData.append('username', memberToAdd.username);
  formData.append('email', memberToAdd.email);
  formData.append('password', memberToAdd.password);
  if (memberToAdd.age) formData.append('age', memberToAdd.age);
  formData.append('is_superuser', memberToAdd.is_superuser);
  formData.append('is_staff', memberToAdd.is_staff);

  await axios.post('/members/', formData);
  await fetchMembers();
  await fetchMemberStats();
  hideAddModal();
}

function onRemoveClick(m) {
  memberToDelete.id = m.id;
  memberToDelete.username = m.username;
  const modalEl = document.getElementById('deleteMemberModal');
  const modalInstance = new bootstrap.Modal(modalEl);
  modalInstance.show();
}

async function confirmDelete() {
  const deletedId = memberToDelete.id;
  await axios.delete(`/members/${deletedId}/`);

  // Убираем удаленного читателя из выделенных
  selectedMembers.value = selectedMembers.value.filter(id => id !== deletedId);

  await fetchMembers();
  await fetchMemberStats();
  hideDeleteModal();
}

function toggleSelection(id) {
  if (selectedMembers.value.includes(id)) {
    selectedMembers.value = selectedMembers.value.filter(x => x !== id);
  } else {
    selectedMembers.value.push(id);
  }
}

function showDeleteSelectedModal() {
  const modalEl = document.getElementById('deleteSelectedModal');
  deleteSelectedModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
  deleteSelectedModalInstance.show();
}

function hideDeleteSelectedModal() {
  if (deleteSelectedModalInstance) deleteSelectedModalInstance.hide();
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
}

async function confirmDeleteSelected() {
  await Promise.all(selectedMembers.value.map(id => axios.delete(`/members/${id}/`)));
  selectedMembers.value = [];
  hideDeleteSelectedModal();
  await fetchMembers();
  await fetchMemberStats();
}

async function fetchMemberStats() {
  try {
    const response = await axios.get('/members/stats/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      }
    });
    memberStats.value = response.data;
  } catch (error) {
    console.error('Ошибка при получении данных:', error);
    if (error.response && error.response.status === 403) {
      router.push('/no-access'); // Если нет доступа, перенаправить
    }
  }
}

async function exportMembersExcel() {
  const response = await axios.get('/members/export/excel/', { responseType: 'blob' });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'members.xlsx');
  document.body.appendChild(link);
  link.click();
  link.remove();
}

async function exportMembersWord() {
  const response = await axios.get('/members/export/word/', { responseType: 'blob' });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'members.docx');
  document.body.appendChild(link);
  link.click();
  link.remove();
}

function hideAddModal() {
  const modalEl = document.getElementById('addMemberModal');
  const modalInstance = bootstrap.Modal.getInstance(modalEl);
  if (modalInstance) modalInstance.hide();
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
}

function hideEditModal() {
  const modalEl = document.getElementById('editMemberModal');
  const modalInstance = bootstrap.Modal.getInstance(modalEl);
  if (modalInstance) modalInstance.hide();
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
}

function hideDeleteModal() {
  const modalEl = document.getElementById('deleteMemberModal');
  const modalInstance = bootstrap.Modal.getInstance(modalEl);
  if (modalInstance) modalInstance.hide();
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
}
</script>

<style scoped>
.stats-line {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  font-size: 0.9em;
}

.stats-left {
  display: flex;
  gap: 12px;
}

.stats-right {
  display: flex;
  gap: 6px;
}

.stat {
  background: #fafafa;
  border: 1px solid #ddd;
  padding: 4px 10px;
  border-radius: 6px;
  color: #333;
}

.list-group-item.selected {
  background-color: #d1e7dd;
  border-color: #0f5132;
  color: #0f5132;
}
</style>