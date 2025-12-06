<script setup>
import { ref, reactive, onMounted, computed, shallowRef } from 'vue'
import axios from 'axios'
import { showNotification, handleApiError } from '../utils'

// данные
const loans = shallowRef([])
const filteredLoans = shallowRef([])
const loanStats = ref(null)
const user = ref(null)
const books = shallowRef([])
const libraries = shallowRef([])
const members = shallowRef([])
const currentMember = ref(null)

// пагинация
const page = ref(1)
const itemsPerPage = ref(20)

// состояние
const searchQuery = ref('')
const sortOrder = ref('asc')

const isAdmin = computed(() => !!user.value?.is_superuser)

const notification = reactive({
  visible: false,
  message: '',
  type: 'success',
  _timeoutId: null,
})

const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)

const loanToAdd = reactive({
  library: null,
  book: null,
  loan_date: '',
})

const loanToEdit = reactive({
  id: null,
  library: null,
  book: null,
  member: null,
  loan_date: '',
})

const loanToDelete = reactive({
  id: null,
  bookTitle: '',
  memberName: '',
})

// кэширование для быстрого доступа
const booksMap = computed(() => {
  const map = new Map()
  books.value.forEach(b => map.set(b.id, b))
  return map
})

const membersMap = computed(() => {
  const map = new Map()
  members.value.forEach(m => map.set(m.id, m))
  return map
})

const librariesMap = computed(() => {
  const map = new Map()
  libraries.value.forEach(l => map.set(l.id, l))
  return map
})

// доступные книги с мемоизацией
const availableBooks = computed(() => {
  const libId = loanToAdd.library ? Number(loanToAdd.library) : null
  return books.value.filter(b => {
    if (libId && b.library !== libId) return false
    return b.is_available === true
  })
})

const availableEditBooks = computed(() => {
  const libId = loanToEdit.library ? Number(loanToEdit.library) : null
  return books.value.filter(b => {
    if (libId && b.library !== libId) return false
    return b.is_available === true
  })
})

