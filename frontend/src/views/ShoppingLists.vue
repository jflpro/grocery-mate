<script setup>
import { ref, onMounted } from "vue";
import { shoppingListsAPI, ingredientsAPI, aiAPI } from "@/services/api.js";

/* -----------------------------------------
   STATE
----------------------------------------- */
const shoppingList = ref(null);       // Active list (single default list)
const shoppingItems = ref([]);        // Items of the active list
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

/* -----------------------------------------
   AI STATE
----------------------------------------- */
const aiLoading = ref(false);
const aiSuggestions = ref(null);

/* -----------------------------------------
   LOADERS
----------------------------------------- */
const loadIngredients = async () => {
  try {
    const res = await ingredientsAPI.getAll();
    ingredients.value = res.data || [];
  } catch (error) {
    console.error("Error loading ingredients:", error);
  }
};

/**
 * Ensure the user has at least one shopping list.
 * - If none exists, we create a default one: "My Shopping List"
 * - Then we keep the first list as the active one and display its items.
 */
const ensureDefaultShoppingList = async () => {
  const res = await shoppingListsAPI.getAll(); // GET /shopping-lists/
  const lists = res.data || [];

  if (lists.length === 0) {
    // Create default list
    const created = await shoppingListsAPI.createList({
      name: "My Shopping List",
    });
    shoppingList.value = created.data;
  } else {
    shoppingList.value = lists[0];
  }

  shoppingItems.value = shoppingList.value.items || [];
};

const reloadActiveList = async () => {
  if (!shoppingList.value) {
    await ensureDefaultShoppingList();
    return;
  }
  // Reload all lists and find the active one again
  const res = await shoppingListsAPI.getAll();
  const lists = res.data || [];
  const found = lists.find((l) => l.id === shoppingList.value.id) || lists[0];
  shoppingList.value = found || null;
  shoppingItems.value = shoppingList.value ? shoppingList.value.items || [] : [];
};

const loadShoppingContext = async () => {
  isLoading.value = true;
  try {
    await ensureDefaultShoppingList();
  } catch (error) {
    console.error("Error loading shopping lists:", error);
  } finally {
    isLoading.value = false;
  }
};

/* -----------------------------------------
   CREATE ITEM
----------------------------------------- */
const addItem = async () => {
  if (!shoppingList.value) {
    await ensureDefaultShoppingList();
  }

  const listId = shoppingList.value?.id;
  if (!listId || !newItem.value.ingredient_id) return;

  const ingredient = ingredients.value.find(
    (i) => i.id === newItem.value.ingredient_id,
  );
  if (!ingredient) return;

  // Backend expects ShoppingItemCreate: { item_name, quantity, unit }
  const payload = {
    item_name: ingredient.name,
    quantity: newItem.value.quantity || 1,
    unit: ingredient.unit || "pcs",
  };

  try {
    await shoppingListsAPI.addItem(listId, payload); // POST /shopping-lists/{listId}/items
    closeCreateModal();
    await reloadActiveList();
  } catch (error) {
    console.error("Error adding item:", error.response?.data || error);
  }
};

/* -----------------------------------------
   EDIT ITEM
----------------------------------------- */
const openEditModal = (item) => {
  // item comes from backend: { id, item_name, quantity, unit, ... }
  editingItem.value = { ...item };
  showEditModal.value = true;
};

const saveEditItem = async () => {
  if (!editingItem.value || !editingItem.value.id) return;

  const payload = {
    item_name: editingItem.value.item_name,
    quantity: editingItem.value.quantity,
    unit: editingItem.value.unit,
    is_purchased: editingItem.value.is_purchased,
  };

  try {
    await shoppingListsAPI.updateItem(editingItem.value.id, payload); // PUT /shopping-lists/items/{id}
    closeEditModal();
    await reloadActiveList();
  } catch (error) {
    console.error("Error updating item:", error.response?.data || error);
  }
};

/* -----------------------------------------
   DELETE ITEM
----------------------------------------- */
const openDeleteConfirm = (id) => {
  deletingItemId.value = id;
  showConfirmDeleteModal.value = true;
};

