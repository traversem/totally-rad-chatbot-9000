<template>
  <div class="auth-component">
    <div class="auth-card">
      <h2 class="auth-title">{{ isSignUp ? 'Sign Up' : 'Sign In' }}</h2>

      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="success" class="success-message">{{ success }}</div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            v-model="email"
            required
            placeholder="your.email@example.com"
          />
        </div>

        <div v-if="!needsConfirmation" class="form-group">
          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            placeholder="••••••••"
          />
        </div>

        <div v-if="needsConfirmation" class="form-group">
          <label for="code">Verification Code</label>
          <input
            type="text"
            id="code"
            v-model="confirmationCode"
            required
            placeholder="Enter code from your email"
          />
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ buttonText }}
        </button>
      </form>

      <div class="auth-toggle">
        <button @click="toggleMode" class="toggle-btn">
          {{ isSignUp ? 'Already have an account? Sign In' : "Don't have an account? Sign Up" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { authService } from '../services/auth';

const emit = defineEmits(['authenticated']);

const email = ref('');
const password = ref('');
const confirmationCode = ref('');
const isSignUp = ref(false);
const needsConfirmation = ref(false);
const loading = ref(false);
const error = ref('');
const success = ref('');

const buttonText = computed(() => {
  if (loading.value) return 'Loading...';
  if (needsConfirmation.value) return 'Verify';
  return isSignUp.value ? 'Sign Up' : 'Sign In';
});

function toggleMode() {
  isSignUp.value = !isSignUp.value;
  needsConfirmation.value = false;
  error.value = '';
  success.value = '';
}

async function handleSubmit() {
  error.value = '';
  success.value = '';
  loading.value = true;

  try {
    if (needsConfirmation.value) {
      await handleConfirmation();
    } else if (isSignUp.value) {
      await handleSignUp();
    } else {
      await handleSignIn();
    }
  } finally {
    loading.value = false;
  }
}

async function handleSignUp() {
  const result = await authService.signUp({
    email: email.value,
    password: password.value
  });

  if (result.success) {
    success.value = 'Sign up successful! Check your email for verification code.';
    needsConfirmation.value = true;
    password.value = '';
  } else {
    error.value = result.error || 'Sign up failed';
  }
}

async function handleSignIn() {
  const result = await authService.signIn({
    email: email.value,
    password: password.value
  });

  if (result.success) {
    success.value = 'Sign in successful!';
    emit('authenticated');
  } else {
    error.value = result.error || 'Sign in failed';
  }
}

async function handleConfirmation() {
  const result = await authService.confirmSignUp({
    email: email.value,
    code: confirmationCode.value
  });

  if (result.success) {
    success.value = 'Email verified! You can now sign in.';
    needsConfirmation.value = false;
    isSignUp.value = false;
    confirmationCode.value = '';
  } else {
    error.value = result.error || 'Verification failed';
  }
}
</script>

<style scoped>
.auth-component {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.auth-card {
  background: var(--card-bg);
  border: 3px solid var(--rad-cyan);
  border-radius: 10px;
  padding: 2rem;
  width: 100%;
  max-width: 500px;
  box-shadow:
    0 0 20px rgba(0, 255, 255, 0.3),
    0 0 40px rgba(153, 69, 255, 0.2);
}

.auth-title {
  font-size: 2rem;
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--rad-cyan);
  text-transform: uppercase;
  letter-spacing: 0.2rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: var(--text-secondary);
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.875rem;
  letter-spacing: 0.1rem;
}

.form-group input {
  background: var(--darker-bg);
  border: 2px solid var(--border-color);
  color: var(--text-primary);
  padding: 0.75rem 1rem;
  font-size: 1rem;
  font-family: 'Courier New', monospace;
  border-radius: 5px;
  transition: all 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--rad-cyan);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

.submit-btn {
  background: linear-gradient(135deg, var(--rad-purple), var(--rad-pink));
  color: white;
  border: none;
  padding: 1rem 2rem;
  font-size: 1.125rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.1rem;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(153, 69, 255, 0.4);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(153, 69, 255, 0.6);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-toggle {
  margin-top: 1.5rem;
  text-align: center;
}

.toggle-btn {
  background: none;
  border: none;
  color: var(--rad-cyan);
  cursor: pointer;
  text-decoration: underline;
  font-size: 0.875rem;
  transition: color 0.3s;
}

.toggle-btn:hover {
  color: var(--rad-pink);
}

.error-message {
  background: rgba(255, 0, 0, 0.2);
  border: 2px solid #ff0000;
  color: #ff6666;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1rem;
  text-align: center;
}

.success-message {
  background: rgba(0, 255, 0, 0.2);
  border: 2px solid var(--rad-green);
  color: var(--rad-green);
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1rem;
  text-align: center;
}
</style>
