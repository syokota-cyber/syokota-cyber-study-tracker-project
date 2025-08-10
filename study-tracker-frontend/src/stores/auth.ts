// 認証状態管理ストア
// Piniaを使用した認証状態の管理

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService, type User, type LoginCredentials, type RegisterData, type AuthResponse } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状態
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 計算プロパティ
  const isLoggedIn = computed(() => isAuthenticated.value && user.value !== null)
  const currentUser = computed(() => user.value)

  // アクション
  const login = async (credentials: LoginCredentials) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await authService.login(credentials)
      isAuthenticated.value = true
      
      // ユーザー情報を取得
      await fetchCurrentUser()
      
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'ログインに失敗しました'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const testLogin = async () => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await authService.testLogin()
      isAuthenticated.value = true
      
      // テストユーザー情報を設定
      user.value = {
        id: response.user_id,
        email: 'test@example.com',
        full_name: 'テストユーザー',
        is_active: true,
        created_at: new Date().toISOString()
      }
      
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'テストログインに失敗しました'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData: RegisterData) => {
    try {
      isLoading.value = true
      error.value = null
      
      const newUser = await authService.register(userData)
      return newUser
    } catch (err) {
      error.value = err instanceof Error ? err.message : '登録に失敗しました'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    authService.logout()
    user.value = null
    isAuthenticated.value = false
    error.value = null
  }

  const fetchCurrentUser = async () => {
    try {
      if (!authService.isAuthenticated()) {
        return
      }
      
      const currentUser = await authService.getCurrentUser()
      user.value = currentUser
      isAuthenticated.value = true
    } catch (err) {
      console.error('ユーザー情報取得エラー:', err)
      // トークンが無効な場合はログアウト
      logout()
    }
  }

  const initializeAuth = async () => {
    try {
      if (authService.isAuthenticated()) {
        await fetchCurrentUser()
      }
    } catch (err) {
      console.error('認証初期化エラー:', err)
      logout()
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // 状態
    user,
    isAuthenticated,
    isLoading,
    error,
    
    // 計算プロパティ
    isLoggedIn,
    currentUser,
    
    // アクション
    login,
    testLogin,
    register,
    logout,
    fetchCurrentUser,
    initializeAuth,
    clearError
  }
})
