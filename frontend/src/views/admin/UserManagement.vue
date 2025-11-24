<template>
  <div class="px-4 py-6">
    <!-- Header -->
    <div class="mb-6">
      <h2 class="text-3xl font-bold text-gray-900">User Management</h2>
      <p class="text-gray-600">
        Manage all users and their permissions.
      </p>
    </div>

    <!-- Error message -->
    <div
      v-if="errorMessage"
      class="mb-4 rounded-md bg-red-50 p-4 text-sm text-red-700"
    >
      {{ errorMessage }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="py-10 text-center">
      <div
        class="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-primary-600"
      ></div>
      <p class="mt-4 text-gray-600">Loading users...</p>
    </div>

    <!-- Content -->
    <div v-else>
      <!-- Statistics Cards -->
      <div class="mb-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div class="overflow-hidden rounded-lg bg-white shadow">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <span class="text-3xl">👥</span>
              </div>
              <div class="ml-5 flex-1">
                <dl>
                  <dt class="truncate text-sm font-medium text-gray-500">
                    Total Users
                  </dt>
                  <dd class="text-2xl font-semibold text-gray-900">
                    {{ stats.total_users }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="overflow-hidden rounded-lg bg-white shadow">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <span class="text-3xl">✅</span>
              </div>
              <div class="ml-5 flex-1">
                <dl>
                  <dt class="truncate text-sm font-medium text-gray-500">
                    Active Users
                  </dt>
                  <dd class="text-2xl font-semibold text-gray-900">
                    {{ stats.active_users }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="overflow-hidden rounded-lg bg-white shadow">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <span class="text-3xl">🛡️</span>
              </div>
              <div class="ml-5 flex-1">
                <dl>
                  <dt class="truncate text-sm font-medium text-gray-500">
                    Admins
                  </dt>
                  <dd class="text-2xl font-semibold text-gray-900">
                    {{ stats.admin_users }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="overflow-hidden rounded-lg bg-white shadow">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <span class="text-3xl">🆕</span>
              </div>
              <div class="ml-5 flex-1">
                <dl>
                  <dt class="truncate text-sm font-medium text-gray-500">
                    New This Month
                  </dt>
                  <dd class="text-2xl font-semibold text-gray-900">
                    {{ stats.new_users_this_month }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Users Table -->
      <div class="overflow-hidden rounded-lg bg-white shadow">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                User
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                Status
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                Role
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                Joined
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                Last Login
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
            <tr v-for="user in users" :key="user.id">
              <td class="whitespace-nowrap px-6 py-4">
                <div>
                  <div class="text-sm font-medium text-gray-900">
                    {{ user.username }}
                  </div>
                  <div class="text-sm text-gray-500">
                    {{ user.email }}
                  </div>
                </div>
              </td>

              <td class="whitespace-nowrap px-6 py-4">
                <span
                  v-if="user.is_active"
                  class="inline-flex rounded-full bg-green-100 px-2 text-xs font-semibold leading-5 text-green-800"
                >
                  Active
                </span>
                <span
                  v-else
                  class="inline-flex rounded-full bg-red-100 px-2 text-xs font-semibold leading-5 text-red-800"
                >
                  Inactive
                </span>
              </td>

              <td class="whitespace-nowrap px-6 py-4">
                <span
                  v-if="user.is_admin"
                  class="inline-flex rounded-full bg-purple-100 px-2 text-xs font-semibold leading-5 text-purple-800"
                >
                  Admin
                </span>
                <span
                  v-else
                  class="inline-flex rounded-full bg-gray-100 px-2 text-xs font-semibold leading-5 text-gray-800"
                >
                  User
                </span>
              </td>

              <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                {{ formatDate(user.created_at) }}
              </td>

              <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                {{ user.last_login ? formatDate(user.last_login) : "Never" }}
              </td>

              <td
                class="whitespace-nowrap px-6 py-4 text-right text-sm font-medium"
              >
                <button
                  type="button"
                  class="mr-3 text-indigo-600 hover:text-indigo-900"
                  @click="toggleUserStatus(user)"
                >
                  {{ user.is_active ? "Deactivate" : "Activate" }}
                </button>

                <button
                  type="button"
                  class="mr-3 text-purple-600 hover:text-purple-900"
                  @click="toggleAdminStatus(user)"
                >
                  {{ user.is_admin ? "Remove Admin" : "Make Admin" }}
                </button>

                <button
                  type="button"
                  class="text-red-600 hover:text-red-900"
                  @click="confirmDelete(user)"
                >
                  Delete
                </button>
              </td>
            </tr>

            <tr v-if="users.length === 0">
              <td
                colspan="6"
                class="px-6 py-4 text-center text-sm text-gray-500"
              >
                No users found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";

const users = ref([]);
const stats = ref({
  total_users: 0,
  active_users: 0,
  admin_users: 0,
  new_users_this_month: 0,
});
const loading = ref(false);
const errorMessage = ref("");

const handleError = (error, fallbackMessage) => {
  if (error?.response?.status === 403) {
    errorMessage.value = "Not authorized. Admin access required.";
  } else {
    errorMessage.value =
      error?.response?.data?.detail || fallbackMessage || "Unexpected error.";
  }
};

const loadUsers = async () => {
  try {
    const response = await api.get("/admin/users", {
      params: { skip: 0, limit: 100 },
    });
    users.value = response.data;
  } catch (error) {
    console.error("Error loading users:", error);
    handleError(error, "Failed to load users.");
  }
};

const loadStats = async () => {
  try {
    const response = await api.get("/admin/users/stats");
    stats.value = response.data;
  } catch (error) {
    console.error("Error loading stats:", error);
    handleError(error, "Failed to load user statistics.");
  }
};

const reloadAll = async () => {
  loading.value = true;
  errorMessage.value = "";
  try {
    await Promise.all([loadUsers(), loadStats()]);
  } finally {
    loading.value = false;
  }
};

const toggleUserStatus = async (user) => {
  const newStatus = !user.is_active;
  try {
    await api.patch(`/admin/users/${user.id}`, {
      is_active: newStatus,
    });
    await reloadAll();
  } catch (error) {
    console.error("Error updating user status:", error);
    handleError(error, "Failed to update user status.");
  }
};

const toggleAdminStatus = async (user) => {
  const newStatus = !user.is_admin;
  try {
    await api.patch(`/admin/users/${user.id}`, {
      is_admin: newStatus,
    });
    await reloadAll();
  } catch (error) {
    console.error("Error updating user role:", error);
    handleError(error, "Failed to update user role.");
  }
};

const confirmDelete = async (user) => {
  const confirmed = window.confirm(
    `Are you sure you want to delete ${user.username}? This cannot be undone.`,
  );
  if (!confirmed) return;

  try {
    await api.delete(`/admin/users/${user.id}`);
    await reloadAll();
  } catch (error) {
    console.error("Error deleting user:", error);
    handleError(error, "Failed to delete user.");
  }
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

onMounted(() => {
  reloadAll();
});
</script>
