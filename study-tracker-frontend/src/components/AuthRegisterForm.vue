<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- ヘッダー -->
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          新規アカウント作成
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          または
          <router-link
            to="/login"
            class="font-medium text-indigo-600 hover:text-indigo-500"
          >
            既存アカウントでログイン
          </router-link>
        </p>
      </div>

      <!-- 登録フォーム -->
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <!-- エラーメッセージ -->
        <div v-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">
                {{ error }}
              </h3>
            </div>
          </div>
        </div>

        <!-- 成功メッセージ -->
        <div v-if="successMessage" class="rounded-md bg-green-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-green-800">
                {{ successMessage }}
              </h3>
            </div>
          </div>
        </div>

        <!-- 氏名入力 -->
        <div>
          <label for="fullName" class="block text-sm font-medium text-gray-700">
            氏名
          </label>
          <div class="mt-1">
            <input
              id="fullName"
              v-model="form.full_name"
              name="fullName"
              type="text"
              autocomplete="name"
              required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="山田 太郎"
            />
          </div>
        </div>

        <!-- メールアドレス入力 -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">
            メールアドレス
          </label>
          <div class="mt-1">
            <input
              id="email"
              v-model="form.email"
              name="email"
              type="email"
              autocomplete="email"
              required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="your@email.com"
            />
          </div>
        </div>

        <!-- パスワード入力 -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">
            パスワード
          </label>
          <div class="mt-1">
            <input
              id="password"
              v-model="form.password"
              name="password"
              type="password"
              autocomplete="new-password"
              required
              minlength="8"
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="8文字以上で入力"
            />
          </div>
          <p class="mt-1 text-xs text-gray-500">
            パスワードは8文字以上で入力してください
          </p>
        </div>

        <!-- パスワード確認入力 -->
        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
            パスワード（確認）
          </label>
          <div class="mt-1">
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              name="confirmPassword"
              type="password"
              autocomplete="new-password"
              required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="パスワードを再入力"
            />
          </div>
          <p v-if="!passwordsMatch && confirmPassword" class="mt-1 text-xs text-red-500">
            パスワードが一致しません
          </p>
        </div>

        <!-- 登録ボタン -->
        <div>
          <button
            type="submit"
            :disabled="isLoading || !isFormValid"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ isLoading ? '登録中...' : 'アカウント作成' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// ルーター
const router = useRouter()

// 認証ストア
const authStore = useAuthStore()

// フォームデータ
const form = reactive({
  full_name: '',
  email: '',
  password: ''
})

// 確認用パスワード
const confirmPassword = ref('')

// 状態
const isLoading = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

// 計算プロパティ
const passwordsMatch = computed(() => {
  return form.password === confirmPassword.value
})

const isFormValid = computed(() => {
  return form.full_name.trim() !== '' &&
         form.email.trim() !== '' &&
         form.password.length >= 8 &&
         passwordsMatch.value
})

// 登録処理
const handleRegister = async () => {
  try {
    isLoading.value = true
    error.value = null
    successMessage.value = null
    
    if (!isFormValid.value) {
      error.value = 'フォームの入力内容を確認してください'
      return
    }
    
    await authStore.register({
      full_name: form.full_name,
      email: form.email,
      password: form.password
    })
    
    successMessage.value = 'アカウントが正常に作成されました。ログインページに移動します。'
    
    // 3秒後にログインページにリダイレクト
    setTimeout(() => {
      router.push('/login')
    }, 3000)
    
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登録に失敗しました'
  } finally {
    isLoading.value = false
  }
}
</script>
