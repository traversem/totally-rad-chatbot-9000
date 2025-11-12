/**
 * Authentication service using AWS Cognito
 */
import { Amplify } from 'aws-amplify';
import { signIn, signUp, signOut, confirmSignUp, getCurrentUser, fetchAuthSession } from 'aws-amplify/auth';
import { config } from '../config';

// Configure Amplify
Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: config.userPoolId,
      userPoolClientId: config.userPoolClientId,
      loginWith: {
        email: true
      }
    }
  }
});

export interface SignUpParams {
  email: string;
  password: string;
}

export interface SignInParams {
  email: string;
  password: string;
}

export interface ConfirmSignUpParams {
  email: string;
  code: string;
}

export const authService = {
  /**
   * Sign up a new user
   */
  async signUp({ email, password }: SignUpParams) {
    try {
      const { userId } = await signUp({
        username: email,
        password,
        options: {
          userAttributes: {
            email
          }
        }
      });
      return { success: true, userId };
    } catch (error: any) {
      console.error('Sign up error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Confirm sign up with verification code
   */
  async confirmSignUp({ email, code }: ConfirmSignUpParams) {
    try {
      await confirmSignUp({
        username: email,
        confirmationCode: code
      });
      return { success: true };
    } catch (error: any) {
      console.error('Confirm sign up error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Sign in existing user
   */
  async signIn({ email, password }: SignInParams) {
    try {
      const result = await signIn({
        username: email,
        password
      });
      return { success: true, result };
    } catch (error: any) {
      console.error('Sign in error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Sign out current user
   */
  async signOut() {
    try {
      await signOut();
      return { success: true };
    } catch (error: any) {
      console.error('Sign out error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Get current authenticated user
   */
  async getCurrentUser() {
    try {
      const user = await getCurrentUser();
      return { success: true, user };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  },

  /**
   * Get current auth session and JWT token
   */
  async getAuthToken() {
    try {
      const session = await fetchAuthSession();
      const token = session.tokens?.idToken?.toString();
      return token;
    } catch (error) {
      console.error('Get auth token error:', error);
      return null;
    }
  },

  /**
   * Check if user is authenticated
   */
  async isAuthenticated() {
    const result = await this.getCurrentUser();
    return result.success;
  }
};
