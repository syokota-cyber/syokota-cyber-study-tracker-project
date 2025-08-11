<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">📝 新規学習記録</h3>
        <button @click="closeModal" class="close-btn" title="閉じる">
          ✕
        </button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="handleSubmit" class="form">
          <!-- エラーメッセージ -->
          <div v-if="error" class="error-message">
            <p>{{ error }}</p>
            <button @click="error = null" class="clear-error-btn">✕</button>
          </div>

          <!-- タイトル -->
          <div class="form-group">
            <label for="title">タイトル *</label>
            <input 
              id="title"
              v-model="form.title"
              type="text"
              required
              placeholder="学習内容のタイトル"
              class="form-input"
            />
          </div>

          <!-- カテゴリ -->
          <div class="form-group">
            <label for="category">カテゴリ *</label>
            <select 
              id="category"
              v-model="form.category"
              required
              class="form-input"
            >
              <option value="">カテゴリを選択</option>
              <option value="プログラミング">プログラミング</option>
              <option value="数学">数学</option>
              <option value="英語">英語</option>
              <option value="物理">物理</option>
              <option value="化学">化学</option>
              <option value="歴史">歴史</option>
              <option value="地理">地理</option>
              <option value="文学">文学</option>
              <option value="その他">その他</option>
            </select>
          </div>

          <!-- 難易度 -->
          <div class="form-group">
            <label for="difficulty">難易度 *</label>
            <div class="difficulty-selector">
              <span 
                v-for="i in 5" 
                :key="i" 
                @click="form.difficulty = i"
                :class="['star', i <= form.difficulty ? 'filled' : 'empty']"
              >
                ★
              </span>
            </div>
            <p class="form-help">クリックして難易度を選択（1-5）</p>
          </div>

          <!-- 学習時間 -->
          <div class="form-group">
            <label for="studyTime">学習時間（時間） *</label>
            <input 
              id="studyTime"
              v-model.number="form.study_time"
              type="number"
              min="0.1"
              step="0.1"
              required
              placeholder="1.5"
              class="form-input"
            />
          </div>

          <!-- 学習内容 -->
          <div class="form-group">
            <label for="content">学習内容</label>
            <textarea 
              id="content"
              v-model="form.content"
              rows="4"
              placeholder="学習した内容や感想を記録..."
              class="form-input"
            ></textarea>
          </div>

          <!-- ボタン -->
          <div class="form-actions">
            <button 
              type="button" 
              @click="closeModal" 
              class="cancel-btn"
            >
              キャンセル
            </button>
            <button 
              type="submit" 
              :disabled="isLoading || !isFormValid"
              class="submit-btn"
            >
              {{ isLoading ? '作成中...' : '作成' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { apiService } from '@/services/api'
import type { StudyRecordCreate } from '@/services/api'

interface Props {
  onClose: () => void
}

const props = defineProps<Props>()

// フォームデータ
const form = reactive<StudyRecordCreate>({
  title: '',
  category: '',
  difficulty: 1,
  study_time: 1,
  content: ''
})

// 状態
const isLoading = ref(false)
const error = ref<string | null>(null)

// フォームバリデーション
const isFormValid = computed(() => {
  return form.title.trim() !== '' &&
         form.category !== '' &&
         form.difficulty >= 1 &&
         form.difficulty <= 5 &&
         form.study_time > 0
})

// モーダルを閉じる
const closeModal = () => {
  props.onClose()
}

// フォーム送信
const handleSubmit = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    if (!isFormValid.value) {
      error.value = 'フォームの入力内容を確認してください'
      return
    }
    
    await apiService.createStudyRecord(form)
    
    // 成功時はモーダルを閉じる
    closeModal()
    
    // ページをリロードして最新データを表示
    window.location.reload()
    
  } catch (err) {
    error.value = err instanceof Error ? err.message : '学習記録の作成に失敗しました'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  padding: 1rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #374151;
}

.form-input {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-help {
  font-size: 0.75rem;
  color: #6b7280;
}

.difficulty-selector {
  display: flex;
  gap: 0.25rem;
}

.star {
  font-size: 1.5rem;
  cursor: pointer;
  transition: color 0.2s;
}

.star.filled {
  color: #fbbf24;
}

.star.empty {
  color: #d1d5db;
}

.star:hover {
  color: #fbbf24;
}

.error-message {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  padding: 0.75rem;
  color: #dc2626;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.clear-error-btn {
  background: none;
  border: none;
  color: #dc2626;
  cursor: pointer;
  font-size: 1rem;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background-color: white;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
}

.cancel-btn:hover {
  background-color: #f9fafb;
}

.submit-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  background-color: #3b82f6;
  color: white;
  font-weight: 500;
  cursor: pointer;
}

.submit-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
