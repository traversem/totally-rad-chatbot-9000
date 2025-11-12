/**
 * Application configuration
 * This will be populated during deployment
 */

export interface AppConfig {
  apiEndpoint: string;
  userPoolId: string;
  userPoolClientId: string;
  region: string;
}

// Default config - will be replaced during build/deployment
export const config: AppConfig = {
  apiEndpoint: import.meta.env.VITE_API_ENDPOINT || '',
  userPoolId: import.meta.env.VITE_USER_POOL_ID || '',
  userPoolClientId: import.meta.env.VITE_USER_POOL_CLIENT_ID || '',
  region: import.meta.env.VITE_REGION || 'eu-west-1'
};
