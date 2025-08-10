<template>
  <div class="login-view">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1 class="login-title">🔐 StudyTracker</h1>
          <p class="login-subtitle">学習進捗管理システム</p>
        </div>

        <!-- エラーメッセージ -->
        <div v-if="authStore.error" class="error-message">
          <p>{{ authStore.error }}</p>
          <button @click="authStore.clearError" class="clear-error-btn">✕</button>
        </div>

        <!-- テストログインセクション -->
        <div class="test-login-section">
          <h3>🚀 クイックスタート</h3>
          <p>開発・テスト用の簡単ログイン</p>
          <button 
            @click="handleTestLogin" 
            :disabled="authStore.isLoading"
            class="test-login-btn"
          >
            {{ authStore.isLoading ? 'ログイン中...' : '🔑 テストログイン' }}
          </button>
        </div>

        <div class="divider">
          <span>または</span>
        </div>

        <!-- 通常ログインフォーム -->
        <form @submit.prevent="handleLogin" class="login-form">
          <h3>📝 ユーザーログイン</h3>
          
          <div class="form-group">
            <label for="email">メールアドレス</label>
            <input 
              id="email"
              v-model="form.email"
              type="email"
              required
              placeholder="example@email.com"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="password">パスワード</label>
            <input 
              id="password"
              v-model="form.password"
              type="password"
              required
              placeholder="パスワードを入力"
              class="form-input"
            />
          </div>

          <button 
            type="submit" 
            :disabled="authStore.isLoading || !isFormValid"
            class="login-btn"
          >
            {{ authStore.isLoading ? 'ログイン中...' : 'ログイン' }}
          </button>
        </form>

        <!-- 登録リンク -->
        <div class="register-section">
          <p>アカウントをお持ちでない方は</p>
          <button @click="showRegister = true" class="register-link">
            新規登録
          </button>
        </div>
      </div>
    </div>

    <!-- 登録モーダル -->
    <div v-if="showRegister" class="modal-overlay" @click="showRegister = false">
      <div class="modal-content" @click.stop>
        <RegisterForm @close="showRegister = false" @registered="handleRegistered" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import RegisterForm from '@/components/RegisterForm.vue'

const router = useRouter()
const authStore = useAuthStore()

// フォーム状態
const form = ref({
  email: '',
  password: ''
})

// 登録モーダル表示状態
const showRegister = ref(false)

// フォームバリデーション
const isFormValid = computed(() => {
  return form.value.email.trim() !== '' && form.value.password.trim() !== ''
})

// テストログイン処理
const handleTestLogin = async () => {
  try {
    await authStore.testLogin()
    router.push('/')
  } catch (error) {
    console.error('テストログインエラー:', error)
  }
}

// 通常ログイン処理
const handleLogin = async () => {
  try {
    await authStore.login({
      email: form.value.email,
      password: form.value.password
    })
    router.push('/')
  } catch (error) {
    console.error('ログインエラー:', error)
  }
}

// 登録完了処理
const handleRegistered = () => {
  showRegister.value = false
  // 登録完了メッセージを表示（オプション）
}
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.login-subtitle {
  color: #666;
  font-size: 16px;
}

.error-message {
  background-color: #ffebee;
  border: 1px solid #f44336;
  color: #c62828;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.clear-error-btn {
  background: none;
  border: none;
  color: #c62828;
  cursor: pointer;
  font-size: 18px;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.test-login-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.test-login-section h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 18px;
}

.test-login-section p {
  margin: 0 0 16px 0;
  color: #666;
  font-size: 14px;
}

.test-login-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s;
}

.test-login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.test-login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.divider {
  text-align: center;
  margin: 30px 0;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background-color: #e0e0e0;
}

.divider span {
  background: white;
  padding: 0 16px;
  color: #666;
  font-size: 14px;
}

.login-form h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.login-btn {
  width: 100%;
  background-color: #667eea;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.login-btn:hover:not(:disabled) {
  background-color: #5a6fd8;
}

.login-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.register-section {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.register-section p {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
}

.register-link {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
}

.register-link:hover {
  color: #5a6fd8;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}
</style>
