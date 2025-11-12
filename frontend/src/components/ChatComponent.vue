<template>
  <div class="chat-component">
    <div class="chat-header">
      <div class="user-info">
        <span class="user-label">Logged in as:</span>
        <span class="user-email">{{ user?.username }}</span>
      </div>
      <button @click="$emit('signout')" class="signout-btn">Sign Out</button>
    </div>

    <div class="chat-window">
      <div class="messages-container" ref="messagesContainer">
        <div v-if="messages.length === 0" class="welcome-message">
          <h3>Welcome to Totally Rad Chatbot 9000!</h3>
          <p>Ask me anything. I'm powered by Claude on AWS Bedrock.</p>
          <div class="suggestions">
            <button @click="sendSuggestion('Tell me a joke')" class="suggestion-btn">
              Tell me a joke
            </button>
            <button @click="sendSuggestion('Explain quantum computing')" class="suggestion-btn">
              Explain quantum computing
            </button>
            <button @click="sendSuggestion('Write a haiku about coding')" class="suggestion-btn">
              Write a haiku
            </button>
          </div>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role]"
        >
          <div class="message-content">
            <div class="message-role">{{ msg.role === 'user' ? 'You' : 'Claude' }}</div>
            <div class="message-text">{{ msg.content }}</div>
            <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>

        <div v-if="loading" class="message assistant">
          <div class="message-content">
            <div class="message-role">Claude</div>
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="input-container">
        <form @submit.prevent="sendMessage" class="input-form">
          <textarea
            v-model="currentMessage"
            @keydown.enter.exact.prevent="sendMessage"
            placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
            class="message-input"
            rows="3"
            :disabled="loading"
          ></textarea>
          <button type="submit" class="send-btn" :disabled="!currentMessage.trim() || loading">
            Send
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue';
import { apiService } from '../services/api';

interface Props {
  user: any;
}

defineProps<Props>();
defineEmits(['signout']);

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const messages = ref<Message[]>([]);
const currentMessage = ref('');
const loading = ref(false);
const conversationId = ref<string>('');
const messagesContainer = ref<HTMLElement | null>(null);

onMounted(() => {
  // Could load chat history here if needed
});

async function sendMessage() {
  if (!currentMessage.value.trim() || loading.value) return;

  const userMessage = currentMessage.value.trim();
  messages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: new Date()
  });

  currentMessage.value = '';
  loading.value = true;

  scrollToBottom();

  try {
    const response = await apiService.sendMessage({
      message: userMessage,
      conversation_id: conversationId.value || undefined
    });

    conversationId.value = response.conversation_id;

    messages.value.push({
      role: 'assistant',
      content: response.response,
      timestamp: new Date(response.timestamp)
    });

    scrollToBottom();
  } catch (error: any) {
    console.error('Error sending message:', error);
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error processing your request. Please try again.',
      timestamp: new Date()
    });
  } finally {
    loading.value = false;
  }
}

function sendSuggestion(suggestion: string) {
  currentMessage.value = suggestion;
  sendMessage();
}

function formatTime(timestamp: Date): string {
  return new Date(timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

async function scrollToBottom() {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
}
</script>

<style scoped>
.chat-component {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 300px);
  min-height: 500px;
}

.chat-header {
  background: var(--card-bg);
  border: 2px solid var(--rad-purple);
  border-radius: 10px 10px 0 0;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(153, 69, 255, 0.3);
}

.user-info {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.user-label {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.user-email {
  color: var(--rad-cyan);
  font-weight: bold;
}

.signout-btn {
  background: linear-gradient(135deg, #ff0066, #ff6600);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.875rem;
  transition: all 0.3s;
}

.signout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(255, 0, 102, 0.4);
}

.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--card-bg);
  border: 2px solid var(--rad-purple);
  border-top: none;
  border-radius: 0 0 10px 10px;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: var(--darker-bg);
}

.messages-container::-webkit-scrollbar-thumb {
  background: var(--rad-purple);
  border-radius: 4px;
}

.welcome-message {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.welcome-message h3 {
  color: var(--rad-cyan);
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1.5rem;
}

.suggestion-btn {
  background: var(--darker-bg);
  border: 2px solid var(--rad-cyan);
  color: var(--rad-cyan);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.suggestion-btn:hover {
  background: var(--rad-cyan);
  color: var(--darker-bg);
  transform: translateY(-2px);
}

.message {
  display: flex;
  margin-bottom: 0.5rem;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 1rem;
  border-radius: 10px;
  position: relative;
}

.message.user .message-content {
  background: linear-gradient(135deg, var(--rad-purple), var(--rad-pink));
  border: 2px solid var(--rad-pink);
}

.message.assistant .message-content {
  background: var(--darker-bg);
  border: 2px solid var(--rad-cyan);
}

.message-role {
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
  letter-spacing: 0.1rem;
}

.message.user .message-role {
  color: var(--rad-yellow);
}

.message.assistant .message-role {
  color: var(--rad-cyan);
}

.message-text {
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message-time {
  font-size: 0.625rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 0.25rem;
  padding: 0.5rem 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--rad-cyan);
  border-radius: 50%;
  animation: bounce 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

.input-container {
  border-top: 2px solid var(--border-color);
  padding: 1rem;
  background: var(--darker-bg);
}

.input-form {
  display: flex;
  gap: 1rem;
}

.message-input {
  flex: 1;
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  color: var(--text-primary);
  padding: 0.75rem;
  font-size: 1rem;
  font-family: 'Courier New', monospace;
  border-radius: 5px;
  resize: none;
  transition: all 0.3s;
}

.message-input:focus {
  outline: none;
  border-color: var(--rad-cyan);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.message-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn {
  background: linear-gradient(135deg, var(--rad-purple), var(--rad-pink));
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  font-size: 1rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.1rem;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(153, 69, 255, 0.4);
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(153, 69, 255, 0.6);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .chat-component {
    height: calc(100vh - 250px);
  }

  .message-content {
    max-width: 85%;
  }

  .input-form {
    flex-direction: column;
    gap: 0.5rem;
  }

  .send-btn {
    width: 100%;
  }
}
</style>
