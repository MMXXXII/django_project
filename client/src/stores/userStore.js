import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const isOtpVerified = ref(false)
  const isSuperUser = ref(false)
  const loading = ref(false)
  const error = ref(null)
  const pendingUsername = ref(null)

  function initializeFromStorage() {
    const savedUser = localStorage.getItem('user_data')
    const savedAuth = localStorage.getItem('is_authenticated')
    const savedOtp = localStorage.getItem('is_otp_verified')
    const savedSuperUser = localStorage.getItem('is_superuser')

    if (savedUser) {
      user.value = JSON.parse(savedUser)
      isAuthenticated.value = savedAuth === 'true'
      isOtpVerified.value = savedOtp === 'true'
      isSuperUser.value = savedSuperUser === 'true'
      return isAuthenticated.value && isOtpVerified.value
    }
    return false
  }

  async function login(usernameParam, passwordParam) {
    loading.value = true
    error.value = null

    const response = await axios.post('/userprofile/login/', {
      username: usernameParam,
      password: passwordParam,
    })

    loading.value = false

    if (response.data.is_authenticated === false && response.data.otp_sent) {
      user.value = {
        username: response.data.username,
        email: response.data.email,
        is_superuser: response.data.is_superuser || false,
      }
      pendingUsername.value = usernameParam
      isAuthenticated.value = false
      isOtpVerified.value = false
      isSuperUser.value = user.value.is_superuser

      localStorage.setItem('user_data', JSON.stringify(user.value))
      localStorage.setItem('is_authenticated', 'false')
      localStorage.setItem('is_otp_verified', 'false')
      localStorage.setItem('is_superuser', isSuperUser.value.toString())

      return response.data
    } else {
      error.value = response.data.error || 'Ошибка авторизации'
      throw new Error(error.value)
    }
  }

  async function verifyOtp(otpKey) {
    loading.value = true
    error.value = null

    const response = await axios.post('/userprofile/otp-login/', {
      key: otpKey,
      username: pendingUsername.value,
    })

    loading.value = false

    if (response.data.success && response.data.is_authenticated) {
      isAuthenticated.value = true
      isOtpVerified.value = true
      error.value = null
      pendingUsername.value = null

      localStorage.setItem('user_data', JSON.stringify(user.value))
      localStorage.setItem('is_authenticated', 'true')
      localStorage.setItem('is_otp_verified', 'true')
      localStorage.setItem('is_superuser', isSuperUser.value.toString())

      return true
    } else {
      error.value = response.data.error || 'Неверный OTP код'
      isOtpVerified.value = false
      return false
    }
  }

  async function checkOtpStatus() {
    const response = await axios.get('/userprofile/otp-status/')
    isOtpVerified.value = response.data.otp_good
    return isOtpVerified.value
  }

  async function getUserInfo() {
    const response = await axios.get('/userprofile/info/')
    user.value = response.data
    isAuthenticated.value = true
    isSuperUser.value = user.value.is_superuser
    return user.value
  }

  async function logout() {
    loading.value = true
    
    if (isAuthenticated.value) {
      await axios.post('/userprofile/logout/')
    }
    
    user.value = null
    isAuthenticated.value = false
    isOtpVerified.value = false
    isSuperUser.value = false
    pendingUsername.value = null
    error.value = null
    loading.value = false

    localStorage.removeItem('user_data')
    localStorage.removeItem('is_authenticated')
    localStorage.removeItem('is_otp_verified')
    localStorage.removeItem('is_superuser')
  }

  return {
    user,
    isAuthenticated,
    isOtpVerified,
    isSuperUser,
    loading,
    error,
    pendingUsername,

    initializeFromStorage,
    login,
    verifyOtp,
    checkOtpStatus,
    getUserInfo,
    logout,
  }
})