// пагинированные данные
const paginatedLoans = computed(() => {
  const start = (page.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredLoans.value.slice(start, end)
})

const totalPages = computed(() => Math.ceil(filteredLoans.value.length / itemsPerPage.value))

// вспомогательные функции с кэшем
function getMemberName(memberId) {
  const member = membersMap.value.get(memberId)
  if (member) return member.first_name || member.username
  if (currentMember.value?.id === memberId) {
    return currentMember.value.first_name || currentMember.value.username
  }
  return 'Неизвестно'
}

function getLibraryName(bookId) {
  const book = booksMap.value.get(bookId)
  if (!book) return ''
  const library = librariesMap.value.get(book.library)
  return library?.name || ''
}

function getBookTitle(bookId) {
  return booksMap.value.get(bookId)?.title || ''
}

// загрузка данных
async function loadUser() {
  try {
    const r = await axios.get('/userprofile/info/')
    user.value = r.data
  } catch (err) {
    handleApiError(
      err,
      'Не удалось получить информацию о пользователе',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

async function loadCurrentMember() {
  try {
    const response = await axios.get('/library-members/')
    if (response.data && response.data.length > 0) {
      if (isAdmin.value) {
        members.value = response.data
      } else {
        currentMember.value = response.data[0]
        members.value = response.data
      }
    }
  } catch (err) {
    handleApiError(
      err,
      'Не удалось загрузить читателей',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

async function loadLibraries() {
  try {
    const r = await axios.get('/libraries/')
    libraries.value = r.data
  } catch (err) {
    handleApiError(
      err,
      'Не удалось загрузить библиотеки',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

async function loadBooks() {
  try {
    const r = await axios.get('/books/')
    books.value = r.data
  } catch (err) {
    handleApiError(
      err,
      'Не удалось загрузить книги',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

async function loadLoans() {
  try {
    const r = await axios.get('/loans/')
    loans.value = r.data
    applyFilter()
  } catch (err) {
    handleApiError(
      err,
      'Не удалось загрузить список выдач',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

async function loadLoanStats() {
  try {
    const r = await axios.get('/loans/stats/')
    loanStats.value = r.data
  } catch (err) {
    handleApiError(
      err,
      'Не удалось загрузить статистику',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

// оптимизированная фильтрация и сортировка
let filterTimeout = null
function applyFilter() {
  clearTimeout(filterTimeout)
  filterTimeout = setTimeout(() => {
    const q = searchQuery.value.trim().toLowerCase()
    let list = loans.value

    if (q) {
      list = list.filter((l) => {
        const book = booksMap.value.get(l.book)
        const bookTitle = book?.title?.toLowerCase() || ''
        const member = membersMap.value.get(l.member)
        const memberName = (member?.first_name || member?.username || '').toLowerCase()
        return bookTitle.includes(q) || memberName.includes(q)
      })
    }

    // сортировка
    list = [...list].sort((a, b) => {
      const bookA = booksMap.value.get(a.book)?.title?.toLowerCase() || ''
      const bookB = booksMap.value.get(b.book)?.title?.toLowerCase() || ''
      return sortOrder.value === 'asc' 
        ? bookA.localeCompare(bookB) 
        : bookB.localeCompare(bookA)
    })

    filteredLoans.value = list
    page.value = 1
  }, 300)
}

function onLibraryChange() {
  loanToAdd.book = null
}

function onEditLibraryChange() {
  loanToEdit.book = null
}

async function addLoan() {
  if (!loanToAdd.book || !loanToAdd.loan_date) {
    showNotification(notification, 'Заполните все поля', 'warning')
    return
  }

  if (!currentMember.value || !currentMember.value.id) {
    showNotification(notification, 'У вас нет профиля читателя', 'warning')
    return
  }

  try {
    await axios.post('/loans/', {
      book: loanToAdd.book,
      member: currentMember.value.id,
      loan_date: loanToAdd.loan_date,
    })

    loanToAdd.library = null
    loanToAdd.book = null
    loanToAdd.loan_date = ''
    showAddDialog.value = false

    await Promise.all([loadBooks(), loadLoans(), loadLoanStats()])
    showNotification(notification, 'Выдача добавлена', 'success')
  } catch (err) {
    handleApiError(
      err,
      'Ошибка при добавлении выдачи',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

function openEditDialog(loan) {
  if (!isAdmin.value) return
  const book = booksMap.value.get(loan.book)
  loanToEdit.id = loan.id
  loanToEdit.library = book?.library || null
  loanToEdit.book = loan.book
  loanToEdit.member = loan.member
  loanToEdit.loan_date = loan.loan_date
  showEditDialog.value = true
}

async function updateLoan() {
  if (!isAdmin.value || !loanToEdit.id) return

  try {
    await axios.put(`/loans/${loanToEdit.id}/`, {
      book: loanToEdit.book,
      member: loanToEdit.member,
      loan_date: loanToEdit.loan_date,
    })

    showEditDialog.value = false
    await Promise.all([loadBooks(), loadLoans(), loadLoanStats()])
    showNotification(notification, 'Изменения сохранены', 'warning')
  } catch (err) {
    handleApiError(
      err,
      'Ошибка при обновлении выдачи',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

function openDeleteDialog(loan) {
  if (!isAdmin.value) return
  loanToDelete.id = loan.id
  loanToDelete.bookTitle = getBookTitle(loan.book)
  loanToDelete.memberName = getMemberName(loan.member)
  showDeleteDialog.value = true
}

async function deleteLoan() {
  if (!isAdmin.value || !loanToDelete.id) return

  try {
    await axios.delete(`/loans/${loanToDelete.id}/`)
    showDeleteDialog.value = false
    await Promise.all([loadBooks(), loadLoans(), loadLoanStats()])
    showNotification(notification, 'Выдача удалена', 'danger')
  } catch (err) {
    handleApiError(
      err,
      'Ошибка при удалении выдачи',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

async function returnBook(loan) {
  try {
    await axios.post(`/loans/${loan.id}/return/`)
    await Promise.all([loadBooks(), loadLoans(), loadLoanStats()])
    showNotification(notification, 'Книга возвращена', 'success')
  } catch (err) {
    handleApiError(
      err,
      'Ошибка при возврате книги',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

async function exportLoans(type = 'excel') {
  if (!isAdmin.value) return

  try {
    const response = await axios.get('/loans/export/', {
      params: { type },
      responseType: 'blob',
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', type === 'excel' ? 'loans.xlsx' : 'loans.docx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    showNotification(notification, 'Файл скачивается', 'success')
  } catch (err) {
    handleApiError(
      err,
      'Ошибка при экспорте',
      (msg, type = 'danger') => showNotification(notification, msg, type),
    )
  }
}

onMounted(async () => {
  await loadUser()
  await Promise.all([
    loadLibraries(),
    loadBooks(),
    loadCurrentMember(),
  ])
  await loadLoans()
  await loadLoanStats()
})
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card class="pa-4" elevation="2">
          <div class="d-flex justify-space-between align-center mb-4">
            <div>
              <h2 class="mb-1">Выдачи</h2>
              <div class="text-body-2 text-medium-emphasis">
                Количество: {{ loanStats?.count || 0 }},
                читатель с максимальным количеством книг: {{ loanStats?.topReader?.name || 'не найден' }}
              </div>
            </div>

            <div class="d-flex gap-2" v-if="isAdmin">
              <v-btn
                color="success"
                variant="outlined"
                prepend-icon="mdi-microsoft-excel"
                @click="exportLoans('excel')"
              >
                Excel
              </v-btn>
              <v-btn
                color="indigo"
                variant="outlined"
                prepend-icon="mdi-file-word"
                @click="exportLoans('word')"
              >
                Word
              </v-btn>
            </div>
          </div>

          <v-alert
            v-if="notification.visible"
            :type="notification.type"
            class="mb-4"
            variant="tonal"
            closable
          >
            {{ notification.message }}
          </v-alert>

          <v-row class="mb-4" align="center">
            <v-col cols="12" md="6">
              <v-text-field
                v-model="searchQuery"
                label="Поиск по выдачам"
                variant="outlined"
                density="comfortable"
                clearable
                prepend-inner-icon="mdi-magnify"
                @input="applyFilter"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="sortOrder"
                :items="[
                  { title: 'От A до Я', value: 'asc' },
                  { title: 'От Я до A', value: 'desc' },
                ]"
                item-title="title"
                item-value="value"
                label="Сортировка"
                variant="outlined"
                density="comfortable"
                @update:model-value="applyFilter"
              />
            </v-col>
          </v-row>

          <v-row v-if="!isAdmin" class="mb-4" align="end">
            <v-col cols="4">
              <v-select
                v-model="loanToAdd.library"
                :items="libraries"
                item-value="id"
                item-title="name"
                label="Библиотека"
                variant="outlined"
                density="comfortable"
                hide-details
                @update:model-value="onLibraryChange"
              />
            </v-col>
            <v-col cols="4">
              <v-select
                v-model="loanToAdd.book"
                :items="availableBooks"
                item-value="id"
                item-title="title"
                label="Книга"
                variant="outlined"
                density="comfortable"
                hide-details
              />
            </v-col>
            <v-col cols="2">
              <v-text-field
                v-model="loanToAdd.loan_date"
                type="date"
                label="Дата выдачи"
                variant="outlined"
                density="comfortable"
                hide-details
              />
            </v-col>
            <v-col cols="2">
              <v-btn
                color="primary"
                block
                size="large"
                prepend-icon="mdi-plus"
                @click="addLoan"
              >
                Добавить
              </v-btn>
            </v-col>
          </v-row>

          <v-list lines="two">
            <v-list-item
              v-for="loan in paginatedLoans"
              :key="loan.id"
            >
              <template #default>
                <div>
                  <div class="font-weight-medium">
                    {{ getBookTitle(loan.book) }} → {{ getMemberName(loan.member) }}
                    <v-chip
                      v-if="loan.return_date"
                      color="success"
                      variant="flat"
                      size="x-small"
                      class="ml-2"
                    >
                      Возвращена {{ loan.return_date }}
                    </v-chip>
                    <v-chip
                      v-else
                      color="warning"
                      variant="flat"
                      size="x-small"
                      class="ml-2"
                    >
                      Выдана
                    </v-chip>
                  </div>
                  <div class="text-body-2 text-medium-emphasis">
                    Дата выдачи: {{ loan.loan_date }}
                  </div>
                  <div class="text-body-2 text-medium-emphasis">
                    Библиотека: {{ getLibraryName(loan.book) }}
                  </div>
                </div>
              </template>

              <template #append>
                <div class="d-flex gap-2">
                  <v-btn
                    v-if="!loan.return_date"
                    size="small"
                    variant="text"
                    color="info"
                    prepend-icon="mdi-keyboard-return"
                    @click.stop="returnBook(loan)"
                  >
                    Вернуть
                  </v-btn>
                  <v-btn
                    v-if="isAdmin"
                    icon
                    size="small"
                    variant="text"
                    color="primary"
                    @click.stop="openEditDialog(loan)"
                  >
                    <v-icon icon="mdi-pencil" />
                  </v-btn>
                  <v-btn
                    v-if="isAdmin"
                    icon
                    size="small"
                    variant="text"
                    color="error"
                    @click.stop="openDeleteDialog(loan)"
                  >
                    <v-icon icon="mdi-delete" />
                  </v-btn>
                </div>
              </template>
            </v-list-item>

            <v-list-item
              v-if="!filteredLoans.length"
              title="Выдач пока нет"
              subtitle="Добавьте первую выдачу."
            />
          </v-list>

          <div v-if="totalPages > 1" class="d-flex justify-center mt-4">
            <v-pagination
              v-model="page"
              :length="totalPages"
              :total-visible="7"
            />
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-if="isAdmin" v-model="showAddDialog" max-width="520">
      <v-card>
        <v-card-title>Добавить выдачу</v-card-title>
        <v-card-text>
          <v-select
            v-model="loanToAdd.library"
            :items="libraries"
            item-value="id"
            item-title="name"
            label="Библиотека"
            variant="outlined"
            density="comfortable"
            class="mb-3"
            @update:model-value="onLibraryChange"
          />
          <v-select
            v-model="loanToAdd.book"
            :items="availableBooks"
            item-value="id"
            item-title="title"
            label="Книга"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-select
            v-model="loanToAdd.member"
            :items="members"
            item-value="id"
            item-title="first_name"
            label="Читатель"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-text-field
            v-model="loanToAdd.loan_date"
            type="date"
            label="Дата выдачи"
            variant="outlined"
            density="comfortable"
          />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="showAddDialog = false">
            Отмена
          </v-btn>
          <v-btn color="primary" @click="addLoan">
            Добавить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-if="isAdmin" v-model="showEditDialog" max-width="520">
      <v-card>
        <v-card-title>Редактировать выдачу</v-card-title>
        <v-card-text>
          <v-select
            v-model="loanToEdit.library"
            :items="libraries"
            item-value="id"
            item-title="name"
            label="Библиотека"
            variant="outlined"
            density="comfortable"
            class="mb-3"
            @update:model-value="onEditLibraryChange"
          />
          <v-select
            v-model="loanToEdit.book"
            :items="availableEditBooks"
            item-value="id"
            item-title="title"
            label="Книга"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-select
            v-model="loanToEdit.member"
            :items="members"
            item-value="id"
            item-title="first_name"
            label="Читатель"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-text-field
            v-model="loanToEdit.loan_date"
            type="date"
            label="Дата выдачи"
            variant="outlined"
            density="comfortable"
          />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="showEditDialog = false">
            Отмена
          </v-btn>
          <v-btn color="primary" @click="updateLoan">
            Сохранить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-if="isAdmin" v-model="showDeleteDialog" max-width="420">
      <v-card>
        <v-card-title class="text-h6">
          Удалить выдачу
        </v-card-title>
        <v-card-text>
          Вы уверены, что хотите удалить выдачу
          <strong>{{ loanToDelete.bookTitle }} → {{ loanToDelete.memberName }}</strong>?
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="showDeleteDialog = false">
            Отмена
          </v-btn>
          <v-btn color="error" @click="deleteLoan">
            Удалить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>