const deleteItem = async () => {
  if (!deletingItemId.value) return;

  try {
    await shoppingListsAPI.deleteItem(deletingItemId.value); // DELETE /shopping-lists/items/{id}
    closeDeleteConfirm();
    await reloadActiveList();
  } catch (error) {
    console.error("Error deleting item:", error.response?.data || error);
  }
};

/* -----------------------------------------
   RESET / CLOSE HELPERS
----------------------------------------- */
const resetNewItem = () => ({
  ingredient_id: null,
  quantity: 1,
});

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

/* -----------------------------------------
   AI: GENERATE SHOPPING LIST SUGGESTIONS
----------------------------------------- */
const generateAIShoppingList = async () => {
  if (!ingredients.value.length) {
    aiSuggestions.value =
      "No ingredients found. Please add ingredients in your fridge first.";
    return;
  }

  const inventorySummary = ingredients.value
    .map((i) => `${i.name} (${i.quantity} ${i.unit})`)
    .join(", ");

  const question = `
You are a cooking assistant.

Here are the ingredients currently available in my fridge / pantry:

${inventorySummary}

Based on this, generate an optimized shopping list for 3 days (breakfast, lunch, dinner) for 1 person.
Reply STRICTLY in the following format, in English, with no additional explanation:

- category: item (quantity, unit)
- category: item (quantity, unit)

No text before or after, only the list itself.
  `.trim();

  aiLoading.value = true;
  aiSuggestions.value = null;

  try {
    const res = await aiAPI.ask(question);
    aiSuggestions.value = res.data["answer"] || res.data["réponse"] || "";
  } catch (error) {
    console.error("Error generating AI shopping list:", error);
    aiSuggestions.value =
      "Error while generating the shopping list with AI.";
  } finally {
    aiLoading.value = false;
  }
};

/* -----------------------------------------
   MOUNT
----------------------------------------- */
onMounted(async () => {
  await loadIngredients();
  await loadShoppingContext();
});
</script>

