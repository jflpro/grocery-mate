<script setup>
import { ref, onMounted } from "vue";
import { ingredientsAPI } from "@/services/api";

/* ---------------------------
   STATE
--------------------------- */
const ingredients = ref([]);
const isLoading = ref(false);

const showCreateModal = ref(false);
const showEditModal = ref(false);
const showConfirmDeleteModal = ref(false);

const categories = [
  "Vegetables",
  "Fruits",
  "Meat",
  "Fish",
  "Dairy",
  "Grains",
  "Snacks",
  "Drinks",
  "Other",
];

const locations = ["Fridge", "Freezer", "Pantry", "Other"];

const units = ["pcs", "kg", "g", "L", "ml", "pack"];

const newIngredient = ref({
  name: "",
  category: "Vegetables",
  location: "Fridge",
  quantity: 1,
  unit: "pcs",
  expiry_date: null, // string "YYYY-MM-DD" ou null
});

const editingIngredient = ref(null);
const deletingIngredientId = ref(null);

/* ---------------------------
   HELPERS
--------------------------- */
const normalizePayload = (ing) => {
  const payload = {
    name: ing.name?.trim(),
    category: ing.category || null,
    location: ing.location || null,
    quantity: Number(ing.quantity) || 0,
    unit: ing.unit || "pcs",
  };

  if (ing.expiry_date && ing.expiry_date !== "") {
    payload.expiry_date = ing.expiry_date; // HTML date input → "YYYY-MM-DD"
  }

  console.log("🔧 Normalized ingredient payload:", payload);
  return payload;
};

const resetNewIngredient = () => ({
  name: "",
  category: "Vegetables",
  location: "Fridge",
  quantity: 1,
  unit: "pcs",
  expiry_date: null,
});

/* ---------------------------
   LOADERS
--------------------------- */
const loadIngredients = async () => {
  isLoading.value = true;
  try {
    console.log("📥 Loading ingredients...");
    const res = await ingredientsAPI.getAll();
    console.log("📥 Ingredients loaded from API:", res.data);
    ingredients.value = res.data;
  } catch (error) {
    console.error("❌ Error while loading ingredients:", error);
  } finally {
    isLoading.value = false;
  }
};

/* ---------------------------
   CREATE
--------------------------- */
const createIngredient = async () => {
  if (!newIngredient.value.name.trim()) {
    console.warn("⚠️ Name is required, aborting create.");
    return;
  }

  try {
    const payload = normalizePayload(newIngredient.value);
    console.log("➡️ Creating ingredient with payload:", payload);
    const res = await ingredientsAPI.add(payload);
    console.log("✅ Ingredient created:", res.data);

    showCreateModal.value = false;
    newIngredient.value = resetNewIngredient();

    await loadIngredients();
  } catch (error) {
    console.error("❌ Error while creating ingredient:", error);
    alert("Error while creating ingredient. Check console for details.");
  }
};

/* ---------------------------
   EDIT
--------------------------- */
const openEditModal = (ing) => {
  editingIngredient.value = {
    ...ing,
    expiry_date: ing.expiry_date || null,
  };
  showEditModal.value = true;
};

const saveEditIngredient = async () => {
  if (!editingIngredient.value?.name?.trim()) return;

  try {
    const payload = normalizePayload(editingIngredient.value);
    console.log(
      `➡️ Updating ingredient ${editingIngredient.value.id} with payload:`,
      payload,
    );
    const res = await ingredientsAPI.update(editingIngredient.value.id, payload);
    console.log("✅ Ingredient updated:", res.data);

    showEditModal.value = false;
    editingIngredient.value = null;

    await loadIngredients();
  } catch (error) {
    console.error("❌ Error while updating ingredient:", error);
    alert("Error while updating ingredient. Check console for details.");
  }
};

/* ---------------------------
   DELETE
--------------------------- */
const openDeleteConfirm = (id) => {
  deletingIngredientId.value = id;
  showConfirmDeleteModal.value = true;
};

const deleteIngredient = async () => {
  if (!deletingIngredientId.value) return;
  try {
    console.log("🗑 Deleting ingredient id:", deletingIngredientId.value);
    await ingredientsAPI.delete(deletingIngredientId.value);

    showConfirmDeleteModal.value = false;
    deletingIngredientId.value = null;

    await loadIngredients();
  } catch (error) {
    console.error("❌ Error while deleting ingredient:", error);
    alert("Error while deleting ingredient. Check console for details.");
  }
};

/* ---------------------------
   CLOSE HELPERS
--------------------------- */
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

/* ---------------------------
   MOUNT
--------------------------- */
onMounted(async () => {
  await loadIngredients();
});
</script>

