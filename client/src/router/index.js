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
import NoAccess from '../components/NoAccess.vue' // Страница для доступа без прав

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
    meta: { requiresAuth: true, requiresOtp: true, requiresSuperUser: true } // Проверка на суперпользователя
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
    component: NoAccess, // Страница ошибки доступа
    meta: { hideHeader: true }
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

let initialized = false  // Инициализация переменной

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // Проверяем, была ли уже выполнена инициализация
  if (!initialized) {
    initialized = true
    const restored = userStore.initializeFromStorage()
    console.log('[v0] Store initialized from storage:', restored)
  }

  // Проверка, требует ли маршрут авторизации
  if (to.meta.requiresAuth) {
    if (!userStore.isAuthenticated) {
      console.log('[v0] Not authenticated, redirecting to login')
      next('/login')
      return
    }

    // Проверка на OTP (если требуется)
    if (to.meta.requiresOtp && !userStore.isOtpVerified) {
      console.log('[v0] OTP not verified, redirecting to login')
      next('/login')
      return
    }

    // Проверка на суперпользователя, если это требуется
    if (to.meta.requiresSuperUser && !userStore.isSuperUser) {
      console.log('[v0] Not superuser, redirecting to no-access')
      next('/no-access') // Редирект на страницу с ошибкой доступа, если не суперпользователь
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
