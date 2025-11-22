<script setup>
import { ref, onMounted } from "vue";
import { recipesAPI, ingredientsAPI, aiAPI } from "@/services/api.js";

/* -----------------------------------------
   STATE
----------------------------------------- */
const recipes = ref([]);
const ingredients = ref([]);
const isLoading = ref(false);

const showCreateModal = ref(false);
const showEditModal = ref(false);
const showConfirmDeleteModal = ref(false);

const newRecipe = ref({
  title: "",
  description: "",
  ingredient_ids: [], // selected inventory ingredient IDs for creation
});

const editingRecipe = ref(null);
const deletingRecipeId = ref(null);

/* -----------------------------------------
   HELPERS
----------------------------------------- */
// Normalize payload to match backend schema safely
const normalizeRecipePayload = (r) => ({
  title: r.title?.trim(),
  description: r.description?.trim() || null,

  // Simple use of description as instructions text
  instructions: r.description?.trim() || "",

  // Safe defaults
  prep_time: r.prep_time ?? 0,
  cook_time: r.cook_time ?? 0,
  servings: r.servings ?? 1,
  calories: r.calories ?? null,
  is_healthy: r.is_healthy ?? false,
  is_public: r.is_public ?? false,
});

// Build required_ingredients list from selected ingredient IDs (inventory)
const buildRequiredIngredientsFromIds = (ingredientIds) => {
  if (!Array.isArray(ingredientIds) || !ingredientIds.length) return [];

  return ingredientIds
    .map((id) => ingredients.value.find((i) => i.id === id))
    .filter(Boolean)
    .map((ing) => ({
      name: ing.name,
      quantity: ing.quantity ?? 1,
      unit: ing.unit || "",
    }));
};

// Map recipe.required_ingredients (backend) to inventory IDs when possible
const mapRecipeIngredientsToIds = (recipeIngredients) => {
  if (!Array.isArray(recipeIngredients)) return [];

  const byName = new Map(
    ingredients.value.map((ing) => [ing.name.toLowerCase(), ing]),
  );

  return recipeIngredients
    .map((ri) => byName.get(ri.name.toLowerCase()))
    .filter(Boolean)
    .map((ing) => ing.id);
};

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

const loadRecipes = async () => {
  isLoading.value = true;
  try {
    const res = await recipesAPI.getAll();
    recipes.value = (res.data || []).map((r) => ({
      ...r,
      // For UI convenience, expose ingredients as required_ingredients
      ingredients: r.required_ingredients || r.ingredients || [],
    }));
  } catch (error) {
    console.error("Error loading recipes:", error);
  } finally {
    isLoading.value = false;
  }
};

/* -----------------------------------------
   CREATE
----------------------------------------- */
const createRecipe = async () => {
  if (!newRecipe.value.title.trim()) return;

  try {
    const basePayload = normalizeRecipePayload(newRecipe.value);
    const required_ingredients = buildRequiredIngredientsFromIds(
      newRecipe.value.ingredient_ids,
    );

    const payload = {
      ...basePayload,
      required_ingredients,
    };

    await recipesAPI.add(payload);
    closeCreateModal();
    await loadRecipes();
  } catch (error) {
    console.error(
      "Error creating recipe:",
      error.response?.data || error.message || error,
    );
  }
};

/* -----------------------------------------
   EDIT
----------------------------------------- */
const openEditModal = (recipe) => {
  editingRecipe.value = {
    ...recipe,
    description: recipe.description || "",
    // Try to map required_ingredients names to inventory IDs for the multiselect
    ingredient_ids: mapRecipeIngredientsToIds(recipe.ingredients || []),
  };
  showEditModal.value = true;
};

const saveEditRecipe = async () => {
  if (!editingRecipe.value.title.trim()) return;

  try {
    // For now, we only update base fields; required_ingredients
    // are not updated by the backend update endpoint.
    const payload = normalizeRecipePayload(editingRecipe.value);

    await recipesAPI.update(editingRecipe.value.id, payload);
    closeEditModal();
    await loadRecipes();
  } catch (error) {
    console.error(
      "Error updating recipe:",
      error.response?.data || error.message || error,
    );
  }
};

