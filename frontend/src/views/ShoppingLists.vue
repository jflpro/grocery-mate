<template>
  <div class="p-6 bg-gray-50 min-h-full">

    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-center mb-8 border-b pb-4">
      <h1 class="text-4xl font-extrabold text-gray-800">Mes Listes de Courses</h1>
      <button @click="showCreateList = true"
        class="flex items-center px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 transition duration-150 transform hover:scale-105 mt-4 sm:mt-0">
        Ajouter une Liste
      </button>
    </div>

    <!-- Aucune liste -->
    <div v-if="!shoppingLists.length && !showCreateList"
         class="text-center py-10 text-gray-500 italic text-lg bg-white rounded-xl shadow-lg">
      Aucune liste de courses pour le moment. Créez-en une pour commencer !
    </div>

    <!-- Listes -->
    <div v-for="list in shoppingLists" :key="list.id" class="bg-white rounded-xl shadow-xl p-4 mb-6">
      <div class="flex justify-between items-center mb-2">
        <h2 class="text-xl font-semibold">{{ list.name }}</h2>
        <div class="flex space-x-2">
          <button @click="editList(list)" class="text-indigo-600 hover:text-indigo-900 transition">Modifier</button>
          <button @click="deleteList(list.id)" class="text-red-600 hover:text-red-900 transition">Supprimer</button>
          <button @click="openAddItem(list.id)" class="text-green-600 hover:text-green-900 transition">Ajouter un item</button>
        </div>
      </div>
      <ul>
        <li v-for="item in list.items" :key="item.id" class="flex justify-between items-center py-1 border-b">
          <div class="flex items-center">
            <input type="checkbox" v-model="item.is_purchased" @change="toggleItemStatus(item.id, item.is_purchased)" class="mr-2">
            <span :class="item.is_purchased ? 'line-through text-gray-400' : ''">
              {{ item.item_name }} - {{ item.quantity }} {{ item.unit }}
            </span>
          </div>
          <button @click="deleteItem(item.id)" class="text-red-600 hover:text-red-900 transition">Supprimer</button>
        </li>
      </ul>
    </div>

    <!-- MODAL: Créer une liste -->
    <Transition name="modal-fade">
      <div v-if="showCreateList" class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
        <div class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md transform transition-all">
          <h3 class="text-2xl font-bold text-gray-800 mb-4">Nouvelle Liste de Courses</h3>
          <form @submit.prevent="createList" class="space-y-4">
            <input type="text" v-model="newListName" placeholder="Nom de la liste" required
                   class="w-full border border-gray-300 rounded-lg p-3 focus:ring-indigo-500 focus:border-indigo-500">
            <div class="flex justify-end space-x-3">
              <button type="button" @click="showCreateList = false"
                      class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition">Annuler</button>
              <button type="submit"
                      class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">Créer</button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- MODAL: Ajouter un item -->
    <Transition name="modal-fade">
      <div v-if="showAddItem" class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
        <div class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md transform transition-all">
          <h3 class="text-2xl font-bold text-gray-800 mb-4">Ajouter un Item</h3>
          <form @submit.prevent="addItem" class="space-y-4">
            <input type="text" v-model="newItem.item_name" placeholder="Nom de l'item" required
                   class="w-full border border-gray-300 rounded-lg p-3 focus:ring-indigo-500 focus:border-indigo-500">
            <div class="flex space-x-2">
              <input type="number" v-model.number="newItem.quantity" min="1" step="any" required
                     class="w-1/2 border border-gray-300 rounded-lg p-3 focus:ring-indigo-500 focus:border-indigo-500">
              <input type="text" v-model="newItem.unit" placeholder="Unité"
                     class="w-1/2 border border-gray-300 rounded-lg p-3 focus:ring-indigo-500 focus:border-indigo-500">
            </div>
            <div class="flex justify-end space-x-3">
              <button type="button" @click="showAddItem = false"
                      class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition">Annuler</button>
              <button type="submit"
                      class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">Ajouter</button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { shoppingListsAPI } from "@/services/api.js";

const shoppingLists = ref([]);
const showCreateList = ref(false);
const newListName = ref("");
const showAddItem = ref(false);
const currentListId = ref(null);
const newItem = ref({ item_name: "", quantity: 1, unit: "kg", is_purchased: false });

const loadShoppingLists = async () => {
  try {
    const res = await shoppingListsAPI.getAll();
    shoppingLists.value = res.data;
  } catch (error) {
    console.error("Erreur chargement shopping lists:", error);
  }
};

const createList = async () => {
  if (!newListName.value.trim()) return;
  try {
    await shoppingListsAPI.add({ name: newListName.value });
    newListName.value = "";
    showCreateList.value = false;
    await loadShoppingLists();
  } catch (error) {
    console.error("Erreur création liste:", error);
  }
};

const editList = async (list) => {
  const newName = prompt("Nouveau nom de la liste :", list.name);
  if (!newName || !newName.trim()) return;
  try {
    await shoppingListsAPI.update(list.id, { name: newName });
    await loadShoppingLists();
  } catch (error) {
    console.error("Erreur modification liste:", error);
  }
};

const deleteList = async (id) => {
  if (!confirm("Supprimer cette liste ?")) return;
  try {
    await shoppingListsAPI.delete(id);
    await loadShoppingLists();
  } catch (error) {
    console.error("Erreur suppression liste:", error);
  }
};

const openAddItem = (listId) => {
  currentListId.value = listId;
  showAddItem.value = true;
};

const addItem = async () => {
  if (!newItem.value.item_name.trim() || newItem.value.quantity <= 0) return;
  try {
    await shoppingListsAPI.addItem(currentListId.value, newItem.value);
    newItem.value = { item_name: "", quantity: 1, unit: "kg", is_purchased: false };
    showAddItem.value = false;
    await loadShoppingLists();
  } catch (error) {
    console.error("Erreur ajout item:", error);
  }
};

const toggleItemStatus = async (itemId, isPurchased) => {
  try {
    await shoppingListsAPI.updateItem(itemId, { is_purchased: isPurchased });
    await loadShoppingLists();
  } catch (error) {
    console.error("Erreur mise à jour status item:", error);
  }
};

const deleteItem = async (itemId) => {
  if (!confirm("Supprimer cet item ?")) return;
  try {
    await shoppingListsAPI.deleteItem(itemId);
    await loadShoppingLists();
  } catch (error) {
    console.error("Erreur suppression item:", error);
  }
};

onMounted(() => loadShoppingLists());
</script>

<style scoped>
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