<template>
  <div class="px-4 py-6 sm:px-0 bg-gray-50 min-h-full">
    <!-- HEADER -->
    <div
      class="flex flex-col sm:flex-row justify-between items-center mb-8 border-b pb-4"
    >
      <h1 class="text-4xl font-bold text-gray-900">My Ingredients</h1>

      <button
        @click="showCreateModal = true"
        class="mt-4 sm:mt-0 px-5 py-2 bg-green-600 text-white rounded-md shadow hover:bg-green-700 transition transform hover:scale-105"
      >
        Add Ingredient
      </button>
    </div>

    <!-- LIST -->
    <div v-if="isLoading" class="text-center py-10 text-xl text-green-700">
      Loading ingredients...
    </div>

    <div
      v-else-if="!ingredients.length"
      class="text-center py-10 text-gray-500 italic text-lg bg-white rounded-lg shadow-md"
    >
      No ingredients yet. Add one to get started!
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="ing in ingredients"
        :key="ing.id"
        class="bg-white p-4 rounded-lg shadow hover:shadow-lg transition flex justify-between items-center"
      >
        <div>
          <h2 class="text-xl font-semibold text-gray-900">
            {{ ing.name }}
          </h2>
          <p class="text-gray-600 mt-1">
            {{ ing.category }} — {{ ing.location }}
          </p>
          <p class="text-gray-500 mt-1 text-sm">
            {{ ing.quantity }} {{ ing.unit }}
            <span v-if="ing.expiry_date"> • Expiry: {{ ing.expiry_date }}</span>
          </p>
        </div>

        <div class="flex space-x-2">
          <button
            @click="openEditModal(ing)"
            class="px-3 py-1 text-blue-600 hover:text-blue-900 bg-blue-50 rounded-md"
          >
            Edit
          </button>
          <button
            @click="openDeleteConfirm(ing.id)"
            class="px-3 py-1 text-red-600 hover:text-red-900 bg-red-50 rounded-md"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL CREATE -->
    <Transition name="modal-fade">
      <div
        v-if="showCreateModal"
        class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50"
      >
        <div
          class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg transform transition-all"
        >
          <h3 class="text-2xl font-bold text-gray-900 mb-4">
            Add Ingredient
          </h3>

          <form @submit.prevent="createIngredient" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">Name</label>
              <input
                v-model="newIngredient.name"
                type="text"
                required
                class="w-full border p-2 rounded-md"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Category</label>
              <select
                v-model="newIngredient.category"
                class="w-full border p-2 rounded-md"
              >
                <option
                  v-for="cat in categories"
                  :key="cat"
                  :value="cat"
                >
                  {{ cat }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Location</label>
              <select
                v-model="newIngredient.location"
                class="w-full border p-2 rounded-md"
              >
                <option
                  v-for="loc in locations"
                  :key="loc"
                  :value="loc"
                >
                  {{ loc }}
                </option>
              </select>
            </div>

            <div class="grid grid-cols-3 gap-4 items-end">
              <div class="col-span-2">
                <label class="block text-sm font-medium mb-1">Quantity</label>
                <input
                  v-model="newIngredient.quantity"
                  type="number"
                  min="0"
                  step="0.01"
                  class="w-full border p-2 rounded-md"
                />
              </div>
              <div class="col-span-1">
                <label class="block text-sm font-medium mb-1">Unit</label>
                <select
                  v-model="newIngredient.unit"
                  class="w-full border p-2 rounded-md"
                >
                  <option v-for="u in units" :key="u" :value="u">
                    {{ u }}
                  </option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">
                Expiry date (optional)
              </label>
              <input
                v-model="newIngredient.expiry_date"
                type="date"
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
                class="px-4 py-2 bg-green-600 text-white rounded-md"
              >
                Create
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- MODAL EDIT -->
    <Transition name="modal-fade">
      <div
        v-if="showEditModal && editingIngredient"
        class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50"
      >
        <div
          class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg transform transition-all"
        >
          <h3 class="text-2xl font-bold text-gray-900 mb-4">
            Edit Ingredient
          </h3>

          <form @submit.prevent="saveEditIngredient" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">Name</label>
              <input
                v-model="editingIngredient.name"
                type="text"
                required
                class="w-full border p-2 rounded-md"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Category</label>
              <select
                v-model="editingIngredient.category"
                class="w-full border p-2 rounded-md"
              >
                <option
                  v-for="cat in categories"
                  :key="cat"
                  :value="cat"
                >
                  {{ cat }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Location</label>
              <select
                v-model="editingIngredient.location"
                class="w-full border p-2 rounded-md"
              >
                <option
                  v-for="loc in locations"
                  :key="loc"
                  :value="loc"
                >
                  {{ loc }}
                </option>
              </select>
            </div>

            <div class="grid grid-cols-3 gap-4 items-end">
              <div class="col-span-2">
                <label class="block text-sm font-medium mb-1">Quantity</label>
                <input
                  v-model="editingIngredient.quantity"
                  type="number"
                  min="0"
                  step="0.01"
                  class="w-full border p-2 rounded-md"
                />
              </div>
              <div class="col-span-1">
                <label class="block text-sm font-medium mb-1">Unit</label>
                <select
                  v-model="editingIngredient.unit"
                  class="w-full border p-2 rounded-md"
                >
                  <option v-for="u in units" :key="u" :value="u">
                    {{ u }}
                  </option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">
                Expiry date (optional)
              </label>
              <input
                v-model="editingIngredient.expiry_date"
                type="date"
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
                class="px-4 py-2 bg-green-600 text-white rounded-md"
              >
                Save
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- MODAL DELETE -->
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
            Are you sure you want to delete this ingredient?
          </p>

          <div class="flex justify-center space-x-4">
            <button
              @click="closeDeleteConfirm"
              class="px-4 py-2 bg-gray-200 rounded-md"
            >
              Cancel
            </button>
            <button
              @click="deleteIngredient"
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