<template>
  <div class="px-4 py-6 sm:px-0 bg-gray-50 min-h-full">
    <!-- HEADER -->
    <div
      class="flex flex-col sm:flex-row justify-between items-center mb-4 border-b pb-4"
    >
      <h1 class="text-4xl font-bold text-gray-900">
        Shopping List
        <span v-if="shoppingList" class="text-lg text-gray-500 ml-2">
          ({{ shoppingList.name }})
        </span>
      </h1>

      <div class="flex flex-col sm:flex-row gap-3 mt-4 sm:mt-0">
        <button
          @click="generateAIShoppingList"
          class="flex items-center px-5 py-2 bg-indigo-600 text-white font-semibold rounded-md shadow hover:bg-indigo-700 transition duration-150 transform hover:scale-105"
        >
          AI List
        </button>

        <button
          @click="showCreateModal = true"
          class="flex items-center px-5 py-2 bg-primary-600 text-white font-semibold rounded-md shadow hover:bg-primary-700 transition duration-150 transform hover:scale-105"
        >
          Add Item
        </button>
      </div>
    </div>

    <!-- AI STATUS / RESULT -->
    <div v-if="aiLoading" class="text-center py-4 text-indigo-600 text-lg">
      The AI is preparing a shopping list adapted to your fridge...
    </div>

    <div
      v-if="aiSuggestions && !aiLoading"
      class="bg-white border border-indigo-200 p-4 rounded-lg shadow mb-6"
    >
      <h2 class="text-2xl font-bold text-indigo-700 mb-3">
        AI Suggested Shopping List
      </h2>
      <p class="whitespace-pre-line text-gray-800">
        {{ aiSuggestions }}
      </p>
    </div>

    <!-- LOADING / EMPTY STATES -->
    <div v-if="isLoading" class="text-center py-10 text-xl text-primary-600">
      Loading items...
    </div>

    <div
      v-else-if="!shoppingItems.length"
      class="text-center py-10 text-gray-500 italic text-lg bg-white rounded-lg shadow-md"
    >
      No items yet. Add one to get started!
    </div>

    <!-- ITEMS LIST -->
    <div v-else class="space-y-4">
      <div
        v-for="item in shoppingItems"
        :key="item.id"
        class="bg-white p-4 rounded-lg shadow hover:shadow-lg transition flex justify-between items-center"
      >
        <div>
          <h2 class="text-lg font-semibold text-gray-900">
            {{ item.item_name }}
          </h2>
          <p class="text-gray-600">
            Quantity: {{ item.quantity }} {{ item.unit }}
          </p>
        </div>
        <div class="flex space-x-2">
          <button
            @click="openEditModal(item)"
            class="text-primary-600 hover:text-primary-900 p-1 rounded-full hover:bg-primary-50 transition"
          >
            Edit
          </button>
          <button
            @click="openDeleteConfirm(item.id)"
            class="text-red-600 hover:text-red-900 p-1 rounded-full hover:bg-red-50 transition"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL: CREATE ITEM -->
    <Transition name="modal-fade">
      <div
        v-if="showCreateModal"
        class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50"
      >
        <div
          class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg transform transition-all"
        >
          <h3 class="text-2xl font-bold text-gray-900 mb-4">
            Add Item
          </h3>
          <form @submit.prevent="addItem" class="space-y-4">
            <div>
              <label class="block font-medium mb-1">Ingredient:</label>
              <select
                v-model="newItem.ingredient_id"
                class="w-full border p-2 rounded-md"
                required
              >
                <option value="" disabled>Select an ingredient</option>
                <option v-for="ing in ingredients" :key="ing.id" :value="ing.id">
                  {{ ing.name }} ({{ ing.unit }})
                </option>
              </select>
            </div>
            <div>
              <label class="block font-medium mb-1">Quantity:</label>
              <input
                v-model.number="newItem.quantity"
                type="number"
                min="1"
                class="w-full border p-2 rounded-md"
              />
            </div>
            <div class="flex justify-end space-x-2">
              <button
                type="button"
                @click="closeCreateModal"
                class="px-4 py-2 bg-gray-200 rounded-md"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-primary-600 text-white rounded-md"
              >
                Add
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- MODAL: EDIT ITEM -->
    <Transition name="modal-fade">
      <div
        v-if="showEditModal && editingItem"
        class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50"
      >
        <div
          class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg transform transition-all"
        >
          <h3 class="text-2xl font-bold text-gray-900 mb-4">
            Edit: {{ editingItem.item_name }}
          </h3>
          <form @submit.prevent="saveEditItem" class="space-y-4">
            <div>
              <label class="block font-medium mb-1">Item name:</label>
              <input
                v-model="editingItem.item_name"
                type="text"
                class="w-full border p-2 rounded-md"
                required
              />
            </div>
            <div>
              <label class="block font-medium mb-1">Quantity:</label>
              <input
                v-model.number="editingItem.quantity"
                type="number"
                min="1"
                class="w-full border p-2 rounded-md"
              />
            </div>
            <div>
              <label class="block font-medium mb-1">Unit:</label>
              <input
                v-model="editingItem.unit"
                type="text"
                class="w-full border p-2 rounded-md"
              />
            </div>
            <div class="flex justify-end space-x-2">
              <button
                type="button"
                @click="closeEditModal"
                class="px-4 py-2 bg-gray-200 rounded-md"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-primary-600 text-white rounded-md"
              >
                Save
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- MODAL: DELETE CONFIRM -->
    <Transition name="modal-fade">
      <div
        v-if="showConfirmDeleteModal"
        class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50"
      >
        <div
          class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md transform transition-all text-center"
        >
          <h3 class="text-xl font-bold text-gray-900 mb-4">
            Confirm deletion
          </h3>
          <p class="mb-6">
            Are you sure you want to delete this item?
          </p>
          <div class="flex justify-center space-x-4">
            <button
              @click="closeDeleteConfirm"
              class="px-4 py-2 bg-gray-200 rounded-md"
            >
              Cancel
            </button>
            <button
              @click="deleteItem"
              class="px-4 py-2 bg-red-600 text-white rounded-md"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>