/* -----------------------------------------
   DELETE
----------------------------------------- */
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
    console.error(
      "Error deleting recipe:",
      error.response?.data || error.message || error,
    );
  }
};

/* -----------------------------------------
   RESET / CLOSE HELPERS
----------------------------------------- */
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

/* -----------------------------------------
   AI : GENERATED RECIPE (DISPLAY)
----------------------------------------- */
const aiLoading = ref(false);
const aiGenerated = ref(null);

const generateAIRecipe = async () => {
  if (!ingredients.value.length) return;

  const ingredientNames = ingredients.value.map((i) => i.name).join(", ");

  aiLoading.value = true;
  aiGenerated.value = null;

  try {
    const res = await aiAPI.recipe(ingredientNames);
    // backend payload key kept in French: "recette"
    aiGenerated.value = res.data.recette;
  } catch (e) {
    console.error("Error with AI recipe:", e);
  } finally {
    aiLoading.value = false;
  }
};

/* -----------------------------------------
   AI : AUTO-FILL FORM
----------------------------------------- */
const autoFillFromAI = async () => {
  if (!ingredients.value.length) return;

  const ingredientNames = ingredients.value.map((i) => i.name).join(", ");

  aiLoading.value = true;

  try {
    const res = await aiAPI.recipe(ingredientNames);
    const text = res.data.recette || "";

    const lines = text
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);

    const title = lines.shift() || "AI Recipe";
    const description = lines.join(" ");

    showCreateModal.value = true;

    newRecipe.value.title = title;
    newRecipe.value.description = description;
    // Preselect all inventory ingredients by default
    newRecipe.value.ingredient_ids = ingredients.value.map((i) => i.id);
  } catch (e) {
    console.error("Error AI auto-fill:", e);
  } finally {
    aiLoading.value = false;
  }
};

/* -----------------------------------------
   MOUNT
----------------------------------------- */
onMounted(async () => {
  await loadIngredients();
  await loadRecipes();
});
</script>

