<template>
  <div class="landing-page">
    <div class="overlay">
      <!-- Header -->
      <header class="landing-header">
        <h1 class="logo">GroceryMate</h1>
        <nav class="nav">
          <RouterLink to="/login" class="nav-link">Log in</RouterLink>
        </nav>
      </header>

      <!-- Hero section -->
      <main class="hero">
        <div class="hero-content">
          <h2>{{ content.hero_title }}</h2>
          <p>{{ content.hero_subtitle }}</p>
          <div class="hero-actions">
            <RouterLink to="/login" class="btn-primary">
              Get started
            </RouterLink>
            <RouterLink to="/register" class="btn-secondary">
              Create an account
            </RouterLink>
          </div>
        </div>
      </main>

      <!-- Features section (décalée vers le bas) -->
      <section class="section section-light section-top-offset">
        <div class="section-inner">
          <h3 class="section-title">Why GroceryMate?</h3>
          <div class="features-grid">
            <div class="feature-card">
              <h4>{{ content.feature1_title }}</h4>
              <p>{{ content.feature1_text }}</p>
            </div>
            <div class="feature-card">
              <h4>{{ content.feature2_title }}</h4>
              <p>{{ content.feature2_text }}</p>
            </div>
            <div class="feature-card">
              <h4>{{ content.feature3_title }}</h4>
              <p>{{ content.feature3_text }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- How it works section -->
      <section class="section section-dark">
        <div class="section-inner">
          <h3 class="section-title">How it works</h3>
          <ol class="steps-list">
            <li>
              <span class="step-badge">1</span>
              <div class="step-content">
                <h4>{{ content.how1_title }}</h4>
                <p>{{ content.how1_text }}</p>
              </div>
            </li>
            <li>
              <span class="step-badge">2</span>
              <div class="step-content">
                <h4>{{ content.how2_title }}</h4>
                <p>{{ content.how2_text }}</p>
              </div>
            </li>
            <li>
              <span class="step-badge">3</span>
              <div class="step-content">
                <h4>{{ content.how3_title }}</h4>
                <p>{{ content.how3_text }}</p>
              </div>
            </li>
          </ol>
        </div>
      </section>

      <!-- CTA band -->
      <section class="section section-cta">
        <div class="section-inner section-cta-inner">
          <div>
            <h3 class="section-title">{{ content.cta_title }}</h3>
            <p class="section-subtitle">
              {{ content.cta_subtitle }}
            </p>
          </div>
          <RouterLink to="/register" class="btn-primary">
            Create your free account
          </RouterLink>
        </div>
      </section>

      <!-- Footer -->
      <footer class="landing-footer">
        <p>© {{ currentYear }} GroceryMate. All rights reserved.</p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router';
import { ref, computed, onMounted } from 'vue';
import { landingAPI } from '@/services/api.js';

// état local avec fallback par défaut
const content = ref({
  hero_title: 'Smart Grocery Management',
  hero_subtitle:
    'Track your inventory, avoid waste, and plan your recipes with a simple, modern web app.',

  feature1_title: 'Real-time inventory',
  feature1_text: 'Know exactly what you have in your fridge and pantry, anytime.',

  feature2_title: 'Anti-waste by design',
  feature2_text: 'Track expiry dates and use ingredients before they go to waste.',

  feature3_title: 'Recipe-friendly',
  feature3_text: 'Link your ingredients to recipes and plan meals with confidence.',

  how1_title: 'Create your account',
  how1_text: 'Sign up in a few seconds and secure your personal space.',

  how2_title: 'Add your ingredients',
  how2_text:
    'Save what you already have at home: name, quantity, location, expiry date.',

  how3_title: 'Plan & shop smarter',
  how3_text: 'Build shopping lists and recipes based on your real inventory.',

  cta_title: 'Ready to take control of your kitchen?',
  cta_subtitle: 'Start with a simple account and keep your groceries under control.',
});

const currentYear = computed(() => new Date().getFullYear());

const isLoading = ref(false);
const loadError = ref(null);

const loadLandingContent = async () => {
  try {
    isLoading.value = true;
    loadError.value = null;

    const { data } = await landingAPI.getPublic();
    content.value = data;
  } catch (err) {
    console.error('❌ Error loading landing content:', err);
    loadError.value = 'Unable to load landing content.';
    // On garde les valeurs par défaut
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  loadLandingContent();
});
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  width: 100%;
  background-image: url("@/assets/landing/landing-background.png");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.overlay {
  min-height: 100vh;
  width: 100%;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  flex-direction: column;
}

.landing-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 3rem;
  color: #ffffff;
}

.logo {
  font-size: 1.6rem;
  font-weight: 700;
}

.nav {
  display: flex;
  gap: 1rem;
}

.nav-link {
  color: #ffffff;
  text-decoration: none;
  font-weight: 500;
}

.nav-link:hover {
  text-decoration: underline;
}

.hero {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 3rem;
}

.hero-content {
  max-width: 540px;
  color: #ffffff;
}

.hero-content h2 {
  font-size: 2.8rem;
  margin-bottom: 1rem;
}

.hero-content p {
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.9rem 1.8rem;
  border-radius: 999px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background: #22c55e;
  color: #0f172a;
}

.btn-primary:hover {
  background: #16a34a;
}

.btn-secondary {
  background: rgba(15, 23, 42, 0.7);
  color: #e5e7eb;
}

.btn-secondary:hover {
  background: rgba(15, 23, 42, 0.9);
}

.section {
  padding: 3rem 1.5rem;
}

.section-top-offset {
  margin-top: 4rem;
}

.section-light {
  background: rgba(15, 23, 42, 0.75);
  color: #e5e7eb;
}

.section-dark {
  background: rgba(15, 23, 42, 0.95);
  color: #e5e7eb;
}

.section-cta {
  background: rgba(15, 23, 42, 0.9);
  color: #e5e7eb;
}

.section-inner {
  max-width: 960px;
  margin: 0 auto;
}

.section-title {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.5rem;
}

.feature-card {
  background: rgba(15, 23, 42, 0.85);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.feature-card h4 {
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.feature-card p {
  font-size: 0.95rem;
  color: #cbd5f5;
}

.steps-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 1.2rem;
}

.steps-list li {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.step-badge {
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  background: #22c55e;
  color: #0f172a;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.step-content h4 {
  margin: 0 0 0.3rem 0;
  font-size: 1.05rem;
}

.step-content p {
  margin: 0;
  font-size: 0.95rem;
  color: #cbd5f5;
}

.section-cta-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.section-subtitle {
  margin-top: 0.3rem;
  font-size: 0.95rem;
  color: #cbd5f5;
}

.landing-footer {
  padding: 1rem 3rem;
  text-align: center;
  font-size: 0.85rem;
  color: #e5e7eb;
  background: rgba(15, 23, 42, 0.95);
}

@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .landing-header {
    padding: 1rem 1.5rem;
  }

  .hero {
    padding: 2rem 1.5rem;
  }

  .hero-content h2 {
    font-size: 2.1rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .section-cta-inner {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
