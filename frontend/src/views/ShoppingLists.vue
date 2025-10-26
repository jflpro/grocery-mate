<script setup>
import { ref, onMounted } from "vue";
// ✅ Correction ici : nom exact de l'export dans api.js
import { shoppingListsAPI, ingredientsAPI } from "@/services/api.js";

// --- Références réactives ---
const shoppingItems = ref([]);
const ingredients = ref([]);
const isLoading = ref(false);

const showCreateModal = ref(false);
const showEditModal = ref(false);
const showConfirmDeleteModal = ref(false);

const newItem = ref({
  ingredient_id: null,
  quantity: 1,
});
const editingItem = ref(null);
const deletingItemId = ref(null);

// --- Chargement des ingrédients ---
const loadIngredients = async () => {
  try {
    const res = await ingredientsAPI.getAll();
    ingredients.value = res.data;
  } catch (error) {
    console.error("Erreur chargement ingrédients:", error);
  }
};

// --- Chargement des items de la liste ---
const loadShoppingItems = async () => {
  isLoading.value = true;
  try {
    const res = await shoppingListsAPI.getAll();
    shoppingItems.value = res.data;
  } catch (error) {
    console.error("Erreur chargement liste de courses:", error);
  } finally {
    isLoading.value = false;
  }
};

// --- Ajouter un item ---
const addItem = async () => {
  if (!newItem.value.ingredient_id) return;
  try {
    await shoppingListsAPI.add(newItem.value);
    closeCreateModal();
    await loadShoppingItems();
  } catch (error) {
    console.error("Erreur ajout item:", error);
  }
};

// --- Editer un item ---
const openEditModal = (item) => {
  editingItem.value = { ...item };
  showEditModal.value = true;
};

const saveEditItem = async () => {
  if (!editingItem.value.ingredient_id) return;
  try {
    await shoppingListsAPI.update(editingItem.value.id, editingItem.value);
    closeEditModal();
    await loadShoppingItems();
  } catch (error) {
    console.error("Erreur modification item:", error);
  }
};

// --- Supprimer un item ---
const openDeleteConfirm = (id) => {
  deletingItemId.value = id;
  showConfirmDeleteModal.value = true;
};

const deleteItem = async () => {
  try {
    await shoppingListsAPI.delete(deletingItemId.value);
    closeDeleteConfirm();
    await loadShoppingItems();
  } catch (error) {
    console.error("Erreur suppression item:", error);
  }
};

// --- Réinitialiser un nouvel item ---
const resetNewItem = () => ({
  ingredient_id: null,
  quantity: 1,
});

// --- Fermeture des modaux ---
const closeCreateModal = () => {
  showCreateModal.value = false;
  newItem.value = resetNewItem();
};
const closeEditModal = () => {
  showEditModal.value = false;
  editingItem.value = null;
};
const closeDeleteConfirm = () => {
  showConfirmDeleteModal.value = false;
  deletingItemId.value = null;
};

// --- Montée initiale ---
onMounted(async () => {
  await loadIngredients();
  await loadShoppingItems();
});
</script>

<template>
<div class="px-4 py-6 sm:px-0 bg-gray-50 min-h-full">

  <!-- Header -->
  <div class="flex flex-col sm:flex-row justify-between items-center mb-8 border-b pb-4">
    <h1 class="text-4xl font-bold text-gray-900">Liste de Courses</h1>
    <button @click="showCreateModal = true"
      class="flex items-center px-5 py-2 bg-primary-600 text-white font-semibold rounded-md shadow hover:bg-primary-700 transition duration-150 transform hover:scale-105 mt-4 sm:mt-0">
      Ajouter un Item
    </button>
  </div>

  <!-- État de chargement / vide -->
  <div v-if="isLoading" class="text-center py-10 text-xl text-primary-600">
    Chargement des items...
  </div>
  <div v-else-if="!shoppingItems.length" class="text-center py-10 text-gray-500 italic text-lg bg-white rounded-lg shadow-md">
    Aucun item pour le moment. Ajoutez-en pour commencer !
  </div>

  <!-- Liste des items -->
  <div v-else class="space-y-4">
    <div v-for="item in shoppingItems" :key="item.id" class="bg-white p-4 rounded-lg shadow hover:shadow-lg transition flex justify-between items-center">
      <div>
        <h2 class="text-lg font-semibold text-gray-900">{{ item.ingredient.name }}</h2>
        <p class="text-gray-600">Quantité: {{ item.quantity }} {{ item.ingredient.unit }}</p>
      </div>
      <div class="flex space-x-2">
        <button @click="openEditModal(item)" class="text-primary-600 hover:text-primary-900 p-1 rounded-full hover:bg-primary-50 transition">
          Modifier
        </button>
        <button @click="openDeleteConfirm(item.id)" class="text-red-600 hover:text-red-900 p-1 rounded-full hover:bg-red-50 transition">
          Supprimer
        </button>
      </div>
    </div>
  </div>

  <!-- Modaux Créer / Éditer / Supprimer -->
  <Transition name="modal-fade">
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg transform transition-all">
        <h3 class="text-2xl font-bold text-gray-900 mb-4">Ajouter un Item</h3>
        <form @submit.prevent="addItem" class="space-y-4">
          <div>
            <label class="block font-medium mb-1">Ingrédient :</label>
            <select v-model="newItem.ingredient_id" class="w-full border p-2 rounded-md" required>
              <option value="" disabled>Sélectionner un ingrédient</option>
              <option v-for="ing in ingredients" :key="ing.id" :value="ing.id">{{ ing.name }}</option>
            </select>
          </div>
          <div>
            <label class="block font-medium mb-1">Quantité :</label>
            <input v-model.number="newItem.quantity" type="number" min="1" class="w-full border p-2 rounded-md">
          </div>
          <div class="flex justify-end space-x-2">
            <button type="button" @click="closeCreateModal" class="px-4 py-2 bg-gray-200 rounded-md">Annuler</button>
            <button type="submit" class="px-4 py-2 bg-primary-600 text-white rounded-md">Ajouter</button>
          </div>
        </form>
      </div>
    </div>
  </Transition>

  <Transition name="modal-fade">
    <div v-if="showEditModal && editingItem" class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg transform transition-all">
        <h3 class="text-2xl font-bold text-gray-900 mb-4">Modifier : {{ editingItem.ingredient.name }}</h3>
        <form @submit.prevent="saveEditItem" class="space-y-4">
          <div>
            <label class="block font-medium mb-1">Ingrédient :</label>
            <select v-model="editingItem.ingredient_id" class="w-full border p-2 rounded-md" required>
              <option value="" disabled>Sélectionner un ingrédient</option>
              <option v-for="ing in ingredients" :key="ing.id" :value="ing.id">{{ ing.name }}</option>
            </select>
          </div>
          <div>
            <label class="block font-medium mb-1">Quantité :</label>
            <input v-model.number="editingItem.quantity" type="number" min="1" class="w-full border p-2 rounded-md">
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
        <p class="mb-6">Êtes-vous sûr de vouloir supprimer cet item ?</p>
        <div class="flex justify-center space-x-4">
          <button @click="closeDeleteConfirm" class="px-4 py-2 bg-gray-200 rounded-md">Annuler</button>
          <button @click="deleteItem" class="px-4 py-2 bg-red-600 text-white rounded-md">Supprimer</button>
        </div>
      </div>
    </div>
  </Transition>

</div>
</template>
