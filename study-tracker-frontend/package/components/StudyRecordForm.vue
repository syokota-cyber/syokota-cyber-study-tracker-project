<template>
  <div class="study-record-form">
    <div class="form-header">
      <h2 class="form-title">{{ isEditing ? '学習記録を編集' : '新しい学習記録を作成' }}</h2>
      <button @click="$emit('close')" class="close-btn">✕</button>
    </div>

    <form @submit.prevent="handleSubmit" class="form">
      <!-- タイトル -->
      <div class="form-group">
        <label for="title" class="form-label">タイトル *</label>
        <input
          id="title"
          v-model="form.title"
          type="text"
          class="form-input"
          :class="{ 'error': errors.title }"
          placeholder="学習内容のタイトルを入力"
          required
        />
        <span v-if="errors.title" class="error-message">{{ errors.title }}</span>
      </div>

      <!-- カテゴリ -->
      <div class="form-group">
        <label for="category" class="form-label">カテゴリ *</label>
        <select
          id="category"
          v-model="form.category"
          class="form-select"
          :class="{ 'error': errors.category }"
          required
        >
          <option value="">カテゴリを選択</option>
          <option value="プログラミング">プログラミング</option>
          <option value="バックエンド">バックエンド</option>
          <option value="フロントエンド">フロントエンド</option>
          <option value="データベース">データベース</option>
          <option value="インフラ">インフラ</option>
          <option value="デザイン">デザイン</option>
          <option value="その他">その他</option>
        </select>
        <span v-if="errors.category" class="error-message">{{ errors.category }}</span>
      </div>

      <!-- 難易度 -->
      <div class="form-group">
        <label class="form-label">難易度 *</label>
        <div class="difficulty-selector">
          <div
            v-for="level in 5"
            :key="level"
            @click="form.difficulty = level"
            :class="['difficulty-option', { 'selected': form.difficulty === level }]"
          >
            <span class="difficulty-stars">
              <span
                v-for="i in 5"
                :key="i"
                :class="['star', i <= level ? 'filled' : 'empty']"
              >
                ★
              </span>
            </span>
            <span class="difficulty-text">{{ getDifficultyText(level) }}</span>
          </div>
        </div>
        <span v-if="errors.difficulty" class="error-message">{{ errors.difficulty }}</span>
      </div>

      <!-- 学習時間 -->
      <div class="form-group">
        <label for="study-time" class="form-label">学習時間（分） *</label>
        <div class="time-input-group">
          <input
            id="study-time"
            v-model.number="form.study_time"
            type="number"
            min="1"
            max="1440"
            class="form-input time-input"
            :class="{ 'error': errors.study_time }"
            placeholder="学習時間を分で入力"
            required
          />
          <span class="time-hint">分（最大24時間）</span>
        </div>
        <span v-if="errors.study_time" class="error-message">{{ errors.study_time }}</span>
      </div>

      <!-- メモ -->
      <div class="form-group">
        <label for="content" class="form-label">メモ</label>
        <textarea
          id="content"
          v-model="form.content"
          class="form-textarea"
          :class="{ 'error': errors.content }"
          placeholder="学習内容の詳細や感想を記録"
          rows="4"
        ></textarea>
        <span v-if="errors.content" class="error-message">{{ errors.content }}</span>
      </div>

      <!-- フォームアクション -->
      <div class="form-actions">
        <button
          type="button"
          @click="$emit('close')"
          class="btn btn-secondary"
          :disabled="submitting"
        >
          キャンセル
        </button>
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="submitting"
        >
          {{ submitting ? '送信中...' : (isEditing ? '更新' : '作成') }}
        </button>
      </div>
    </form>

    <!-- エラーメッセージ -->
    <div v-if="submitError" class="submit-error">
      <p>エラーが発生しました: {{ submitError }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { apiService, type StudyRecord, type StudyRecordCreate, type StudyRecordUpdate } from '@/services/api'

// Props
interface Props {
  record?: StudyRecord | null
  isEditing?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  record: null,
  isEditing: false
})

// Emits
const emit = defineEmits<{
  close: []
  saved: [record: StudyRecord]
}>()

// フォームデータ
const form = reactive<StudyRecordCreate>({
  title: '',
  category: '',
  difficulty: 3,
  study_time: 60,
  content: ''
})

