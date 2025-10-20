<template>
  <div class="px-4 py-6 sm:px-0 bg-gray-50 min-h-full">

    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-center mb-6">
      <h2 class="text-3xl font-bold text-gray-900">Mes Recettes</h2>
      <div class="flex space-x-3 mt-4 sm:mt-0">
        <button
          @click="findMatchingRecipes"
          class="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-md shadow hover:bg-primary-700 transition"
        >
          🔍 Recettes disponibles
        </button>
        <button
          @click="seedSampleRecipes"
          class="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md bg-white hover:bg-gray-50 transition"
        >
          📚 Recettes exemple
        </button>
      </div>
    </div>

    <!-- Healthy Filter -->
    <div class="mb-6">
      <button
        @click="showHealthyOnly = !showHealthyOnly"
        :class="showHealthyOnly ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
        class="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium"
      >
        {{ showHealthyOnly ? '✓' : '' }} Healthy Recipes Only
      </button>
    </div>

    <!-- Matching Recipes Alert -->
    <div v-if="showMatchingOnly" class="bg-green-50 border-l-4 border-green-400 p-4 mb-6 rounded-md shadow">
      <div class="flex items-start">
        <svg class="h-5 w-5 text-green-400 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <p class="ml-3 text-sm text-green-700">
          Showing recipes you can make with your available ingredients! 
          <button @click="showMatchingOnly = false" class="font-medium underline">Show all recipes</button>
        </p>
      </div>
    </div>

    <!-- Recipes Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="recipe in displayedRecipes" :key="recipe.id" class="bg-white rounded-lg shadow hover:shadow-lg transition">
        <div class="p-6">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-xl font-semibold text-gray-900">{{ recipe.name }}</h3>
            <span v-if="recipe.is_healthy" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Healthy
            </span>
          </div>
          <p class="text-gray-600 text-sm mb-4">{{ recipe.description }}</p>
          <div class="space-y-2 mb-4 text-sm text-gray-500">
            <div class="flex items-center">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Prep time: {{ recipe.prep_time }} min
            </div>
            <div class="flex items-center">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              Servings: {{ recipe.servings }}
            </div>
            <div v-if="recipe.calories" class="flex items-center">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Calories: {{ recipe.calories }}
            </div>
          </div>
          <button
            @click="viewRecipe(recipe)"
            class="w-full px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700 transition"
          >
            View Recipe
          </button>
        </div>
      </div>
    </div>

    <div v-if="displayedRecipes.length === 0" class="text-center py-12 bg-white rounded-lg shadow mt-6">
      <p class="text-gray-500">No recipes found. Try loading sample recipes or adjust your filters!</p>
    </div>

    <!-- Recipe Detail Modal -->
    <Transition name="modal-fade">
      <div v-if="selectedRecipe" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-600 bg-opacity-75">
        <div class="bg-white rounded-lg shadow-xl p-6 max-w-lg w-full transform transition-all">
          <h3 class="text-lg font-medium text-gray-900">{{ selectedRecipe.name }}</h3>
          <p class="text-sm text-gray-500 mb-4">{{ selectedRecipe.description }}</p>
          <ul class="text-sm text-gray-500 list-disc list-inside">
            <li v-for="ingredient in selectedRecipe.ingredients" :key="ingredient.id">
              {{ ingredient.name }} - {{ ingredient.quantity }}
            </li>
          </ul>
          <div class="mt-5 flex justify-end">
            <button @click="selectedRecipe = null" class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
              Close
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script>
import { ref } from "vue";

export default {
  setup() {
    const displayedRecipes = ref([]);
    const selectedRecipe = ref(null);
    const showHealthyOnly = ref(false);
    const showMatchingOnly = ref(false);

    const viewRecipe = (recipe) => {
      selectedRecipe.value = recipe;
    };
    const findMatchingRecipes = () => {};
    const seedSampleRecipes = () => {};

    return {
      displayedRecipes,
      selectedRecipe,
      showHealthyOnly,
      showMatchingOnly,
      viewRecipe,
      findMatchingRecipes,
      seedSampleRecipes
    };
  }
};
</script>

<style scoped>
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
