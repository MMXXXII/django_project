<template>
  <h2>Читатели</h2>

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
import { ref, onBeforeMount, computed } from 'vue'
import axios from 'axios'
import { onMounted } from 'vue'


const members = ref([])
const libraries = ref([])
const memberToAdd = ref({ first_name: '', library: null })
const memberToEdit = ref({ id: null, first_name: '', library: null })
const isLoading = ref(true)  // Флаг для отображения загрузки

const librariesById = computed(() => Object.fromEntries(libraries.value.map(l => [l.id, l])))

async function fetchMembers() {
  try {
    const res = await axios.get('/members/')
    members.value = res.data
  } catch (error) {
    console.error('Ошибка при получении читателей:', error)
  } finally {
    isLoading.value = false // После загрузки данных, меняем флаг
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

async function onAddMember() {
  await axios.post('/members/', { ...memberToAdd.value })
  memberToAdd.value = { first_name: '', library: null }
  await fetchMembers() // Обновляем читателей после добавления
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
  await fetchMembers() // Обновляем читателей после редактирования
}

onMounted(async () => {
  await Promise.all([fetchMembers(), fetchLibraries()])
})
</script>