// フォームエラー
const errors = reactive<Partial<Record<keyof StudyRecordCreate, string>>>({})

// 送信状態
const submitting = ref(false)
const submitError = ref<string | null>(null)

// 編集モードの場合、既存データをフォームに設定
watch(() => props.record, (record) => {
  if (record && props.isEditing) {
    form.title = record.title
    form.category = record.category
    form.difficulty = record.difficulty
    form.study_time = record.study_time
    form.content = record.content
  }
}, { immediate: true })

// バリデーション
const validateForm = (): boolean => {
  // エラーをリセット
  Object.keys(errors).forEach(key => {
    delete errors[key as keyof StudyRecordCreate]
  })

  let isValid = true

  // タイトルバリデーション
  if (!form.title.trim()) {
    errors.title = 'タイトルは必須です'
    isValid = false
  } else if (form.title.length > 100) {
    errors.title = 'タイトルは100文字以内で入力してください'
    isValid = false
  }

  // カテゴリバリデーション
  if (!form.category) {
    errors.category = 'カテゴリを選択してください'
    isValid = false
  }

  // 難易度バリデーション
  if (form.difficulty < 1 || form.difficulty > 5) {
    errors.difficulty = '難易度を選択してください'
    isValid = false
  }

  // 学習時間バリデーション
  if (!form.study_time || form.study_time < 1) {
    errors.study_time = '学習時間は1分以上で入力してください'
    isValid = false
  } else if (form.study_time > 1440) {
    errors.study_time = '学習時間は24時間（1440分）以内で入力してください'
    isValid = false
  }

  // メモバリデーション
  if (form.content && form.content.length > 1000) {
    errors.content = 'メモは1000文字以内で入力してください'
    isValid = false
  }

  return isValid
}

// フォーム送信
const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  submitting.value = true
  submitError.value = null

  try {
    let result: StudyRecord

    if (props.isEditing && props.record) {
      // 更新
      const updateData: StudyRecordUpdate = {
        title: form.title,
        category: form.category,
        difficulty: form.difficulty,
        study_time: form.study_time,
        content: form.content
      }
      result = await apiService.updateStudyRecord(props.record.id, updateData)
    } else {
      // 作成
      const createData: StudyRecordCreate = {
        title: form.title,
        category: form.category,
        difficulty: form.difficulty,
        study_time: form.study_time,
        content: form.content
      }
      result = await apiService.createStudyRecord(createData)
    }

    // 成功時の処理
    console.log('StudyRecordForm: 保存成功、emit を実行:', result)
    emit('saved', result)
    emit('close')
  } catch (err) {
    submitError.value = err instanceof Error ? err.message : '保存に失敗しました'
    console.error('学習記録保存エラー:', err)
  } finally {
    submitting.value = false
  }
}

// 難易度テキスト取得
const getDifficultyText = (level: number): string => {
  const texts = ['', '初級', '初中級', '中級', '中上級', '上級']
  return texts[level] || ''
}
</script>

<style scoped>
.study-record-form {
  max-width: 600px;
  margin: 0 auto;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.form-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  padding: 4px;
  border-radius: 4px;
}

.close-btn:hover {
  background-color: #f5f5f5;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.form-input,
.form-select,
.form-textarea {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

.form-input.error,
.form-select.error,
.form-textarea.error {
  border-color: #f44336;
}

.error-message {
  color: #f44336;
  font-size: 12px;
  margin-top: 4px;
}

.difficulty-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.difficulty-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.difficulty-option:hover {
  background-color: #f9f9f9;
}

.difficulty-option.selected {
  border-color: #2196F3;
  background-color: #e3f2fd;
}

.difficulty-stars {
  display: flex;
  gap: 2px;
}

.star {
  font-size: 16px;
}

.star.filled {
  color: #ffc107;
}

.star.empty {
  color: #ddd;
}

.difficulty-text {
  font-weight: 500;
  color: #333;
}

.time-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-input {
  flex: 1;
}

.time-hint {
  color: #666;
  font-size: 12px;
  white-space: nowrap;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #2196F3;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1976D2;
}

.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.submit-error {
  margin-top: 16px;
  padding: 12px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  border: 1px solid #ffcdd2;
}

.submit-error p {
  margin: 0;
  font-size: 14px;
}
</style> 