import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    isOtpVerified: false,
    isSuperUser: false,
    loading: false,
    error: null,
    pendingUsername: null
  }),

  actions: {
    initializeFromStorage() {
      try {
        const savedUser = localStorage.getItem('user_data')
        const savedAuth = localStorage.getItem('is_authenticated')
        const savedOtp = localStorage.getItem('is_otp_verified')
        const savedSuperUser = localStorage.getItem('is_superuser')

        if (savedUser) {
          this.user = JSON.parse(savedUser)
          this.isAuthenticated = savedAuth === 'true'
          this.isOtpVerified = savedOtp === 'true'
          this.isSuperUser = savedSuperUser === 'true' || false


          return this.isAuthenticated && this.isOtpVerified
        } else {
          console.log('[v0] No user data found in storage')
        }
      } catch (e) {
        console.error('[v0] Error loading from storage:', e)
      }
      return false
    },

    async login(username, password) {
      this.loading = true
      this.error = null
      try {

        const response = await axios.post('/userprofile/login/', {
          username,
          password
        })

        if (response.data.is_authenticated === false && response.data.otp_sent) {
          this.user = {
            username: response.data.username,
            email: response.data.email,
            is_superuser: response.data.is_superuser || false
          }
          this.pendingUsername = username
          this.isAuthenticated = false
          this.isOtpVerified = false
          this.isSuperUser = this.user.is_superuser

          localStorage.setItem('user_data', JSON.stringify(this.user))
          localStorage.setItem('is_authenticated', 'false')
          localStorage.setItem('is_otp_verified', 'false')
          localStorage.setItem('is_superuser', this.isSuperUser.toString())

          return response.data
        } else {
          this.error = response.data.error || 'Ошибка авторизации'
          throw new Error(this.error)
        }
      } catch (error) {       
        this.error = error.response?.data?.error || error.message || 'Ошибка авторизации'
        throw error
      } finally {
        this.loading = false
      }
    },

    async verifyOtp(otpKey) {
      this.loading = true
      this.error = null


      try {
        const response = await axios.post('/userprofile/otp-login/', {
          key: otpKey,
          username: this.pendingUsername
        })

        if (response.data.success && response.data.is_authenticated) {
          this.isAuthenticated = true
          this.isOtpVerified = true
          this.error = null
          this.pendingUsername = null

          localStorage.setItem('user_data', JSON.stringify(this.user))
          localStorage.setItem('is_authenticated', 'true')
          localStorage.setItem('is_otp_verified', 'true')
          localStorage.setItem('is_superuser', this.isSuperUser.toString())

          return true
        } else {
          this.error = response.data.error || 'Неверный OTP код'
          this.isOtpVerified = false
          return false
        }
      } catch (error) {
        this.error = error.response?.data?.error || 'Ошибка проверки OTP'
        this.isOtpVerified = false
        throw error
      } finally {
        this.loading = false
      }
    },

    async checkOtpStatus() {
      try {
        const response = await axios.get('/userprofile/otp-status/')
        this.isOtpVerified = response.data.otp_good
        return response.data.otp_good
      } catch (error) {
        this.isOtpVerified = false
        return false
      }
    },

    async getUserInfo() {
      try {
        const response = await axios.get('/userprofile/info/')
        this.user = response.data
        this.isAuthenticated = true
        this.isSuperUser = this.user.is_superuser
        return this.user
      } catch (error) {
        this.isAuthenticated = false
        this.user = null
        this.isOtpVerified = false
        this.isSuperUser = false
        throw error
      }
    },

    async logout() {
      this.loading = true
      try {
        if (this.isAuthenticated) {
          await axios.post('/userprofile/logout/')
        }
      } catch (error) {
      } finally {
        this.user = null
        this.isAuthenticated = false
        this.isOtpVerified = false
        this.isSuperUser = false
        this.pendingUsername = null
        this.error = null
        this.loading = false

        localStorage.removeItem('user_data')
        localStorage.removeItem('is_authenticated')
        localStorage.removeItem('is_otp_verified')
        localStorage.removeItem('is_superuser')
      }
    }
  }
})