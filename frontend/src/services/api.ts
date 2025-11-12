/**
 * API service for chatbot backend
 */
import axios, { AxiosInstance } from 'axios';
import { config } from '../config';
import { authService } from './auth';

export interface ChatMessage {
  message: string;
  conversation_id?: string;
  system_prompt?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  timestamp: string;
}

export interface ChatHistoryItem {
  userId: string;
  conversationId: string;
  timestamp: number;
  userMessage: string;
  aiResponse: string;
  createdAt: string;
}

export interface HistoryResponse {
  history: ChatHistoryItem[];
  count: number;
}

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: config.apiEndpoint,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Add auth token to requests
    this.client.interceptors.request.use(async (config) => {
      const token = await authService.getAuthToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  /**
   * Send a chat message
   */
  async sendMessage(data: ChatMessage): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/chat', data);
    return response.data;
  }

  /**
   * Get chat history
   */
  async getHistory(conversationId?: string, limit: number = 50): Promise<HistoryResponse> {
    const params: any = { limit };
    if (conversationId) {
      params.conversation_id = conversationId;
    }
    const response = await this.client.get<HistoryResponse>('/history', { params });
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
