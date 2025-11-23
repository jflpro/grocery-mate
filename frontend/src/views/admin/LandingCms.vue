<template>
  <div class="admin-landing">
    <header class="admin-landing__header">
      <h1>Landing page content</h1>
      <p class="subtitle">
        Admin view – edit the public homepage text (work in progress).
      </p>
    </header>

    <section class="admin-landing__content">
      <p>
        This is a placeholder for the Landing CMS. The API endpoints and form
        will be wired later.
      </p>
    </section>
  </div>
</template>

<script setup>
// no logic yet, placeholder view
</script>

<style scoped>
.admin-landing {
  max-width: 960px;
  margin: 2rem auto;
  padding: 2rem 1.5rem;
}

.admin-landing__header {
  margin-bottom: 1.5rem;
}

.admin-landing__header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}

.subtitle {
  color: #6b7280;
  font-size: 0.95rem;
}

.admin-landing__content {
  padding: 1.5rem;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  color: #111827;
  font-size: 0.95rem;
}
</style>
