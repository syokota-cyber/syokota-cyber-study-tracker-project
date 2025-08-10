import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresGuest: true }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ],
})

// ナビゲーションガード
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 認証状態の初期化
  if (!authStore.isAuthenticated && authStore.isAuthenticated !== false) {
    await authStore.initializeAuth()
  }
  
  // 認証が必要なページ
  if (to.meta.requiresAuth) {
    if (authStore.isAuthenticated) {
      next()
    } else {
      next('/login')
    }
  }
  // ゲスト専用ページ（ログイン画面など）
  else if (to.meta.requiresGuest) {
    if (authStore.isAuthenticated) {
      next('/')
    } else {
      next()
    }
  }
  // その他のページ
  else {
    next()
  }
})

export default router
