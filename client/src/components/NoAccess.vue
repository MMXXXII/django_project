<template>
  <v-container fluid class="min-vh-100 d-flex flex-column align-center justify-center text-center bg-white pa-0">
    <img src="https://i.pinimg.com/originals/c3/d7/42/c3d742e30ac2256f94d6d0f13e833845.gif" alt="Танцующая девочка"
      class="dance-girl mb-6" />

    <h1 class="display-1 font-weight-bold text-black mb-3">403</h1>
    <p class="lead text-black mb-6">
      Похоже, вы нашли секретный уголок библиотеки 📚<br />
      Михаил Дмитриевич, 3 хотя бы не ставьте (2 тоже)
    </p>

    <v-btn to="/books" class="white-btn">
      На главную
    </v-btn>

  </v-container>
</template>

<style scoped>
.min-vh-100 {
  min-height: 100vh;
}

.dance-girl {
  max-width: 350px;
  width: 100%;
  height: auto;
}

.display-1 {
  font-weight: bold;
  font-size: 6rem;
  line-height: 1;
}

.lead {
  font-size: 1.25rem;
}
</style>
