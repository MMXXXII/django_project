import { createRouter, createWebHistory } from "vue-router"
import { useUserStore } from "../stores/userStore"
import Genres from "../components/Genres.vue"
import Libraries from "../components/Libraries.vue"
import Books from "../components/Books.vue"
import Members from "../components/Members.vue"
import Loans from "../components/Loans.vue"
import Profile from "../components/Profile.vue"
import Login from "../components/Login.vue"
import NotFound from '../components/NotFound.vue'


const routes = [
  { 
    path: "/", 
    redirect: "/books" 
  },
  { 
    path: "/genres", 
    component: Genres,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/libraries", 
    component: Libraries,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/books", 
    component: Books,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/members", 
    component: Members,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/loans", 
    component: Loans,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/profile", 
    component: Profile,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/login", 
    component: Login 
  },
  { 
    path: '/:pathMatch(.*)*', 
    name: 'NotFound', 
    component: NotFound,
    meta: { hideHeader: true }  
  }
]


const router = createRouter({
  history: createWebHistory(),
  routes,
})

let initialized = false

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  if (!initialized) {
    initialized = true
    const restored = userStore.initializeFromStorage()
    console.log('[v0] Store initialized from storage:', restored)
  }
  
  if (to.meta.requiresAuth) {
    if (!userStore.isAuthenticated) {
      console.log('[v0] Not authenticated, redirecting to login')
      next('/login')
      return
    }
    
    if (to.meta.requiresOtp && !userStore.isOtpVerified) {
      console.log('[v0] OTP not verified, redirecting to login')
      next('/login')
      return
    }
    
    next()
  } else if (to.path === '/login' && userStore.isAuthenticated && userStore.isOtpVerified) {
    console.log('[v0] Already authenticated, redirecting to books')
    next('/books')
  } else {
    next()
  }
})

export default router
