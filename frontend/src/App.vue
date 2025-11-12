<template>
  <div id="app">
    <header class="app-header">
      <h1 class="app-title">
        <span class="totally">Totally</span>
        <span class="rad">Rad</span>
        <span class="chatbot">Chatbot</span>
        <span class="version">9000</span>
      </h1>
      <p class="tagline">Powered by Claude on AWS Bedrock • The Most Excellent AI Chat Experience</p>
    </header>

    <main class="app-main">
      <div v-if="!isAuthenticated" class="auth-container">
        <AuthComponent @authenticated="handleAuthenticated" />
      </div>

      <div v-else class="chat-container">
        <ChatComponent :user="currentUser" @signout="handleSignOut" />
      </div>
    </main>

    <footer class="app-footer">
      <p>&copy; 2025 Totally Rad Chatbot 9000 • Built with Vue 3 + TypeScript + AWS</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AuthComponent from './components/AuthComponent.vue';
import ChatComponent from './components/ChatComponent.vue';
import { authService } from './services/auth';

const isAuthenticated = ref(false);
const currentUser = ref<any>(null);

onMounted(async () => {
  await checkAuth();
});

async function checkAuth() {
  const result = await authService.getCurrentUser();
  if (result.success) {
    isAuthenticated.value = true;
    currentUser.value = result.user;
  }
}

function handleAuthenticated() {
  checkAuth();
}

async function handleSignOut() {
  await authService.signOut();
  isAuthenticated.value = false;
  currentUser.value = null;
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --rad-purple: #9945FF;
  --rad-pink: #FF00FF;
  --rad-cyan: #00FFFF;
  --rad-yellow: #FFFF00;
  --rad-green: #00FF00;
  --dark-bg: #1a1a2e;
  --darker-bg: #0f0f1e;
  --card-bg: #252545;
  --text-primary: #ffffff;
  --text-secondary: #b8b8d1;
  --border-color: #444466;
}

body {
  font-family: 'Courier New', monospace;
  background: linear-gradient(135deg, var(--dark-bg) 0%, var(--darker-bg) 100%);
  color: var(--text-primary);
  min-height: 100vh;
  background-attachment: fixed;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, var(--rad-purple), var(--rad-pink));
  padding: 2rem;
  text-align: center;
  border-bottom: 4px solid var(--rad-cyan);
  box-shadow: 0 4px 20px rgba(153, 69, 255, 0.5);
  position: relative;
  overflow: hidden;
}

.app-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    90deg,
    transparent,
    transparent 10px,
    rgba(255, 255, 255, 0.03) 10px,
    rgba(255, 255, 255, 0.03) 20px
  );
  pointer-events: none;
}

.app-title {
  font-size: 3rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.3rem;
  text-shadow:
    3px 3px 0 var(--rad-cyan),
    6px 6px 0 var(--rad-yellow),
    9px 9px 20px rgba(0, 0, 0, 0.5);
  margin-bottom: 0.5rem;
  animation: glow 2s ease-in-out infinite alternate;
  position: relative;
  z-index: 1;
}

.app-title span {
  display: inline-block;
  margin: 0 0.2rem;
}

.totally { color: #fff; }
.rad { color: var(--rad-cyan); }
.chatbot { color: var(--rad-yellow); }
.version {
  color: var(--rad-green);
  font-size: 2rem;
}

@keyframes glow {
  from {
    filter: drop-shadow(0 0 10px var(--rad-cyan));
  }
  to {
    filter: drop-shadow(0 0 20px var(--rad-pink));
  }
}

.tagline {
  font-size: 1rem;
  color: white;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
  font-weight: bold;
  position: relative;
  z-index: 1;
}

.app-main {
  flex: 1;
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

.auth-container,
.chat-container {
  width: 100%;
  max-width: 1200px;
}

.app-footer {
  background: var(--darker-bg);
  padding: 1rem;
  text-align: center;
  border-top: 2px solid var(--border-color);
  font-size: 0.875rem;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .app-title {
    font-size: 2rem;
  }

  .version {
    font-size: 1.5rem !important;
  }

  .app-header {
    padding: 1rem;
  }

  .app-main {
    padding: 1rem;
  }
}
</style>
