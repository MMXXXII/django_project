import { createRouter, createWebHistory } from 'vue-router'
import Genres from '../components/Genres.vue'
import Libraries from '../components/Libraries.vue'
import Books from '../components/Books.vue'
import Members from '../components/Members.vue'
import Loans from '../components/Loans.vue'


const routes = [
  { path: '/', redirect: '/books' },
  { path: '/genres', component: Genres },
  { path: '/libraries', component: Libraries },
  { path: '/books', component: Books },
  { path: '/members', component: Members },
  { path: '/loans', component: Loans },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
