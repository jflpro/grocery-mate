<template>
  <div class="max-w-5xl mx-auto py-8 px-4">
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Landing page content</h1>
      <p class="text-gray-600 text-sm">
        Admin view – edit the public homepage text.
      </p>
    </header>

    <!-- États globaux -->
    <div v-if="isLoading" class="mb-4 text-blue-600 text-sm">
      Loading landing content...
    </div>
    <div v-if="loadError" class="mb-4 text-red-600 text-sm">
      {{ loadError }}
    </div>
    <div v-if="saveSuccess" class="mb-4 text-green-600 text-sm">
      Changes saved successfully.
    </div>
    <div v-if="saveError" class="mb-4 text-red-600 text-sm">
      Error saving changes: {{ saveError }}
    </div>

    <form @submit.prevent="handleSave" class="space-y-8">
      <!-- HERO -->
      <section class="bg-white shadow rounded-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Hero section</h2>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Hero title
          </label>
          <input
            v-model="form.hero_title"
            type="text"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Hero subtitle
          </label>
          <textarea
            v-model="form.hero_subtitle"
            rows="3"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          ></textarea>
        </div>
      </section>

      <!-- FEATURES -->
      <section class="bg-white shadow rounded-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Features (3 cards)</h2>

        <!-- Feature 1 -->
        <div class="mb-4 border-b border-gray-200 pb-4">
          <h3 class="font-medium mb-2">Feature 1</h3>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Title
          </label>
          <input
            v-model="form.feature1_title"
            type="text"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm mb-2"
          />
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Text
          </label>
          <textarea
            v-model="form.feature1_text"
            rows="2"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          ></textarea>
        </div>

        <!-- Feature 2 -->
        <div class="mb-4 border-b border-gray-200 pb-4">
          <h3 class="font-medium mb-2">Feature 2</h3>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Title
          </label>
          <input
            v-model="form.feature2_title"
            type="text"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm mb-2"
          />
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Text
          </label>
          <textarea
            v-model="form.feature2_text"
            rows="2"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          ></textarea>
        </div>

        <!-- Feature 3 -->
        <div>
          <h3 class="font-medium mb-2">Feature 3</h3>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Title
          </label>
          <input
            v-model="form.feature3_title"
            type="text"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm mb-2"
          />
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Text
          </label>
          <textarea
            v-model="form.feature3_text"
            rows="2"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          ></textarea>
        </div>
      </section>

      <!-- HOW IT WORKS -->
      <section class="bg-white shadow rounded-lg p-6">
        <h2 class="text-xl font-semibold mb-4">How it works (3 steps)</h2>

        <!-- Step 1 -->
        <div class="mb-4 border-b border-gray-200 pb-4">
          <h3 class="font-medium mb-2">Step 1</h3>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Title
          </label>
          <input
            v-model="form.how1_title"
            type="text"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm mb-2"
          />
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Text
          </label>
          <textarea
            v-model="form.how1_text"
            rows="2"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          ></textarea>
        </div>

        <!-- Step 2 -->
        <div class="mb-4 border-b border-gray-200 pb-4">
          <h3 class="font-medium mb-2">Step 2</h3>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Title
          </label>
          <input
            v-model="form.how2_title"
            type="text"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm mb-2"
          />
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Text
          </label>
          <textarea
            v-model="form.how2_text"
            rows="2"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          ></textarea>
        </div>

        <!-- Step 3 -->
        <div>
          <h3 class="font-medium mb-2">Step 3</h3>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Title
          </label>
          <input
            v-model="form.how3_title"
            type="text"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm mb-2"
          />
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Text
          </label>
          <textarea
            v-model="form.how3_text"
            rows="2"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          ></textarea>
        </div>
      </section>

      <!-- CTA -->
      <section class="bg-white shadow rounded-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Call-to-Action</h2>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            CTA title
          </label>
          <input
            v-model="form.cta_title"
            type="text"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            CTA subtitle
          </label>
          <textarea
            v-model="form.cta_subtitle"
            rows="2"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          ></textarea>
        </div>
      </section>

      <!-- Actions -->
      <div class="flex justify-end gap-3">
        <button
          type="button"
          @click="reloadFromServer"
          class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Reset from server
        </button>
        <button
          type="submit"
          :disabled="isSaving"
          class="px-4 py-2 rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:opacity-60"
        >
          <span v-if="isSaving">Saving...</span>
          <span v-else>Save changes</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { landingAPI } from '@/services/api.js';

const form = ref({
  hero_title: '',
  hero_subtitle: '',
  feature1_title: '',
  feature1_text: '',
  feature2_title: '',
  feature2_text: '',
  feature3_title: '',
  feature3_text: '',
  how1_title: '',
  how1_text: '',
  how2_title: '',
  how2_text: '',
  how3_title: '',
  how3_text: '',
  cta_title: '',
  cta_subtitle: '',
});

const isLoading = ref(false);
const isSaving = ref(false);
const loadError = ref(null);
const saveError = ref(null);
const saveSuccess = ref(false);

const loadFromServer = async () => {
  try {
    isLoading.value = true;
    loadError.value = null;
    const { data } = await landingAPI.getAdmin();
    // on enlève l'id pour ne garder que les champs éditables
    const { id, ...rest } = data;
    form.value = { ...rest };
  } catch (err) {
    console.error('❌ Error loading admin landing content:', err);
    loadError.value = 'Unable to load landing content from server.';
  } finally {
    isLoading.value = false;
  }
};

const reloadFromServer = () => {
  loadFromServer();
};

const handleSave = async () => {
  saveError.value = null;
  saveSuccess.value = false;
  try {
    isSaving.value = true;
    await landingAPI.updateAdmin(form.value);
    saveSuccess.value = true;
  } catch (err) {
    console.error('❌ Error saving landing content:', err);
    saveError.value =
      err.response?.data?.detail || err.message || 'Unknown error';
  } finally {
    isSaving.value = false;
  }
};

onMounted(() => {
  loadFromServer();
});
</script>

<style scoped>
/* on garde un petit max-width déjà assuré par les classes Tailwind */
</style>
