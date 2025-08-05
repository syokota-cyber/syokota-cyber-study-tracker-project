<template>
  <div class="study-record-list">
    <div class="header">
      <h2 class="title">学習記録一覧</h2>
      <div class="header-actions">
        <!-- 一括削除ボタン -->
        <button 
          v-if="selectedRecords.length > 0"
          @click="deleteSelectedRecords" 
          class="bulk-delete-btn"
          title="選択した記録を一括削除"
        >
          🗑️ 選択削除 ({{ selectedRecords.length }})
        </button>
        <button 
          @click="loadRecords" 
          :disabled="loading"
          class="refresh-btn"
          title="一覧を更新"
        >
          {{ loading ? '読み込み中...' : '🔄 更新' }}
        </button>
      </div>
    </div>

    <!-- 検索・フィルタ機能 -->
    <div class="search-filter-section">
      <div class="search-box">
        <input 
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          placeholder="タイトルやカテゴリで検索..."
          class="search-input"
        />
        <button 
          @click="clearSearch"
          v-if="searchQuery"
          class="clear-search-btn"
          title="検索をクリア"
        >
          ✕
        </button>
      </div>
      
      <div class="filter-options">
        <select v-model="categoryFilter" @change="applyFilters" class="filter-select">
          <option value="">すべてのカテゴリ</option>
          <option value="バックエンド">バックエンド</option>
          <option value="フロントエンド">フロントエンド</option>
          <option value="データベース">データベース</option>
          <option value="インフラ">インフラ</option>
          <option value="その他">その他</option>
        </select>
        
        <select v-model="difficultyFilter" @change="applyFilters" class="filter-select">
          <option value="">すべての難易度</option>
          <option value="1">★☆☆☆☆ (初級)</option>
          <option value="2">★★☆☆☆ (初級〜中級)</option>
          <option value="3">★★★☆☆ (中級)</option>
          <option value="4">★★★★☆ (中級〜上級)</option>
          <option value="5">★★★★★ (上級)</option>
        </select>
      </div>
    </div>

    <!-- モーダルコンポーネントを追加 -->
    <StudyRecordModal
      :is-visible="showModal"
      :record="selectedRecord"
      @close="closeModal"
      @edit="handleEdit"
    />

    <!-- エラーメッセージ -->
    <div v-if="error" class="error-message">
      <p>エラーが発生しました: {{ error }}</p>
      <button @click="loadRecords" class="retry-btn">再試行</button>
    </div>

    <!-- ローディング表示 -->
    <div v-if="loading && (!records || records.length === 0)" class="loading">
      <p>学習記録を読み込み中...</p>
    </div>

    <!-- 検索結果が0件の場合 -->
    <div v-if="!loading && filteredRecords && filteredRecords.length === 0 && records && records.length > 0" class="no-results">
      <p>検索条件に一致する学習記録が見つかりませんでした。</p>
      <button @click="clearSearch" class="clear-filters-btn">フィルタをクリア</button>
    </div>

            <!-- 学習記録一覧 -->
        <div v-if="!loading && filteredRecords && filteredRecords.length > 0" class="records-container">
          <table class="records-table">
            <thead>
              <tr>
                <th class="select-header">
                  <input 
                    type="checkbox" 
                    :checked="selectedRecords.length === filteredRecords.length && filteredRecords.length > 0"
                    :indeterminate="selectedRecords.length > 0 && selectedRecords.length < filteredRecords.length"
                    @change="toggleAllSelection"
                    title="全選択/全解除"
                  />
                </th>
                <th>タイトル</th>
                <th>カテゴリ</th>
                <th>難易度</th>
                <th>学習時間</th>
                <th>作成日</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in filteredRecords" :key="record.id" class="record-row">
                <td class="select-cell">
                  <input 
                    type="checkbox" 
                    :checked="selectedRecords.includes(record.id)"
                    @change="toggleRecordSelection(record.id)"
                    title="この記録を選択"
                  />
                </td>
                <td class="title-cell">{{ record.title }}</td>
                <td class="category-cell">
                  <span class="category-badge">{{ record.category }}</span>
                </td>
                <td class="difficulty-cell">
                  <div class="difficulty-stars">
                    <span 
                      v-for="i in 5" 
                      :key="i" 
                      :class="['star', i <= record.difficulty ? 'filled' : 'empty']"
                    >
                      ★
                    </span>
                  </div>
                </td>
                <td class="time-cell">{{ formatStudyTime(record.study_time) }}</td>
                <td class="date-cell">{{ formatDate(record.created_at) }}</td>
                <td class="actions-cell">
                  <button 
                    @click="viewRecord(record)" 
                    class="action-btn view-btn"
                    title="詳細表示 - 学習記録の詳細情報を表示します"
                  >
                    👁️
                  </button>
                  <button 
                    @click="editRecord(record)" 
                    class="action-btn edit-btn"
                    title="編集 - 学習記録を編集します"
                  >
                    ✏️
                  </button>
                  <button 
                    @click="deleteRecord(record.id)" 
                    class="action-btn delete-btn"
                    title="削除 - この学習記録を削除します"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

      <!-- ページネーション -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="changePage(currentPage - 1)" 
          :disabled="currentPage <= 1"
          class="page-btn"
        >
          前へ
        </button>
        <span class="page-info">
          {{ currentPage }} / {{ totalPages }}
        </span>
        <button 
          @click="changePage(currentPage + 1)" 
          :disabled="currentPage >= totalPages"
          class="page-btn"
        >
          次へ
        </button>
      </div>
    </div>

    <!-- データがない場合 -->
    <div v-if="!loading && (!records || records.length === 0)" class="empty-state">
      <p>学習記録がありません</p>
      <p>新しい学習記録を作成してください</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, getCurrentInstance } from 'vue'