<template>
  <div class="px-4 py-6 sm:px-0 bg-gray-50 min-h-full">
    <!-- HEADER -->
    <div
      class="flex flex-col sm:flex-row justify-between items-center mb-8 border-b pb-4"
    >
      <h1 class="text-4xl font-bold text-gray-900">My Recipes</h1>

      <div class="flex space-x-3 mt-4 sm:mt-0">
        <button
          @click="showCreateModal = true"
          class="px-5 py-2 bg-primary-600 text-white rounded-md shadow hover:bg-primary-700 transition transform hover:scale-105"
        >
          Add Recipe
        </button>

        <button
          @click="generateAIRecipe"
          class="px-5 py-2 bg-indigo-600 text-white rounded-md shadow hover:bg-indigo-700 transition transform hover:scale-105"
        >
          AI Recipe
        </button>

        <button
          @click="autoFillFromAI"
          class="px-5 py-2 bg-purple-600 text-white rounded-md shadow hover:bg-purple-700 transition transform hover:scale-105"
        >
          AI Auto-Fill
        </button>
      </div>
    </div>

    <!-- AI LOADING -->
    <div v-if="aiLoading" class="text-center py-6 text-indigo-600 text-xl">
      AI is generating a creative recipe...
    </div>

    <!-- AI RESULT -->
    <div
      v-if="aiGenerated && !aiLoading"
      class="bg-white border border-indigo-200 p-4 rounded-lg shadow my-6"
    >
      <h2 class="text-2xl font-bold text-indigo-700 mb-3">
        AI Generated Recipe
      </h2>
      <p class="whitespace-pre-line text-gray-700">
        {{ aiGenerated }}
      </p>
    </div>

    <!-- LIST OF RECIPES -->
    <div v-if="isLoading" class="text-center py-10 text-xl text-primary-600">
      Loading recipes...
    </div>

    <div
      v-else-if="!recipes.length"
      class="text-center py-10 text-gray-500 italic text-lg bg-white rounded-lg shadow-md"
    >
      No recipes yet. Add one to get started!
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="recipe in recipes"
        :key="recipe.id"
        class="bg-white p-4 rounded-lg shadow hover:shadow-lg transition"
      >
        <div class="flex justify-between items-start">
          <div>
            <h2 class="text-xl font-semibold text-gray-900">
              {{ recipe.title }}
            </h2>
            <p class="text-gray-600 mt-1">{{ recipe.description }}</p>

            <p class="text-gray-500 mt-2 text-sm">
              <span
                v-for="(ing, idx) in (recipe.ingredients || [])"
                :key="ing.id || `${ing.name}-${idx}`"
                class="inline-block bg-gray-100 text-gray-800 px-2 py-1 rounded-full mr-2 mb-1"
              >
                {{ ing.name }}
                <span v-if="ing.quantity">
                  ({{ ing.quantity }} {{ ing.unit || "" }})
                </span>
              </span>
            </p>
          </div>

          <div class="flex space-x-2">
            <button
              @click="openEditModal(recipe)"
              class="text-primary-600 hover:text-primary-900 p-1 rounded-full hover:bg-primary-50 transition"
            >
              Edit
            </button>

            <button
              @click="openDeleteConfirm(recipe.id)"
              class="text-red-600 hover:text-red-900 p-1 rounded-full hover:bg-red-50 transition"
            >
              Delete
            </button>
          </div>
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
            Add Recipe
          </h3>

          <form @submit.prevent="createRecipe" class="space-y-4">
            <input
              v-model="newRecipe.title"
              type="text"
              placeholder="Title"
              required
              class="w-full border p-2 rounded-md"
            />

            <textarea
              v-model="newRecipe.description"
              placeholder="Description"
              rows="3"
              class="w-full border p-2 rounded-md"
            ></textarea>

            <div>
              <label class="block font-medium mb-1">Ingredients (from inventory):</label>
              <select
                v-model="newRecipe.ingredient_ids"
                multiple
                class="w-full border p-2 rounded-md"
              >
                <option
                  v-for="ing in ingredients"
                  :key="ing.id"
                  :value="ing.id"
                >
                  {{ ing.name }} ({{ ing.quantity }} {{ ing.unit || "" }})
                </option>
              </select>
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
        v-if="showEditModal && editingRecipe"
        class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50"
      >
        <div
          class="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg transform transition-all"
        >
          <h3 class="text-2xl font-bold text-gray-900 mb-4">
            Edit: {{ editingRecipe.title }}
          </h3>

          <form @submit.prevent="saveEditRecipe" class="space-y-4">
            <input
              v-model="editingRecipe.title"
              type="text"
              required
              class="w-full border p-2 rounded-md"
            />

            <textarea
              v-model="editingRecipe.description"
              rows="3"
              class="w-full border p-2 rounded-md"
            ></textarea>

            <div>
              <label class="block font-medium mb-1">
                Ingredients (from inventory, currently informational for editing):
              </label>
              <select
                v-model="editingRecipe.ingredient_ids"
                multiple
                class="w-full border p-2 rounded-md"
              >
                <option
                  v-for="ing in ingredients"
                  :key="ing.id"
                  :value="ing.id"
                >
                  {{ ing.name }} ({{ ing.quantity }} {{ ing.unit || "" }})
                </option>
              </select>
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
            Are you sure you want to delete this recipe?
          </p>

          <div class="flex justify-center space-x-4">
            <button
              @click="closeDeleteConfirm"
              class="px-4 py-2 bg-gray-200 rounded-md"
            >
              Cancel
            </button>
            <button
              @click="deleteRecipe"
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
