<template>
  <v-app>
    <v-app-bar app color="white" elevation="2" class="px-4">
      <v-btn
        v-if="userStore.isAuthenticated"
        class="mx-1 text-black"
        variant="text"
        to="/genres"
      >
        Жанры
      </v-btn>
      
      <v-btn
        v-if="userStore.isAuthenticated"
        class="mx-1 text-black"
        variant="text"
        to="/libraries"
      >
        Библиотеки
      </v-btn>
      
      <v-btn
        v-if="userStore.isAuthenticated"
        class="mx-1 text-black"
        variant="text"
        to="/books"
      >
        Книги
      </v-btn>
      
      <v-btn
        v-if="userStore.isAuthenticated && userStore.isSuperUser"
        class="mx-1 text-black"
        variant="text"
        to="/members"
      >
        Читатели
      </v-btn>
      
      <v-btn
        v-if="userStore.isAuthenticated"
        class="mx-1 text-black"
        variant="text"
        to="/loans"
      >
        Выдачи
      </v-btn>

      <v-spacer></v-spacer>
      
      <v-menu
        v-if="userStore.isAuthenticated"
        location="bottom end"
      >
        <template #activator="{ props }">
          <v-btn
            v-bind="props"
            class="ml-2 text-black"
            variant="text"
          >
            {{ userStore.user?.username || 'Профиль' }}
            <v-icon end color="black">mdi-menu-down</v-icon>
          </v-btn>
        </template>

        <v-list>
          <v-list-item to="/profile" title="Мой профиль" />
          <v-divider />
          <v-list-item @click="handleLogout" title="Выход" color="error" />
        </v-list>
      </v-menu>

      <v-btn
        v-if="userStore.isAuthenticated"
        href="/admin"
        target="_blank"
        class="ml-2 text-black"
        variant="text"
      >
        Админка
      </v-btn>
    </v-app-bar>
    <v-main>
      <div class="pa-4">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="$route.path" />
          </transition>
        </router-view>
      </div>
    </v-main>
  </v-app>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/userStore'

const router = useRouter()
const userStore = useUserStore()

const handleLogout = async () => {
  await userStore.logout()
  router.push('/login')
}

onMounted(() => {
  userStore.initializeFromStorage()
})
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