import { apiService, type StudyRecord } from '@/services/api'
import StudyRecordModal from './StudyRecordModal.vue'

// リアクティブな状態
const records = ref<StudyRecord[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const currentPage = ref(1)
const totalPages = ref(1)
const totalRecords = ref(0)
const limit = 10
const selectedRecords = ref<number[]>([])

// モーダル関連の状態
const showModal = ref(false)
const selectedRecord = ref<StudyRecord | null>(null)

// 検索・フィルタ関連の状態
const searchQuery = ref('')
const categoryFilter = ref('')
const difficultyFilter = ref('')
const filteredRecords = ref<StudyRecord[]>([])

// 学習記録一覧を取得
const loadRecords = async () => {
  console.log('loadRecords が呼び出されました')
  loading.value = true
  error.value = null
  
  try {
    const result = await apiService.getStudyRecords(currentPage.value, limit)
    console.log('API レスポンス:', result)
    console.log('result.records:', result.records)
    console.log('result.total:', result.total)
    records.value = result.records
    filteredRecords.value = result.records
    totalRecords.value = result.total
    totalPages.value = Math.ceil(result.total / limit)
    console.log('records.value が更新されました:', records.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '不明なエラーが発生しました'
    console.error('学習記録取得エラー:', err)
  } finally {
    loading.value = false
  }
}

// ページ変更
const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadRecords()
  }
}

// 学習記録削除
const deleteRecord = async (id: number) => {
  if (!confirm('この学習記録を削除しますか？')) {
    return
  }
  
  try {
    await apiService.deleteStudyRecord(id)
    // 削除後に一覧を再読み込み
    loadRecords()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '削除に失敗しました'
    console.error('学習記録削除エラー:', err)
  }
}

// 選択した記録を一括削除
const deleteSelectedRecords = async () => {
  if (selectedRecords.value.length === 0) {
    return
  }
  
  if (!confirm(`${selectedRecords.value.length}件の学習記録を削除しますか？`)) {
    return
  }
  
  try {
    // 並行して削除を実行
    await Promise.all(
      selectedRecords.value.map(id => apiService.deleteStudyRecord(id))
    )
    
    // 選択をクリア
    selectedRecords.value = []
    
    // 一覧を再読み込み
    loadRecords()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '一括削除に失敗しました'
    console.error('一括削除エラー:', err)
  }
}

// 記録の選択状態を切り替え
const toggleRecordSelection = (id: number) => {
  const index = selectedRecords.value.indexOf(id)
  if (index > -1) {
    selectedRecords.value.splice(index, 1)
  } else {
    selectedRecords.value.push(id)
  }
}

// 全選択/全解除
const toggleAllSelection = () => {
  if (selectedRecords.value.length === filteredRecords.value.length) {
    selectedRecords.value = []
  } else {
    selectedRecords.value = filteredRecords.value.map(record => record.id)
  }
}

// 学習記録詳細表示（モーダル版）
const viewRecord = (record: StudyRecord) => {
  selectedRecord.value = record
  showModal.value = true
}

// モーダルを閉じる
const closeModal = () => {
  showModal.value = false
  selectedRecord.value = null
}

// モーダルからの編集要求を処理
const handleEdit = (record: StudyRecord) => {
  closeModal()
  editRecord(record)
}

