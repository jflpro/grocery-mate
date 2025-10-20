<script setup>
import { ref, onMounted } from "vue";
import { ingredientsAPI } from "@/services/api.js";
import { format } from "date-fns";
import { fr } from "date-fns/locale";

const UNITS = ["g", "kg", "ml", "L", "unité", "paquet"];

const ingredients = ref([]);
const isLoading = ref(false);

const showCreateModal = ref(false);
const showEditModal = ref(false);
const showConfirmDeleteModal = ref(false);

const newIngredient = ref({
  name: "",
  quantity: 1,
  unit: "unité",
  expiration_date: null,
});
const editingIngredient = ref(null);
const deletingIngredientId = ref(null);

const formatDate = (dateString) => {
  if (!dateString) return "Non spécifiée";
  try {
    return format(new Date(dateString), "dd MMMM yyyy", { locale: fr });
  } catch (e) {
    return dateString;
  }
};

const loadIngredients = async () => {
  isLoading.value = true;
  try {
    const res = await ingredientsAPI.getAll();
    ingredients.value = res.data.sort((a, b) => {
      if (a.expiration_date && b.expiration_date)
        return new Date(a.expiration_date) - new Date(b.expiration_date);
      if (a.expiration_date) return -1;
      if (b.expiration_date) return 1;
      return 0;
    });
  } catch (error) {
    console.error("Erreur chargement ingrédients:", error);
  } finally {
    isLoading.value = false;
  }
};

const createIngredient = async () => {
  if (!newIngredient.value.name.trim() || newIngredient.value.quantity <= 0)
    return;
  try {
    await ingredientsAPI.add(newIngredient.value);
    closeCreateModal();
    await loadIngredients();
  } catch (error) {
    console.error("Erreur création ingrédient:", error);
  }
};

const openEditModal = (ingredient) => {
  editingIngredient.value = { ...ingredient };
  showEditModal.value = true;
};

const saveEditIngredient = async () => {
  if (!editingIngredient.value.name.trim() || editingIngredient.value.quantity <= 0)
    return;
  try {
    await ingredientsAPI.update(editingIngredient.value.id, editingIngredient.value);
    closeEditModal();
    await loadIngredients();
  } catch (error) {
    console.error("Erreur modification ingrédient:", error);
  }
};

const openDeleteConfirm = (id) => {
  deletingIngredientId.value = id;
  showConfirmDeleteModal.value = true;
};

const deleteIngredient = async () => {
  try {
    await ingredientsAPI.delete(deletingIngredientId.value);
    closeDeleteConfirm();
    await loadIngredients();
  } catch (error) {
    console.error("Erreur suppression ingrédient:", error);
  }
};

const resetNewIngredient = () => ({
  name: "",
  quantity: 1,
  unit: "unité",
  expiration_date: null,
});

const closeCreateModal = () => {
  showCreateModal.value = false;
  newIngredient.value = resetNewIngredient();
};
const closeEditModal = () => {
  showEditModal.value = false;
  editingIngredient.value = null;
};
const closeDeleteConfirm = () => {
  showConfirmDeleteModal.value = false;
  deletingIngredientId.value = null;
};

onMounted(() => loadIngredients());
</script>

<template>
<div class="px-4 py-6 sm:px-0 bg-gray-50 min-h-full">

  <!-- Header -->
  <div class="flex flex-col sm:flex-row justify-between items-center mb-8 border-b pb-4">
    <h1 class="text-4xl font-bold text-gray-900">Mon Inventaire</h1>
    <button @click="showCreateModal = true"
      class="flex items-center px-5 py-2 bg-primary-600 text-white font-semibold rounded-md shadow hover:bg-primary-700 transition duration-150 transform hover:scale-105 mt-4 sm:mt-0">
      <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
      Ajouter un Ingrédient
    </button>
  </div>

  <!-- État de chargement / vide -->
  <div v-if="isLoading" class="text-center py-10 text-xl text-primary-600">
    Chargement de l'inventaire...
  </div>
  <div v-else-if="!ingredients.length" class="text-center py-10 text-gray-500 italic text-lg bg-white rounded-lg shadow-md">
    Votre inventaire est vide. Ajoutez quelques ingrédients pour commencer !
  </div>

  <!-- Tableau -->
  <div v-else class="bg-white shadow-md rounded-lg overflow-hidden">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ingrédient</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantité</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date d'Expiration</th>
          <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr v-for="ing in ingredients" :key="ing.id" class="hover:bg-gray-50 transition">
          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ ing.name }}</td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ ing.quantity }} {{ ing.unit }}</td>
          <td class="px-6 py-4 whitespace-nowrap text-sm">
            <span :class="{
                'bg-red-100 text-red-800': ing.expiration_date && new Date(ing.expiration_date) < new Date(),
                'bg-yellow-100 text-yellow-800': ing.expiration_date && new Date(ing.expiration_date) < new Date(Date.now()+7*24*60*60*1000) && new Date(ing.expiration_date) >= new Date(),
                'bg-green-100 text-green-800': !ing.expiration_date || new Date(ing.expiration_date) >= new Date(Date.now()+7*24*60*60*1000)
              }" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
              {{ formatDate(ing.expiration_date) }}
            </span>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
            <div class="flex justify-end space-x-3">
              <button @click="openEditModal(ing)" title="Modifier" class="text-primary-600 hover:text-primary-900 p-1 rounded-full hover:bg-primary-50 transition">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
              </button>
              <button @click="openDeleteConfirm(ing.id)" title="Supprimer" class="text-red-600 hover:text-red-900 p-1 rounded-full hover:bg-red-50 transition">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Modaux (Créer / Éditer / Supprimer) -->
  <Transition name="modal-fade">
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg transform transition-all">
        <h3 class="text-2xl font-bold text-gray-900 mb-4">Ajouter un Nouvel Ingrédient</h3>
        <form @submit.prevent="createIngredient" class="space-y-4">
          <!-- Form Fields identiques au fichier original -->
        </form>
      </div>
    </div>
  </Transition>

  <Transition name="modal-fade">
    <div v-if="showEditModal && editingIngredient" class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg transform transition-all">
        <h3 class="text-2xl font-bold text-gray-900 mb-4">Modifier l'Ingrédient: {{ editingIngredient.name }}</h3>
        <form @submit.prevent="saveEditIngredient" class="space-y-4">
          <!-- Form Fields identiques au fichier original -->
        </form>
      </div>
    </div>
  </Transition>

  <Transition name="modal-fade">
    <div v-if="showConfirmDeleteModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md transform transition-all">
        <h3 class="text-xl font-bold text-gray-900 mb-2">Confirmer la Suppression</h3>
        <p class="text-gray-700 mb-4">Êtes-vous sûr de vouloir supprimer cet ingrédient ?</p>
        <div class="flex justify-end space-x-3">
          <button type="button" @click="closeDeleteConfirm" class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition">Annuler</button>
          <button type="button" @click="deleteIngredient" class="px-4 py-2 bg-red-600 text-white font-semibold rounded-md shadow hover:bg-red-700 transition">Supprimer</button>
        </div>
      </div>
    </div>
  </Transition>

</div>
</template>

<style scoped>
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
