<script setup>
import { ref, onMounted } from "vue";
import { recipesAPI, ingredientsAPI } from "@/services/api.js";

const recipes = ref([]);
const ingredients = ref([]);
const isLoading = ref(false);

const showCreateModal = ref(false);
const showEditModal = ref(false);
const showConfirmDeleteModal = ref(false);

const newRecipe = ref({
  title: "",
  description: "",
  ingredient_ids: [],
});
const editingRecipe = ref(null);
const deletingRecipeId = ref(null);

const loadIngredients = async () => {
  try {
    const res = await ingredientsAPI.getAll();
    ingredients.value = res.data;
  } catch (error) {
    console.error("Erreur chargement ingrédients:", error);
  }
};

const loadRecipes = async () => {
  isLoading.value = true;
  try {
    const res = await recipesAPI.getAll();
    recipes.value = res.data;
  } catch (error) {
    console.error("Erreur chargement recettes:", error);
  } finally {
    isLoading.value = false;
  }
};

const createRecipe = async () => {
  if (!newRecipe.value.title.trim()) return;
  try {
    await recipesAPI.add(newRecipe.value);
    closeCreateModal();
    await loadRecipes();
  } catch (error) {
    console.error("Erreur création recette:", error);
  }
};

const openEditModal = (recipe) => {
  editingRecipe.value = { ...recipe, ingredient_ids: recipe.ingredients.map(i => i.id) };
  showEditModal.value = true;
};

const saveEditRecipe = async () => {
  if (!editingRecipe.value.title.trim()) return;
  try {
    await recipesAPI.update(editingRecipe.value.id, editingRecipe.value);
    closeEditModal();
    await loadRecipes();
  } catch (error) {
    console.error("Erreur modification recette:", error);
  }
};

const openDeleteConfirm = (id) => {
  deletingRecipeId.value = id;
  showConfirmDeleteModal.value = true;
};

const deleteRecipe = async () => {
  try {
    await recipesAPI.delete(deletingRecipeId.value);
    closeDeleteConfirm();
    await loadRecipes();
  } catch (error) {
    console.error("Erreur suppression recette:", error);
  }
};

const resetNewRecipe = () => ({
  title: "",
  description: "",
  ingredient_ids: [],
});

const closeCreateModal = () => {
  showCreateModal.value = false;
  newRecipe.value = resetNewRecipe();
};
const closeEditModal = () => {
  showEditModal.value = false;
  editingRecipe.value = null;
};
const closeDeleteConfirm = () => {
  showConfirmDeleteModal.value = false;
  deletingRecipeId.value = null;
};

onMounted(async () => {
  await loadIngredients();
  await loadRecipes();
});
</script>

