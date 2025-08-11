<template>
  <footer class="bg-gray-800 text-white py-8 mt-auto">
    <div class="container mx-auto px-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- サービス情報 -->
        <div>
          <h3 class="text-lg font-semibold mb-4">StudyTracker</h3>
          <p class="text-gray-300 text-sm">
            個人の学習進捗管理・知識蓄積を目的とした学習支援ツールです。
          </p>
        </div>

        <!-- リンク -->
        <div>
          <h3 class="text-lg font-semibold mb-4">リンク</h3>
          <ul class="space-y-2 text-sm">
            <li>
              <a 
                href="https://github.com/syokota-cyber/syokota-cyber-study-tracker-project" 
                target="_blank" 
                rel="noopener noreferrer"
                class="text-gray-300 hover:text-white transition-colors"
              >
                GitHub プロジェクト
              </a>
            </li>
            <li>
              <a 
                href="/docs/terms-of-service" 
                class="text-gray-300 hover:text-white transition-colors"
              >
                利用規約
              </a>
            </li>
            <li>
              <a 
                href="/docs/privacy-policy" 
                class="text-gray-300 hover:text-white transition-colors"
              >
                プライバシーポリシー
              </a>
            </li>
          </ul>
        </div>

        <!-- お知らせ -->
        <div>
          <h3 class="text-lg font-semibold mb-4">お知らせ</h3>
          <div class="text-sm text-gray-300 space-y-2">
            <p>
              <span class="text-yellow-400 font-semibold">⚠️ 重要:</span>
              本サービスは学習目的で構築されており、商用サービスではありません。
            </p>
            <p>
              データの消失リスクを十分に理解した上でご利用ください。
            </p>
          </div>
        </div>
      </div>

      <!-- 著作権 -->
      <div class="border-t border-gray-700 mt-8 pt-8 text-center">
        <p class="text-gray-400 text-sm">
          © 2025 StudyTracker. All rights reserved.
        </p>
        <p class="text-gray-500 text-xs mt-2">
          学習目的のプロジェクトです。商用利用は想定していません。
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
// フッターコンポーネント
// 利用規約とプライバシーポリシーへのリンクを含む
</script>

<style scoped>
/* フッターのスタイル */
footer {
  margin-top: auto;
}
</style>
