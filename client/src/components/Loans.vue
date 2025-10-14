<template>
  <h2>Выдачи</h2>

  <form @submit.prevent="onAddLoan" class="mb-3">
    <div class="row g-2 align-items-center">
      <div class="col">
        <select v-model="loanToAdd.book" class="form-select" required>
          <option v-for="b in books" :value="b.id" :key="b.id">{{ b.title }}</option>
        </select>
      </div>
      <div class="col">
        <select v-model="loanToAdd.member" class="form-select" required>
          <option v-for="m in members" :value="m.id" :key="m.id">{{ m.first_name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <input type="date" v-model="loanToAdd.loan_date" class="form-control" required />
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить выдачу</button>
      </div>
    </div>
  </form>

  <ul class="list-group">
    <li v-for="l in loans" :key="l.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>
        <div><strong>{{ booksById[l.book]?.title }}</strong> → {{ membersById[l.member]?.first_name }}</div>
        <div class="small text-muted">{{ l.loan_date }}</div>
      </div>
      <div>
        <button class="btn btn-sm btn-danger" @click="onRemove(l)"><i class="bi bi-x"></i></button>
      </div>
    </li>
  </ul>
</template>

<script setup>
import { ref, onBeforeMount, computed } from 'vue'
import axios from 'axios'
import { onMounted } from 'vue'

const loans = ref([])
const books = ref([])
const members = ref([])
const loanToAdd = ref({ book: null, member: null, loan_date: '' })
const isLoading = ref(true)

const booksById = computed(() => Object.fromEntries(books.value.map(b => [b.id, b])))
const membersById = computed(() => Object.fromEntries(members.value.map(m => [m.id, m])))

async function fetchLoans() { loans.value = (await axios.get('/loans/')).data }
async function fetchBooks() { books.value = (await axios.get('/books/')).data }
async function fetchMembers() { members.value = (await axios.get('/members/')).data }

async function onAddLoan() {
  await axios.post('/loans/', { ...loanToAdd.value })
  loanToAdd.value = { book: null, member: null, loan_date: '' }
  await fetchLoans()
}

async function onRemove(l) {
  if (!confirm('Удалить выдачу?')) return
  await axios.delete(`/loans/${l.id}/`)
  await fetchLoans()
}

onMounted(async () => {
  try {
    await Promise.all([
      fetchLoans(),
      fetchBooks(),
      fetchMembers()
    ]);
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error)
  }
});
</script>
