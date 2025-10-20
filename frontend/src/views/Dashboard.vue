<template>
  <div class="px-4 py-6 sm:px-0">
    <h2 class="text-3xl font-bold text-gray-900 mb-6">Dashboard</h2>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="text-4xl">🥬</div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Ingredients</dt>
                <dd class="text-3xl font-semibold text-gray-900">{{ stats.totalIngredients }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="text-4xl">❄️</div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">In Fridge</dt>
                <dd class="text-3xl font-semibold text-gray-900">{{ stats.fridgeItems }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="text-4xl">🗄️</div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">In Pantry</dt>
                <dd class="text-3xl font-semibold text-gray-900">{{ stats.pantryItems }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="text-4xl">⚠️</div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Expiring Soon</dt>
                <dd class="text-3xl font-semibold text-red-600">{{ stats.expiringSoon }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Expiring Items Alert -->
    <div v-if="expiringItems.length > 0" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Items Expiring Soon</h3>
          <div class="mt-2 text-sm text-red-700">
            <ul class="list-disc list-inside space-y-1">
              <li v-for="item in expiringItems" :key="item.id">
                {{ item.name }} - Expires: {{ formatDate(item.expiry_date) }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <router-link
          to="/ingredients"
          class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
        >
          Add Ingredient
        </router-link>
        <router-link
          to="/shopping"
          class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          Create Shopping List
        </router-link>
        <router-link
          to="/recipes"
          class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700"
        >
          Find Recipes
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ingredientsAPI } from "@/services/api.js";

const stats = ref({
  totalIngredients: 0,
  fridgeItems: 0,
  pantryItems: 0,
  expiringSoon: 0
});

const expiringItems = ref([]);

const loadDashboard = async () => {
  try {
    const [allItems, fridgeItems, pantryItems, expiring] = await Promise.all([
      ingredientsAPI.getAll(),
      ingredientsAPI.getAll('Fridge'),
      ingredientsAPI.getAll('Pantry'),
      ingredientsAPI.getExpiringSoon(7)
    ]);

    stats.value = {
      totalIngredients: allItems.data.length,
      fridgeItems: fridgeItems.data.length,
      pantryItems: pantryItems.data.length,
      expiringSoon: expiring.data.length
    };

    expiringItems.value = expiring.data;
  } catch (error) {
    console.error('Error loading dashboard:', error);
  }
};

const formatDate = (dateString) => new Date(dateString).toLocaleDateString();

onMounted(() => loadDashboard());
</script>
