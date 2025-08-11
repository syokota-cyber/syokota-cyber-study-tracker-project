<template>
  <div class="dashboard-view">
    <!-- ヘッダー -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div class="flex items-center">
            <h1 class="text-3xl font-bold text-gray-900">
              📚 StudyTracker
            </h1>
            <span class="ml-4 px-3 py-1 text-sm bg-green-100 text-green-800 rounded-full">
              学習進捗管理システム
            </span>
          </div>
          
          <!-- ユーザーメニュー -->
          <div class="flex items-center space-x-4">
            <div v-if="authStore.currentUser" class="text-sm text-gray-700">
              <span class="font-medium">{{ authStore.currentUser.full_name }}</span>
              <span class="mx-2">さん</span>
            </div>
            <button
              @click="handleLogout"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              ログアウト
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- メインコンテンツ -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <!-- 統計カード -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">
                    総学習記録数
                  </dt>
                  <dd class="text-lg font-medium text-gray-900">
                    {{ stats.total_records || 0 }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">
                    総学習時間
                  </dt>
                  <dd class="text-lg font-medium text-gray-900">
                    {{ stats.total_study_time || 0 }} 時間
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">
                    平均難易度
                  </dt>
                  <dd class="text-lg font-medium text-gray-900">
                    {{ stats.average_difficulty ? stats.average_difficulty.toFixed(1) : '0.0' }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 学習記録リスト -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-medium text-gray-900">
              学習記録
            </h2>
            <button
              @click="showCreateModal = true"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              新規記録
            </button>
          </div>

          <!-- 学習記録リストコンポーネント -->
          <StudyRecordList />
        </div>
      </div>
    </main>

    <!-- 新規記録作成モーダル -->
    <CreateRecordModal 
      v-if="showCreateModal" 
      :onClose="() => showCreateModal = false" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { apiService } from '@/services/api'
import StudyRecordList from '@/components/StudyRecordList.vue'
import CreateRecordModal from '@/components/CreateRecordModal.vue'

// ルーター
const router = useRouter()

// 認証ストア
const authStore = useAuthStore()

// 状態
const showCreateModal = ref(false)
const stats = ref({
  total_records: 0,
  total_study_time: 0,
  average_difficulty: 0
})

// 統計情報を取得
const fetchStats = async () => {
  try {
    const statsData = await apiService.getStudyStats()
    stats.value = statsData
  } catch (error) {
    console.error('統計情報取得エラー:', error)
  }
}

// ログアウト処理
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// コンポーネントマウント時
onMounted(() => {
  fetchStats()
})
</script>