<template>
<div class="px-4 py-6 sm:px-0 bg-gray-50 min-h-full">

  <!-- Header -->
  <div class="flex flex-col sm:flex-row justify-between items-center mb-8 border-b pb-4">
    <h1 class="text-4xl font-bold text-gray-900">Mes Recettes</h1>
    <button @click="showCreateModal = true"
      class="flex items-center px-5 py-2 bg-primary-600 text-white font-semibold rounded-md shadow hover:bg-primary-700 transition duration-150 transform hover:scale-105 mt-4 sm:mt-0">
      Ajouter une Recette
    </button>
  </div>

  <!-- État de chargement / vide -->
  <div v-if="isLoading" class="text-center py-10 text-xl text-primary-600">
    Chargement des recettes...
  </div>
  <div v-else-if="!recipes.length" class="text-center py-10 text-gray-500 italic text-lg bg-white rounded-lg shadow-md">
    Aucune recette pour le moment. Ajoutez-en pour commencer !
  </div>

  <!-- Liste des recettes -->
  <div v-else class="space-y-4">
    <div v-for="recipe in recipes" :key="recipe.id" class="bg-white p-4 rounded-lg shadow hover:shadow-lg transition">
      <div class="flex justify-between items-start">
        <div>
          <h2 class="text-xl font-semibold text-gray-900">{{ recipe.title }}</h2>
          <p class="text-gray-600 mt-1">{{ recipe.description }}</p>
          <p class="text-gray-500 mt-2 text-sm">
            <span v-for="ing in recipe.ingredients" :key="ing.id" class="inline-block bg-gray-100 text-gray-800 px-2 py-1 rounded-full mr-2 mb-1">
              {{ ing.name }} ({{ ing.quantity }} {{ ing.unit }})
            </span>
          </p>
        </div>
        <div class="flex space-x-2">
          <button @click="openEditModal(recipe)" class="text-primary-600 hover:text-primary-900 p-1 rounded-full hover:bg-primary-50 transition">
            Modifier
          </button>
          <button @click="openDeleteConfirm(recipe.id)" class="text-red-600 hover:text-red-900 p-1 rounded-full hover:bg-red-50 transition">
            Supprimer
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modaux Créer / Éditer / Supprimer -->
  <Transition name="modal-fade">
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg transform transition-all">
        <h3 class="text-2xl font-bold text-gray-900 mb-4">Ajouter une Recette</h3>
        <form @submit.prevent="createRecipe" class="space-y-4">
          <input v-model="newRecipe.title" type="text" placeholder="Titre" required class="w-full border p-2 rounded-md">
          <textarea v-model="newRecipe.description" placeholder="Description" rows="3" class="w-full border p-2 rounded-md"></textarea>
          <div>
            <label class="block font-medium mb-1">Ingrédients :</label>
            <select v-model="newRecipe.ingredient_ids" multiple class="w-full border p-2 rounded-md">
              <option v-for="ing in ingredients" :key="ing.id" :value="ing.id">{{ ing.name }}</option>
            </select>
          </div>
          <div class="flex justify-end space-x-2">
            <button type="button" @click="closeCreateModal" class="px-4 py-2 bg-gray-200 rounded-md">Annuler</button>
            <button type="submit" class="px-4 py-2 bg-primary-600 text-white rounded-md">Créer</button>
          </div>
        </form>
      </div>
    </div>
  </Transition>

  <Transition name="modal-fade">
    <div v-if="showEditModal && editingRecipe" class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg transform transition-all">
        <h3 class="text-2xl font-bold text-gray-900 mb-4">Modifier : {{ editingRecipe.title }}</h3>
        <form @submit.prevent="saveEditRecipe" class="space-y-4">
          <input v-model="editingRecipe.title" type="text" required class="w-full border p-2 rounded-md">
          <textarea v-model="editingRecipe.description" rows="3" class="w-full border p-2 rounded-md"></textarea>
          <div>
            <label class="block font-medium mb-1">Ingrédients :</label>
            <select v-model="editingRecipe.ingredient_ids" multiple class="w-full border p-2 rounded-md">
              <option v-for="ing in ingredients" :key="ing.id" :value="ing.id">{{ ing.name }}</option>
            </select>
          </div>
          <div class="flex justify-end space-x-2">
            <button type="button" @click="closeEditModal" class="px-4 py-2 bg-gray-200 rounded-md">Annuler</button>
            <button type="submit" class="px-4 py-2 bg-primary-600 text-white rounded-md">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>
  </Transition>

  <Transition name="modal-fade">
    <div v-if="showConfirmDeleteModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md transform transition-all text-center">
        <h3 class="text-xl font-bold text-gray-900 mb-4">Confirmer la suppression</h3>
        <p class="mb-6">Êtes-vous sûr de vouloir supprimer cette recette ?</p>
        <div class="flex justify-center space-x-4">
          <button @click="closeDeleteConfirm" class="px-4 py-2 bg-gray-200 rounded-md">Annuler</button>
          <button @click="deleteRecipe" class="px-4 py-2 bg-red-600 text-white rounded-md">Supprimer</button>
        </div>
      </div>
    </div>
  </Transition>

</div>
</template>
