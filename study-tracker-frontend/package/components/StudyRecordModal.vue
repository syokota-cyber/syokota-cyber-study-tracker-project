<template>
  <Teleport to="body">
    <div v-if="isVisible" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">📚 学習記録詳細</h3>
          <button @click="closeModal" class="close-btn" title="閉じる">
            ✕
          </button>
        </div>
        
        <div class="modal-body" v-if="record">
          <div class="record-info">
            <div class="info-row">
              <label>タイトル:</label>
              <span class="title">{{ record.title }}</span>
            </div>
            
            <div class="info-row">
              <label>カテゴリ:</label>
              <span class="category-badge">{{ record.category }}</span>
            </div>
            
            <div class="info-row">
              <label>難易度:</label>
              <div class="difficulty-stars">
                <span 
                  v-for="i in 5" 
                  :key="i" 
                  :class="['star', i <= record.difficulty ? 'filled' : 'empty']"
                >
                  ★
                </span>
              </div>
            </div>
            
            <div class="info-row">
              <label>学習時間:</label>
              <span class="study-time">{{ formatStudyTime(record.study_time) }}</span>
            </div>
            
            <div class="info-row">
              <label>作成日:</label>
              <span class="date">{{ formatDate(record.created_at) }}</span>
            </div>
            
            <div class="info-row">
              <label>更新日:</label>
              <span class="date">{{ formatDate(record.updated_at) }}</span>
            </div>
            
            <div class="info-row content-row">
              <label>学習内容:</label>
              <div class="content">
                {{ record.content || '内容なし' }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="editRecord" class="edit-btn" title="この記録を編集">
            ✏️ 編集
          </button>
          <button @click="closeModal" class="close-modal-btn">
            閉じる
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import type { StudyRecord } from '@/types/studyRecord'

interface Props {
  isVisible: boolean
  record: StudyRecord | null
}

interface Emits {
  (e: 'close'): void
  (e: 'edit', record: StudyRecord): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const closeModal = () => {
  emit('close')
}

const editRecord = () => {
  if (props.record) {
    emit('edit', props.record)
  }
}

const formatStudyTime = (minutes: number): string => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  
  if (hours > 0) {
    return `${hours}時間${mins}分`
  }
  return `${mins}分`
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
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
  animation: fadeIn 0.3s ease-out;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease-out;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 24px;
}

.record-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.info-row label {
  font-weight: 600;
  color: #666;
  min-width: 80px;
  flex-shrink: 0;
}

.info-row .title {
  font-weight: 500;
  color: #333;
  font-size: 16px;
}

.category-badge {
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
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

.study-time {
  font-weight: 500;
  color: #666;
}

.date {
  color: #999;
  font-size: 14px;
}

.content-row {
  align-items: flex-start;
}

.content-row label {
  margin-top: 4px;
}

.content {
  background-color: #f9f9f9;
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid #1976d2;
  white-space: pre-wrap;
  line-height: 1.5;
  color: #333;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #eee;
}

.edit-btn, .close-modal-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.edit-btn {
  background-color: #1976d2;
  color: white;
}

.edit-btn:hover {
  background-color: #1565c0;
}

.close-modal-btn {
  background-color: #f5f5f5;
  color: #666;
}

.close-modal-btn:hover {
  background-color: #e0e0e0;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { 
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .info-row {
    flex-direction: column;
    gap: 8px;
  }
  
  .info-row label {
    min-width: auto;
  }
}
</style> 