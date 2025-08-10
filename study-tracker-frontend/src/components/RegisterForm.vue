<template>
  <div class="register-form">
    <div class="form-header">
      <h2>📝 新規登録</h2>
      <button @click="$emit('close')" class="close-btn" title="閉じる">✕</button>
    </div>

    <!-- エラーメッセージ -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="error = null" class="clear-error-btn">✕</button>
    </div>

    <!-- 成功メッセージ -->
    <div v-if="successMessage" class="success-message">
      <p>{{ successMessage }}</p>
    </div>

    <form @submit.prevent="handleRegister" class="form">
      <div class="form-group">
        <label for="fullName">氏名</label>
        <input 
          id="fullName"
          v-model="form.full_name"
          type="text"
          required
          placeholder="山田 太郎"
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label for="registerEmail">メールアドレス</label>
        <input 
          id="registerEmail"
          v-model="form.email"
          type="email"
          required
          placeholder="example@email.com"
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label for="registerPassword">パスワード</label>
        <input 
          id="registerPassword"
          v-model="form.password"
          type="password"
          required
          placeholder="8文字以上で入力"
          class="form-input"
          minlength="8"
        />
        <small class="form-help">パスワードは8文字以上で入力してください</small>
      </div>

      <div class="form-group">
        <label for="confirmPassword">パスワード（確認）</label>
        <input 
          id="confirmPassword"
          v-model="confirmPassword"
          type="password"
          required
          placeholder="パスワードを再入力"
          class="form-input"
        />
      </div>

      <div class="form-actions">
        <button 
          type="button" 
          @click="$emit('close')" 
          class="cancel-btn"
        >
          キャンセル
        </button>
        <button 
          type="submit" 
          :disabled="isLoading || !isFormValid"
          class="register-btn"
        >
          {{ isLoading ? '登録中...' : '登録' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const emit = defineEmits<{
  close: []
  registered: []
}>()

const authStore = useAuthStore()

// フォーム状態
const form = ref({
  full_name: '',
  email: '',
  password: ''
})

const confirmPassword = ref('')
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const isLoading = ref(false)

// フォームバリデーション
const isFormValid = computed(() => {
  return (
    form.value.full_name.trim() !== '' &&
    form.value.email.trim() !== '' &&
    form.value.password.length >= 8 &&
    form.value.password === confirmPassword.value
  )
})

// 登録処理
const handleRegister = async () => {
  if (!isFormValid.value) {
    error.value = '入力内容を確認してください'
    return
  }

  try {
    isLoading.value = true
    error.value = null
    
    await authStore.register({
      full_name: form.value.full_name,
      email: form.value.email,
      password: form.value.password
    })
    
    successMessage.value = '登録が完了しました！ログインしてください。'
    
    // 3秒後にモーダルを閉じる
    setTimeout(() => {
      emit('registered')
    }, 3000)
    
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登録に失敗しました'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-form {
  width: 100%;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.form-header h2 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #666;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: #f0f0f0;
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

.success-message {
  background-color: #e8f5e8;
  border: 1px solid #4caf50;
  color: #2e7d32;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.clear-error-btn {
  background: none;
  border: none;
  color: #c62828;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 6px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.form-input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.form-help {
  margin-top: 4px;
  color: #666;
  font-size: 12px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.cancel-btn {
  flex: 1;
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  padding: 12px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.register-btn {
  flex: 1;
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

.register-btn:hover:not(:disabled) {
  background-color: #5a6fd8;
}

.register-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
