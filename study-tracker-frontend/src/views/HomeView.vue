<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import StudyRecordList from '@/components/StudyRecordList.vue'
import StudyRecordForm from '@/components/StudyRecordForm.vue'
import type { StudyRecord } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

// リアクティブな状態
const showCreateForm = ref(false)
const showEditForm = ref(false)
const editingRecord = ref<StudyRecord | null>(null)
const recordListRef = ref<InstanceType<typeof StudyRecordList> | null>(null)

// フォームを閉じる
const closeForm = () => {
  showCreateForm.value = false
  showEditForm.value = false
  editingRecord.value = null
}

// 学習記録が保存された時の処理
const handleRecordSaved = (record: StudyRecord) => {
  console.log('handleRecordSaved が呼び出されました:', record)
  
  // 一覧を再読み込み
  if (recordListRef.value) {
    console.log('recordListRef.value が存在します')
    recordListRef.value.loadRecords()
  } else {
    console.log('recordListRef.value が null です')
  }
  
  // フォームを閉じる
  closeForm()
  
  // 成功メッセージを表示（将来的に実装）
  console.log('学習記録が保存されました:', record)
}

// 学習記録編集を開始
const startEdit = (record: StudyRecord) => {
  editingRecord.value = record
  showEditForm.value = true
}

// ログアウト処理
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <main class="home-view">
    <div class="container">
      <!-- ヘッダー -->
      <header class="app-header">
        <div class="header-content">
          <div class="header-left">
            <h1 class="app-title">📚 StudyTracker</h1>
            <p class="app-subtitle">学習進捗管理システム</p>
          </div>
          <div class="header-right">
            <div class="user-info">
              <span class="user-name">{{ authStore.currentUser?.full_name || 'ユーザー' }}</span>
              <button @click="handleLogout" class="logout-btn" title="ログアウト">
                🚪 ログアウト
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- メインコンテンツ -->
      <div class="main-content">
        <!-- 学習記録一覧 -->
        <div class="records-section">
          <StudyRecordList 
            ref="recordListRef"
            @record-saved="handleRecordSaved"
            @edit-record="startEdit"
          />
        </div>

        <!-- 新規作成ボタン -->
        <div class="create-section">
          <button 
            @click="showCreateForm = true"
            class="create-btn"
          >
            ➕ 新しい学習記録を作成
          </button>
        </div>
      </div>

      <!-- 作成・編集フォームモーダル -->
      <div v-if="showCreateForm || showEditForm" class="modal-overlay" @click="closeForm">
        <div class="modal-content" @click.stop>
          <StudyRecordForm
            :record="editingRecord"
            :is-editing="showEditForm"
            @close="closeForm"
            @saved="handleRecordSaved"
          />
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.home-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.app-header {
  margin-bottom: 40px;
  color: white;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.header-left {
  text-align: left;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
  background-color: rgba(255, 255, 255, 0.1);
  padding: 12px 20px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.user-name {
  font-weight: 500;
  font-size: 16px;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.app-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.app-subtitle {
  font-size: 1.1rem;
  margin: 0;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.main-content {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.records-section {
  padding: 0;
}

.create-section {
  padding: 20px;
  text-align: center;
  border-top: 1px solid #eee;
  background-color: #f9f9f9;
}

.create-btn {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
}

.create-btn:active {
  transform: translateY(0);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

/* レスポンシブデザイン */
@media (max-width: 768px) {
  .home-view {
    padding: 10px;
  }
  
  .app-title {
    font-size: 2rem;
  }
  
  .app-subtitle {
    font-size: 1rem;
  }
  
  .modal-content {
    max-width: 95vw;
    margin: 10px;
  }
}

@media (max-width: 480px) {
  .app-title {
    font-size: 1.8rem;
  }
  
  .create-btn {
    padding: 10px 20px;
    font-size: 14px;
  }
}
</style>
