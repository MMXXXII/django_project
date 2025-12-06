<template>
  <v-app>
    <div class="container py-4">
      <nav
        v-if="!$route.meta.hideHeader"
        class="mb-4 d-flex justify-content-between align-items-center"
      >
        <div>
          <router-link
            v-if="userStore.isAuthenticated"
            class="btn btn-light me-2"
            to="/genres"
          >Жанры</router-link>
          <router-link
            v-if="userStore.isAuthenticated"
            class="btn btn-light me-2"
            to="/libraries"
          >Библиотеки</router-link>
          <router-link
            v-if="userStore.isAuthenticated"
            class="btn btn-light me-2"
            to="/books"
          >Книги</router-link>
          <router-link
            v-if="userStore.isAuthenticated && userStore.isSuperUser"
            class="btn btn-light me-2"
            to="/members"
          >Читатели</router-link>
          <router-link
            v-if="userStore.isAuthenticated"
            class="btn btn-light me-2"
            to="/loans"
          >Выдачи</router-link>
        </div>

        <div
          class="d-flex align-items-center gap-2"
          v-if="userStore.isAuthenticated"
        >
          <div class="dropdown" ref="dropdownWrapper">
            <button
              class="btn btn-light dropdown-toggle"
              type="button"
              @click="toggleDropdown"
            >
              {{ userStore.user?.username || 'Профиль' }}
            </button>
            <ul
              v-if="isOpen"
              class="dropdown-menu dropdown-menu-end show"
            >
              <li>
                <router-link class="dropdown-item" to="/profile">
                  Мой профиль
                </router-link>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <button
                  class="dropdown-item text-danger"
                  @click="handleLogout"
                >
                  Выход
                </button>
              </li>
            </ul>
          </div>
          <a
            class="btn btn-light d-flex align-items-center"
            href="/admin"
            target="_blank"
          >
            Админка
          </a>
        </div>
      </nav>

      <router-view />
    </div>
  </v-app>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/userStore'

const userStore = useUserStore()
const router = useRouter()
const isOpen = ref(false)
const dropdownWrapper = ref(null)

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const handleClickOutside = (e) => {
  if (dropdownWrapper.value && !dropdownWrapper.value.contains(e.target)) {
    isOpen.value = false
  }
}

const handleLogout = async () => {
  await userStore.logout()
  router.push('/login')
}

onMounted(() => {
  userStore.initializeFromStorage()
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.btn {
  border: none;
  box-shadow: none;
  transition: all 0.2s ease-in-out;
  outline: none;
}
.btn-light {
  background-color: #f8f9fa;
  color: #212529;
}
.btn-light:hover {
  background-color: #e2e6ea;
  color: #212529;
}
.dropdown-item {
  border: none;
}
.dropdown-item:focus,
.dropdown-item:hover {
  background-color: #f1f1f1;
  outline: none;
}
.dropdown-menu {
  margin-top: 0.25rem;
}
</style>
