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
import NoAccess from '../components/NoAccess.vue'

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
    meta: { requiresAuth: true, requiresOtp: true, requiresSuperUser: true } 
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
    path: "/no-access", 
    component: NoAccess, 
  },
  { 
    path: '/:pathMatch(.*)*', 
    name: 'NotFound', 
    component: NotFound,
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
  }

  if (to.meta.requiresAuth) {
    if (!userStore.isAuthenticated) {
      next('/login')
      return
    }

    if (to.meta.requiresOtp && !userStore.isOtpVerified) {
      next('/login')
      return
    }


    if (to.meta.requiresSuperUser && !userStore.isSuperUser) {
      next('/no-access')
      return
    }

    next()
  } else if (to.path === '/login' && userStore.isAuthenticated && userStore.isOtpVerified) {
    next('/books')
  } else {
    next()
  }
})

export default router
