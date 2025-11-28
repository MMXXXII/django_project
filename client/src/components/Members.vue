<template>
  <div>
    <h2>Читатели</h2>
    <!-- Статистика + кнопки -->
    <div class="stats-line">
      <div class="stats-left">
        <div class="stat">Читателей: {{ memberStats?.count || 0 }}</div>
        <div class="stat">Средний возраст: {{ memberStats?.avg_age || 0 }} лет</div>
        <div class="stat">Среднее книг: {{ memberStats?.avg_books || 0 }}</div>
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
      <button class="btn btn-outline-success" @click="showAddModal" style="white-space: nowrap;">Добавить читателя</button>
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
    <!-- Модалка добавления нового пользователя -->
    <div class="modal fade" id="addMemberModal" tabindex="-1" aria-labelledby="addMemberModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="addMemberModalLabel">Добавление нового читателя</h5>
            <button type="button" class="btn-close" @click="hideAddModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label for="addUsername" class="form-label">Имя пользователя</label>
              <input v-model="memberToAdd.username" class="form-control" id="addUsername" placeholder="Имя пользователя" />
            </div>
            <div class="mb-3">
              <label for="addEmail" class="form-label">Электронная почта</label>
              <input v-model="memberToAdd.email" class="form-control" id="addEmail" placeholder="Электронная почта" />
            </div>
            <div class="mb-3">
              <label for="addAge" class="form-label">Возраст</label>
              <input type="number" v-model="memberToAdd.age" class="form-control" id="addAge" placeholder="Возраст" />
            </div>
            <div class="mb-3">
              <label for="addPassword" class="form-label">Пароль</label>
              <input type="password" v-model="memberToAdd.password" class="form-control" id="addPassword" placeholder="Пароль" />
            </div>
            <div class="mb-3">
              <label for="addIsSuperUser" class="form-check-label">Администратор</label>
              <input type="checkbox" v-model="memberToAdd.is_superuser" class="form-check-input" id="addIsSuperUser" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideAddModal">Отмена</button>
            <button type="button" class="btn btn-success" @click="onAddMember">Добавить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка редактирования -->
    <div class="modal fade" id="editMemberModal" tabindex="-1" aria-labelledby="editMemberModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editMemberModalLabel">Редактирование читателя</h5>
            <button type="button" class="btn-close" @click="hideEditModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label for="username" class="form-label">Имя пользователя</label>
              <input v-model="memberToEdit.username" class="form-control" id="username" placeholder="Имя пользователя" />
            </div>
            <div class="mb-3">
              <label for="email" class="form-label">Электронная почта</label>
              <input v-model="memberToEdit.email" class="form-control" id="email" placeholder="Электронная почта" />
            </div>
            <div class="mb-3">
              <label for="age" class="form-label">Возраст</label>
              <input type="number" v-model="memberToEdit.age" class="form-control" id="age" placeholder="Возраст" />
            </div>
            <div class="mb-3">
              <label for="password" class="form-label">Новый пароль</label>
              <input type="password" v-model="memberToEdit.password" class="form-control" id="password" placeholder="Новый пароль" />
            </div>
            <div class="mb-3">
              <label for="isSuperUser" class="form-check-label">Администратор</label>
              <input type="checkbox" v-model="memberToEdit.is_superuser" class="form-check-input" id="isSuperUser" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideEditModal">Отмена</button>
            <button type="button" class="btn btn-success" @click="onUpdateMember">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка удаления -->
    <div class="modal fade" id="deleteMemberModal" tabindex="-1" aria-labelledby="deleteMemberModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="deleteMemberModalLabel">Удаление читателя</h5>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import * as bootstrap from 'bootstrap'

const members = ref([])
const filteredMembers = ref([])
const memberStats = ref([])
const searchQuery = ref('')
const sortOrder = ref('asc')
const selectedMembers = ref([])
const memberToAdd = reactive({ username: '', email: '', password: '', age: null, is_superuser: false, is_staff: false })
const memberToEdit = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  age: null,
  is_superuser: false,
  is_staff: false,
})
const memberToDelete = reactive({ id: null, username: '' })

onMounted(() => {
  searchQuery.value = '';
  fetchMembers();
  fetchMemberStats();
})

async function fetchMembers() {
  try {
    const response = await axios.get('/members/');
    members.value = response.data;
    filterMembers();
  } catch (error) {
    console.error('Error fetching members:', error);
  }
}

function filterMembers() {
  filteredMembers.value = members.value.filter(m => m.username.toLowerCase().includes(searchQuery.value.toLowerCase()));
  sortMembers();
}

