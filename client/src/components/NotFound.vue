<script setup>
</script>

<template>
  <div class="d-flex flex-column align-items-center pt-5 text-center bg-white min-vh-100">
    <img 
      src="https://i.pinimg.com/originals/c3/d7/42/c3d742e30ac2256f94d6d0f13e833845.gif" 
      alt="Танцующая девочка" 
      class="dance-girl mb-4" 
    />

    <h1 class="display-1 mb-3 text-dark">404</h1>
    <p class="lead mb-4 text-secondary">
      Похоже, вы нашли секретный уголок библиотеки 📚<br>
      Михаил Дмитриевич, поставьте 5
    </p>

    <router-link class="btn btn-light btn-lg" to="/books">
      На главную
    </router-link>
  </div>
</template>


<style scoped>
.min-vh-100 {
  min-height: 100vh;
}
.display-1 {
  font-weight: bold;
}
.lead {
  font-size: 1.25rem;
}
.btn-light {
  color: #212529;
  background-color: #f8f9fa;
  border: none;
  box-shadow: none;
}
.btn-light:hover {
  background-color: #f1f1f1;
}
.dance-girl {
  max-width: 350px;
  width: 100%;
  height: auto;
}
</style>
