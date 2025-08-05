# StudyTracker エラーログ

## 概要
このファイルは、StudyTrackerプロジェクトで発生したエラーとその解決過程を記録します。

## 2025年7月31日 - フロントエンド開発エラー

### エラー1: `recordListRef.value.loadRecords is not a function`

#### 発生状況
- **日時**: 2025年7月31日
- **発生箇所**: `study-tracker-frontend/src/views/HomeView.vue`
- **エラーメッセージ**: `recordListRef.value.loadRecords is not a function`
- **ユーザーアクション**: 学習記録作成ボタンを押した時

#### エラー詳細
```javascript
// HomeView.vue の handleRecordSaved 関数内
const handleRecordSaved = (record: StudyRecord) => {
  // 一覧を再読み込み
  if (recordListRef.value) {
    recordListRef.value.loadRecords() // ← ここでエラー発生
  }
  // ...
}
```

#### 原因分析
1. **Vue 3 Composition API の仕様**: `<script setup>` では、関数は自動的に外部に公開されない
2. **defineExpose の未使用**: 子コンポーネントの関数を親から呼び出すには `defineExpose` が必要
3. **コンポーネント設計の問題**: 親子間の通信方法が適切に設計されていない

#### 解決方法
```typescript
// StudyRecordList.vue に追加
defineExpose({
  loadRecords
})
```

#### 修正ファイル
- `study-tracker-frontend/src/components/StudyRecordList.vue`

---

### エラー2: `TypeError: Cannot read properties of undefined (reading 'length')`

#### 発生状況
- **日時**: 2025年7月31日
- **発生箇所**: `study-tracker-frontend/src/components/StudyRecordList.vue`
- **エラーメッセージ**: `TypeError: Cannot read properties of undefined (reading 'length')`
- **発生タイミング**: コンポーネントのレンダリング時

#### エラー詳細
```vue
<!-- StudyRecordList.vue のテンプレート -->
<div v-if="loading && !records.length" class="loading">
<div v-if="!loading && records.length > 0" class="records-container">
<div v-if="!loading && !records.length" class="empty-state">
```

#### 原因分析
1. **初期化タイミング**: `records` が `ref<StudyRecord[]>([])` で初期化されるが、API呼び出し前に `undefined` になる可能性
2. **API エラー時**: API呼び出しが失敗した場合、`records` が適切に更新されない
3. **テンプレートの条件分岐**: `records.length` にアクセスする前に `records` の存在確認が必要

#### 解決方法
```vue
<!-- 修正後のテンプレート -->
<div v-if="loading && (!records || records.length === 0)" class="loading">
<div v-if="!loading && records && records.length > 0" class="records-container">
<div v-if="!loading && (!records || records.length === 0)" class="empty-state">
```

#### 修正ファイル
- `study-tracker-frontend/src/components/StudyRecordList.vue`

---

### エラー3: データ保存後の画面更新問題

#### 発生状況
- **日時**: 2025年7月31日
- **発生箇所**: 学習記録作成後の一覧表示
- **現象**: データは保存されるが画面が更新されない（TOPに戻る現象）
- **コンソールログ**: `学習記録が保存されました: {id: 75, title: 'vue', content: null, ...}`

#### エラー詳細
1. **データ保存**: バックエンドには正常に保存される
2. **画面更新**: フロントエンドの一覧が更新されない
3. **ユーザー体験**: 保存成功メッセージは表示されるが、一覧に反映されない

#### 原因分析
1. **defineExpose の配置問題**: 関数の定義順序が不適切
2. **フィールド名の不一致**: フロントエンドで `notes`、バックエンドで `content` を使用
3. **リアクティブデータの更新**: 一覧の再読み込みが正しく実行されない

#### 解決方法
1. **defineExpose の正しい配置**:
```typescript
onMounted(() => {
  loadRecords()
})

defineExpose({
  loadRecords
})
```

2. **フィールド名の統一**:
```typescript
// api.ts
export interface StudyRecord {
  content: string; // notes → content
}

// StudyRecordForm.vue
const form = reactive<StudyRecordCreate>({
  content: '' // notes → content
})
```

#### 修正ファイル
- `study-tracker-frontend/src/services/api.ts`
- `study-tracker-frontend/src/components/StudyRecordForm.vue`
- `study-tracker-frontend/src/components/StudyRecordList.vue`

---

## 技術的な学び

### Vue 3 Composition API
1. **defineExpose の重要性**: 子コンポーネントの関数を親から呼び出すには必須
2. **リアクティブデータの安全なアクセス**: `undefined` チェックが重要
3. **親子コンポーネント間の通信**: 適切な設計パターンの理解

### エラーハンドリング
1. **型安全性**: TypeScript での型チェックの重要性
2. **段階的なデバッグ**: エラーログの分析と原因特定
3. **ユーザー体験**: エラー時の適切なフィードバック

### データフロー
1. **フロントエンド・バックエンド間のデータ契約**: フィールド名の一貫性
2. **API通信**: エラー時の適切な処理
3. **状態管理**: リアクティブなデータ更新

## 次回の対策

### 予防策
1. **型定義の統一**: フロントエンド・バックエンド間でフィールド名を統一
2. **コンポーネント設計**: 親子間の通信方法を事前に設計
3. **エラーハンドリング**: 適切なエラー処理の実装

### デバッグ手法
1. **コンソールログ**: 詳細なログ出力
2. **段階的なテスト**: 小さな単位での動作確認
3. **ブラウザ開発者ツール**: Network タブでのAPI通信確認

---

**最終更新**: 2025年7月31日
**次回更新予定**: エラー発生時 