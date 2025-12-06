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
    try {
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
    } catch {
    }
    return false
  }

  async function login(usernameParam, passwordParam) {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post('/userprofile/login/', {
        username: usernameParam,
        password: passwordParam,
      })

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
    } catch (err) {
      error.value = err.response?.data?.error || err.message || 'Ошибка авторизации'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function verifyOtp(otpKey) {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post('/userprofile/otp-login/', {
        key: otpKey,
        username: pendingUsername.value,
      })

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
    } catch (err) {
      error.value = err.response?.data?.error || 'Ошибка проверки OTP'
      isOtpVerified.value = false
      throw err
    } finally {
      loading.value = false
    }
  }

  async function checkOtpStatus() {
    try {
      const response = await axios.get('/userprofile/otp-status/')
      isOtpVerified.value = response.data.otp_good
      return isOtpVerified.value
    } catch {
      isOtpVerified.value = false
      return false
    }
  }

  async function getUserInfo() {
    try {
      const response = await axios.get('/userprofile/info/')
      user.value = response.data
      isAuthenticated.value = true
      isSuperUser.value = user.value.is_superuser
      return user.value
    } catch (err) {
      user.value = null
      isAuthenticated.value = false
      isOtpVerified.value = false
      isSuperUser.value = false
      throw err
    }
  }

  async function logout() {
    loading.value = true
    try {
      if (isAuthenticated.value) {
        await axios.post('/userprofile/logout/')
      }
    } catch {
    } finally {
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
