<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-green-600 p-4 text-white flex gap-6">
      <router-link to="/" class="hover:underline">Dashboard</router-link>
      <router-link to="/ingredients" class="hover:underline">Ingredients</router-link>
      <router-link to="/recipes" class="hover:underline">Recipes</router-link>
      <router-link to="/shopping-lists" class="hover:underline">Shopping Lists</router-link>
    </nav>

    <main class="p-6">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
// rien à ajouter ici
</script>

<style scoped>
body {
  font-family: Arial, sans-serif;
}
.router-link-exact-active {
  font-weight: bold;
  text-decoration: underline;
}
</style>
