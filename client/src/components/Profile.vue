<template>
  <div class="profile-container">
    <h2>Профиль пользователя</h2>
    
    <div v-if="userStore.loading" class="loading">Загрузка...</div>
    
    <div v-else-if="userStore.user" class="user-info">
      <p><strong>Имя пользователя:</strong> {{ userStore.user.username }}</p>
      <p><strong>Email:</strong> {{ userStore.user.email }}</p>
      <button @click="handleLogout" class="logout-btn">Выход</button>
    </div>
    
    <div v-else-if="userStore.error" class="error-message">
      {{ userStore.error }}
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const userStore = useUserStore()

onMounted(async () => {
  try {
    if (!userStore.isAuthenticated) {
      router.push('/login')
    }
  } catch (err) {
    console.error('Ошибка при загрузке профиля:', err)
    router.push('/login')
  }
})

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-container {
  max-width: 600px;
  margin: 30px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.user-info {
  margin: 20px 0;
}

.user-info p {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.logout-btn {
  width: 100%;
  padding: 10px 20px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 20px;
}

.logout-btn:hover {
  background-color: #c82333;
}

.loading {
  text-align: center;
  padding: 20px;
}

.error-message {
  color: red;
  margin-top: 10px;
}
</style>