// 検索機能
const handleSearch = () => {
  applyFilters()
}

// 検索をクリア
const clearSearch = () => {
  searchQuery.value = ''
  applyFilters()
}

// フィルタを適用
const applyFilters = () => {
  let filtered = [...records.value]
  
  // 検索クエリでフィルタ
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(record => 
      record.title.toLowerCase().includes(query) ||
      record.category.toLowerCase().includes(query) ||
      record.content.toLowerCase().includes(query)
    )
  }
  
  // カテゴリでフィルタ
  if (categoryFilter.value) {
    filtered = filtered.filter(record => 
      record.category === categoryFilter.value
    )
  }
  
  // 難易度でフィルタ
  if (difficultyFilter.value) {
    filtered = filtered.filter(record => 
      record.difficulty === parseInt(difficultyFilter.value)
    )
  }
  
  filteredRecords.value = filtered
}

// 学習記録編集
const editRecord = (record: StudyRecord) => {
  console.log('編集ボタンがクリックされました:', record)
  
  // 親コンポーネントの編集関数を呼び出し
  const parent = getCurrentInstance()?.parent
  console.log('親コンポーネント:', parent)
  console.log('親コンポーネントのexposed:', parent?.exposed)
  
  if (parent && parent.exposed?.startEdit) {
    console.log('startEdit関数を呼び出します')
    parent.exposed.startEdit(record)
  } else {
    console.log('startEdit関数が見つかりません')
    // フォールバック: アラートで編集情報を表示
    alert(`編集機能の準備中です。\n\n編集したい記録:\nタイトル: ${record.title}\nカテゴリ: ${record.category}`)
  }
}

// 学習時間のフォーマット
const formatStudyTime = (minutes: number): string => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  
  if (hours > 0) {
    return `${hours}時間${mins}分`
  }
  return `${mins}分`
}

// 日付のフォーマット
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

// コンポーネントマウント時にデータを読み込み
onMounted(() => {
  loadRecords()
})

// 外部からアクセス可能な関数を公開
defineExpose({
  loadRecords
})
</script>

<style scoped>
.study-record-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-filter-section {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.search-box {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  position: relative;
}

.search-input {
  flex: 1;
  padding: 10px 40px 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.clear-search-btn {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  font-size: 16px;
  transition: background-color 0.2s;
}

.clear-search-btn:hover {
  background-color: #e0e0e0;
  color: #333;
}

.filter-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.filter-select:focus {
  outline: none;
  border-color: #1976d2;
}

.no-results {
  text-align: center;
  padding: 40px;
  color: #666;
}

.clear-filters-btn {
  margin-top: 12px;
  padding: 8px 16px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.clear-filters-btn:hover {
  background-color: #1565c0;
}

.title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.refresh-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn:hover {
  background-color: #45a049;
}

.refresh-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.bulk-delete-btn {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.bulk-delete-btn:hover {
  background-color: #d32f2f;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid #ffcdd2;
}

.retry-btn {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 8px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.records-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.records-table {
  width: 100%;
  border-collapse: collapse;
}

.records-table th {
  background-color: #f5f5f5;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #ddd;
}

.select-header {
  width: 40px;
  text-align: center;
}

.select-header input[type="checkbox"] {
  cursor: pointer;
}

.records-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.select-cell {
  width: 40px;
  text-align: center;
}

.select-cell input[type="checkbox"] {
  cursor: pointer;
}

.record-row:hover {
  background-color: #f9f9f9;
}

.title-cell {
  font-weight: 500;
  color: #333;
}

.category-badge {
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.difficulty-stars {
  display: flex;
  gap: 2px;
}

.star {
  font-size: 14px;
}

.star.filled {
  color: #ffc107;
}

.star.empty {
  color: #ddd;
}

.time-cell {
  font-weight: 500;
  color: #666;
}

.date-cell {
  color: #999;
  font-size: 14px;
}

.actions-cell {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  font-size: 16px;
  transition: background-color 0.2s;
}

.view-btn:hover {
  background-color: #e3f2fd;
}

.edit-btn:hover {
  background-color: #fff3e0;
}

.delete-btn:hover {
  background-color: #ffebee;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background-color: #f9f9f9;
}

.page-btn {
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background-color: #1976D2;
}

.page-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.page-info {
  font-weight: 500;
  color: #666;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-state p {
  margin: 8px 0;
  font-size: 16px;
}

.empty-state p:first-child {
  font-size: 18px;
  font-weight: 500;
  color: #333;
}
</style> 