function sortMembers() {
  filteredMembers.value.sort((a, b) => {
    if (sortOrder.value === 'admin_first') {
      // Сначала администраторы, потом пользователи
      if (a.is_superuser && !b.is_superuser) return -1;
      if (!a.is_superuser && b.is_superuser) return 1;
      // Если роли одинаковые, сортируем по имени
      return a.username.toLowerCase().localeCompare(b.username.toLowerCase());
    } else if (sortOrder.value === 'user_first') {
      // Сначала пользователи, потом администраторы
      if (!a.is_superuser && b.is_superuser) return -1;
      if (a.is_superuser && !b.is_superuser) return 1;
      // Если роли одинаковые, сортируем по имени
      return a.username.toLowerCase().localeCompare(b.username.toLowerCase());
    } else {
      // Обычная сортировка по алфавиту
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

async function onUpdateMember() {
  try {
    const formData = new FormData();
    formData.append('username', memberToEdit.username);
    formData.append('email', memberToEdit.email);
    if (memberToEdit.age) formData.append('age', memberToEdit.age);
    if (memberToEdit.password) formData.append('password', memberToEdit.password);
    formData.append('is_superuser', memberToEdit.is_superuser);
    formData.append('is_staff', memberToEdit.is_staff);

    await axios.put(`/members/${memberToEdit.id}/`, formData);
    await fetchMembers();
    await fetchMemberStats();
    hideEditModal();
  } catch (error) {
    console.error('Error updating member:', error);
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
  try {
    const formData = new FormData();
    formData.append('username', memberToAdd.username);
    formData.append('email', memberToAdd.email);
    formData.append('password', memberToAdd.password);
    if (memberToAdd.age) formData.append('age', memberToAdd.age);
    formData.append('is_superuser', memberToAdd.is_superuser);
    formData.append('is_staff', memberToAdd.is_staff);

    const response = await axios.post('/members/', formData);
    console.log('Success:', response.data);
    await fetchMembers();
    await fetchMemberStats();
    hideAddModal();
  } catch (error) {
    console.error('Error adding member:', error);
    console.error('Error response:', error.response?.data);
    console.error('Error status:', error.response?.status);
    
    // Показываем понятное сообщение пользователю
    if (error.response?.data?.error) {
      alert(`Ошибка: ${error.response.data.error}`);
    } else if (error.response?.data) {
      alert(`Ошибка: ${JSON.stringify(error.response.data)}`);
    } else {
      alert('Ошибка при добавлении пользователя');
    }
  }
}

function onRemoveClick(m) {
  memberToDelete.id = m.id;
  memberToDelete.username = m.username;
  const modalEl = document.getElementById('deleteMemberModal');
  const modalInstance = new bootstrap.Modal(modalEl);
  modalInstance.show();
}

async function confirmDelete() {
  if (!memberToDelete.id) return;
  try {
    await axios.delete(`/members/${memberToDelete.id}/`);
    await fetchMembers();
    hideDeleteModal();
  } catch (error) {
    console.error('Error deleting member:', error);
  }
}

function toggleSelection(id) {
  if (selectedMembers.value.includes(id)) {
    selectedMembers.value = selectedMembers.value.filter(x => x !== id);
  } else {
    selectedMembers.value.push(id);
  }
}

async function confirmDeleteSelected() {
  if (!selectedMembers.value.length) return;
  await Promise.all(selectedMembers.value.map(id => axios.delete(`/members/${id}/`)));
  selectedMembers.value = [];
  await fetchMembers();
}

async function fetchMemberStats() {
  try {
    const response = await axios.get('/members/stats/');
    memberStats.value = response.data;
    console.log('Stats loaded:', response.data);
  } catch (error) {
    console.error('Error fetching member stats:', error);
    console.error('Error response:', error.response?.data);
    // Устанавливаем значения по умолчанию при ошибке
    memberStats.value = {
      count: 0,
      avg_age: 0,
      avg_books: 0
    };
  }
}

async function exportMembersExcel() {
  try {
    const response = await axios.get('/members/export/excel/', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'members.xlsx');
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error('Error exporting to Excel:', error);
  }
}

async function exportMembersWord() {
  try {
    const response = await axios.get('/members/export/word/', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'members.docx');
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error('Error exporting to Word:', error);
  }
}

function hideAddModal() {
  const modalEl = document.getElementById('addMemberModal');
  const modalInstance = bootstrap.Modal.getInstance(modalEl);
  if (modalInstance) {
    modalInstance.hide();
  }
  // Убираем фокус с элементов внутри модального окна
  document.activeElement?.blur();
  // Очищаем backdrop
  setTimeout(() => {
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('overflow');
    document.body.style.removeProperty('padding-right');
  }, 200);
}

function hideEditModal() {
  const modalEl = document.getElementById('editMemberModal');
  const modalInstance = bootstrap.Modal.getInstance(modalEl);
  if (modalInstance) {
    modalInstance.hide();
  }
  // Убираем фокус с элементов внутри модального окна
  document.activeElement?.blur();
  // Очищаем backdrop
  setTimeout(() => {
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('overflow');
    document.body.style.removeProperty('padding-right');
  }, 200);
}

function hideDeleteModal() {
  const modalEl = document.getElementById('deleteMemberModal');
  const modalInstance = bootstrap.Modal.getInstance(modalEl);
  if (modalInstance) {
    modalInstance.hide();
  }
  // Убираем фокус с элементов внутри модального окна
  document.activeElement?.blur();
  // Очищаем backdrop
  setTimeout(() => {
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('overflow');
    document.body.style.removeProperty('padding-right');
  }, 200);
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

.img-thumbnail {
  border-radius: 4px;
  cursor: pointer;
}

.list-group-item.selected {
  background-color: #d1e7dd;
  border-color: #0f5132;
  color: #0f5132;
}

.form-control {
  width: 100%;
  padding: 8px;
}
</style>