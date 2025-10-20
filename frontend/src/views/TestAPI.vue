<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">Test API GroceryMate</h1>

    <section class="mb-6">
      <h2 class="text-xl font-semibold">Shopping Lists</h2>
      <ul>
        <li v-for="list in shoppingLists" :key="list.id">
          {{ list.name }}
        </li>
      </ul>
    </section>

    <section class="mb-6">
      <h2 class="text-xl font-semibold">Ingredients</h2>
      <ul>
        <li v-for="ingredient in ingredients" :key="ingredient.id">
          {{ ingredient.name }} - {{ ingredient.quantity }}
        </li>
      </ul>
    </section>

    <section>
      <h2 class="text-xl font-semibold">Recipes</h2>
      <ul>
        <li v-for="recipe in recipes" :key="recipe.id">
          {{ recipe.name }}
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { shoppingListsAPI, ingredientsAPI, recipesAPI } from "@/services/api.js";

const shoppingLists = ref([]);
const ingredients = ref([]);
const recipes = ref([]);

onMounted(async () => {
  try {
    const shoppingRes = await shoppingListsAPI.getAll();
    shoppingLists.value = shoppingRes.data;

    const ingredientsRes = await ingredientsAPI.getAll();
    ingredients.value = ingredientsRes.data;

    const recipesRes = await recipesAPI.getAll();
    recipes.value = recipesRes.data;

    console.log("Shopping Lists:", shoppingRes.data);
    console.log("Ingredients:", ingredientsRes.data);
    console.log("Recipes:", recipesRes.data);
  } catch (err) {
    console.error("Erreur API :", err);
  }
});
</script>
