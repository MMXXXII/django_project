<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const otpCode = ref('')
const showOtpInput = ref(false)
const userEmail = ref('')

// Таймер OTP
const otpTimer = ref(300) // 5 минут
let timerInterval = null

const formattedOtpTime = computed(() => {
  const m = Math.floor(otpTimer.value / 60).toString().padStart(2, '0')
  const s = (otpTimer.value % 60).toString().padStart(2, '0')
  return `${m}:${s}`
})

function startOtpTimer() {
  otpTimer.value = 300
  timerInterval = setInterval(() => {
    otpTimer.value--
    if (otpTimer.value <= 0) {
      clearInterval(timerInterval)
      timerInterval = null
      showOtpInput.value = false
      otpCode.value = ''
      userStore.error = 'Время ввода OTP истекло'
    }
  }, 1000)
}

function stopOtpTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

async function handleLogin() {
  try {
    const result = await userStore.login(username.value, password.value)
    userEmail.value = result.email
    showOtpInput.value = true
    userStore.error = null
    stopOtpTimer()
    startOtpTimer()
  } catch (err) {
    console.error('Ошибка при входе:', err)
  }
}

async function handleOtpSubmit() {
  try {
    const success = await userStore.verifyOtp(otpCode.value)
    if (success) {
      stopOtpTimer()
      username.value = ''
      password.value = ''
      otpCode.value = ''
      showOtpInput.value = false
      router.push('/books')
    }
  } catch (err) {
    console.error('Ошибка при проверке OTP:', err)
  }
}

function handleBack() {
  stopOtpTimer()
  showOtpInput.value = false
  otpCode.value = ''
  username.value = ''
  password.value = ''
  userStore.error = null
}
</script>

<template>
  <div class="login-container">
    <!-- Приветствие и GIF выше формы -->
    <div class="welcome-container">
      <img
        src="https://i.pinimg.com/originals/39/70/fd/3970fd45f8264338153834f7ff18f4f0.gif"
        alt="Приветствие"
        class="welcome-gif mb-4"
      />
      <h2>Добро пожаловать! Пожалуйста, войдите в систему.</h2>
    </div>

    <!-- Первый этап: логин и пароль -->
    <form v-if="!showOtpInput" @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">Имя пользователя:</label>
        <input 
          type="text" 
          v-model="username" 
          id="username" 
          required 
          placeholder="Введите имя пользователя"
        />
      </div>
      <div class="form-group">
        <label for="password">Пароль:</label>
        <input 
          type="password" 
          v-model="password" 
          id="password" 
          required 
          placeholder="Введите пароль"
        />
      </div>
      <button type="submit" :disabled="userStore.loading">
        {{ userStore.loading ? 'Загрузка...' : 'Далее' }}
      </button>
    </form>

    <!-- Второй этап: OTP код -->
    <form v-else @submit.prevent="handleOtpSubmit">
      <div class="otp-info">
        <p class="info-title">Введите код подтверждения</p>
        <p class="info-text">
          Осталось времени: <strong>{{ formattedOtpTime }}</strong>
        </p>
      </div>
      
      <div class="form-group">
        <label for="otp">Код подтверждения:</label>
        <input 
          type="text" 
          v-model="otpCode" 
          id="otp" 
          required 
          placeholder="000000"
          maxlength="6"
          inputmode="numeric"
        />
      </div>

      <button type="submit" :disabled="userStore.loading || otpCode.length !== 6">
        {{ userStore.loading ? 'Проверка...' : 'Подтвердить' }}
      </button>
      <button type="button" @click="handleBack" class="back-btn" :disabled="userStore.loading">
        Назад
      </button>
    </form>

    <!-- Сообщение об ошибке -->
    <div v-if="userStore.error" class="error-message">
      {{ userStore.error }}
    </div>
  </div>
</template>


<style scoped>
.login-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #fff;
  box-sizing: border-box;
}

.welcome-container {
  text-align: center;
  margin-bottom: 20px;
}

.welcome-gif {
  width: 100%;
  max-height: 250px;
  object-fit: cover; 
  margin-bottom: 20px; 
}

h2 {
  font-size: 1.5em;
  color: #333;
  font-weight: bold;
  margin-top: 0; 
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-bottom: 10px;
}

button:hover:not(:disabled) {
  background-color: #0056b3;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.back-btn {
  background-color: #6c757d;
}

.back-btn:hover:not(:disabled) {
  background-color: #5a6268;
}

.error-message {
  color: red;
  margin-top: 10px;
  padding: 10px;
  background-color: #ffe6e6;
  border-radius: 4px;
}

.otp-info {
  background-color: #f0f8ff;
  border-left: 4px solid #007bff;
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 4px;
}

.info-title {
  margin: 0 0 10px 0;
  font-weight: bold;
  color: #0056b3;
}

.info-text {
  margin: 5px 0 0 0;
  color: #666;
  font-size: 14px;
}

</style>
