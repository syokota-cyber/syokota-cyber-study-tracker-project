# StudyTracker Gitワークフロー

## 📋 文書情報

| 項目 | 内容 |
|------|------|
| プロジェクト名 | StudyTracker |
| 文書名 | Gitワークフロー |
| 版数 | v1.0 |
| 作成日 | 2025年7月22日 |
| 作成者 | 学習者 |
| 承認者 | - |

---

## 🎯 ワークフロー概要

### 採用するブランチ戦略
**Git Flow**をベースとしたワークフローを採用し、学習目的に最適化した運用を行います。

### ブランチ構成
```
main (本番環境)
├── develop (開発環境)
├── feature/機能名 (機能開発)
├── bugfix/バグ名 (バグ修正)
├── hotfix/緊急修正名 (緊急修正)
└── release/バージョン名 (リリース準備)
```

---

## 🌿 ブランチ命名規則

### メインブランチ
- **main**: 本番環境用の安定版
- **develop**: 開発環境用の統合版

### 作業ブランチ
- **feature/機能名**: 新機能開発
  - 例: `feature/study-record-crud`
  - 例: `feature/search-function`
- **bugfix/バグ名**: バグ修正
  - 例: `bugfix/fix-database-connection`
  - 例: `bugfix/resolve-api-error`
- **hotfix/緊急修正名**: 緊急修正
  - 例: `hotfix/security-patch`
  - 例: `hotfix/critical-bug-fix`
- **release/バージョン名**: リリース準備
  - 例: `release/v1.0.0`
  - 例: `release/v1.1.0`

### 命名規則
- **小文字**: すべて小文字を使用
- **ハイフン区切り**: 単語間はハイフンで区切る
- **説明的**: 機能や修正内容が分かりやすい名前
- **短縮**: 適度に短縮（50文字以内）

---

## 🔄 開発フロー

### 1. 機能開発フロー

#### 1.1 機能ブランチの作成
```bash
# developブランチから開始
git checkout develop
git pull origin develop

# 機能ブランチを作成
git checkout -b feature/study-record-crud
```

#### 1.2 開発・コミット
```bash
# 小さな変更を頻繁にコミット
git add .
git commit -m "feat: 学習記録の基本CRUD機能を実装

- StudyRecordモデルの作成
- データベース接続の実装
- 基本的なCRUD操作の実装"

# 複数のコミット例
git commit -m "feat: 学習記録作成機能を実装"
git commit -m "feat: 学習記録一覧表示機能を実装"
git commit -m "feat: 学習記録更新機能を実装"
git commit -m "feat: 学習記録削除機能を実装"
git commit -m "test: 学習記録CRUDのテストを追加"
```

#### 1.3 プルリクエストの作成
```bash
# 機能ブランチをプッシュ
git push origin feature/study-record-crud

# GitHubでプルリクエストを作成
# developブランチへのマージを要求
```

#### 1.4 コードレビュー・マージ
- プルリクエストのレビュー
- 必要に応じて修正
- developブランチへのマージ

### 2. バグ修正フロー

#### 2.1 バグ修正ブランチの作成
```bash
# developブランチから開始
git checkout develop
git pull origin develop

# バグ修正ブランチを作成
git checkout -b bugfix/fix-database-connection
```

#### 2.2 修正・コミット
```bash
# バグ修正
git add .
git commit -m "fix: データベース接続エラーを修正

- 接続タイムアウトの設定を追加
- エラーハンドリングを改善
- ログ出力を追加"
```

#### 2.3 プルリクエスト・マージ
- developブランチへのプルリクエスト
- レビュー・マージ

### 3. リリースフロー

#### 3.1 リリースブランチの作成
```bash
# developブランチから開始
git checkout develop
git pull origin develop

# リリースブランチを作成
git checkout -b release/v1.0.0
```

#### 3.2 リリース準備
```bash
# バージョン番号の更新
git commit -m "chore: バージョンを1.0.0に更新"

# 最終テスト・修正
git commit -m "fix: リリース前の最終修正"
```

#### 3.3 リリース完了
```bash
# mainブランチにマージ
git checkout main
git merge release/v1.0.0 --no-ff

# タグの作成
git tag -a v1.0.0 -m "Release version 1.0.0"

# developブランチにマージ
git checkout develop
git merge release/v1.0.0 --no-ff

# リリースブランチの削除
git branch -d release/v1.0.0
```

### 4. 緊急修正フロー

#### 4.1 緊急修正ブランチの作成
```bash
# mainブランチから開始
git checkout main
git pull origin main

# 緊急修正ブランチを作成
git checkout -b hotfix/security-patch
```

#### 4.2 修正・コミット
```bash
# 緊急修正
git add .
git commit -m "fix: セキュリティ脆弱性を修正

- 入力検証の強化
- SQLインジェクション対策の追加
- セキュリティテストの追加"
```

#### 4.3 緊急リリース
```bash
# mainブランチにマージ
git checkout main
git merge hotfix/security-patch --no-ff

# タグの作成
git tag -a v1.0.1 -m "Hotfix: Security patch"

# developブランチにマージ
git checkout develop
git merge hotfix/security-patch --no-ff

# 緊急修正ブランチの削除
git branch -d hotfix/security-patch
```

---

## 📝 コミットメッセージ規約

### Conventional Commits形式
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### タイプ
- **feat**: 新機能
- **fix**: バグ修正
- **docs**: ドキュメントのみの変更
- **style**: コードの意味に影響しない変更（空白、フォーマット等）
- **refactor**: バグ修正や機能追加ではないコードの変更
- **perf**: パフォーマンスを改善するコードの変更
- **test**: 不足しているテストの追加や既存のテストの修正
- **chore**: ビルドプロセスや補助ツールの変更

### 例
```bash
# 新機能
git commit -m "feat: 学習記録の検索機能を追加"

# バグ修正
git commit -m "fix: データベース接続エラーを修正"

# ドキュメント
git commit -m "docs: READMEを更新"

# リファクタリング
git commit -m "refactor: StudyRecordクラスをリファクタリング"

# テスト
git commit -m "test: 学習記録APIのテストを追加"

# 設定変更
git commit -m "chore: 依存関係を更新"
```

### 詳細なコミットメッセージ
```bash
git commit -m "feat: 学習記録の検索機能を追加

- タイトル・内容での全文検索機能
- カテゴリ別フィルタリング機能
- 期間別フィルタリング機能
- リアルタイム検索の実装

Closes #123"
```

---

## 🔍 プルリクエスト規約

### プルリクエストの作成
1. **タイトル**: 機能や修正内容を簡潔に記述
2. **説明**: 変更内容の詳細説明
3. **チェックリスト**: 完了した項目の確認
4. **スクリーンショット**: UI変更がある場合

### プルリクエストテンプレート
```markdown
## 変更内容
- 変更内容の概要

## 変更理由
- なぜこの変更が必要だったか

## 実装詳細
- どのように実装したか

## テスト
- [ ] ユニットテストを追加
- [ ] 統合テストを実行
- [ ] 手動テストを実行

## スクリーンショット
- UI変更がある場合

## 関連Issue
- Closes #123
```

### レビュー基準
- **コード品質**: 可読性、保守性
- **テスト**: 適切なテストの存在
- **ドキュメント**: 必要なドキュメントの更新
- **パフォーマンス**: 性能への影響
- **セキュリティ**: セキュリティ上の問題

---

## 🚫 禁止事項

### 絶対にやってはいけないこと
- **mainブランチへの直接コミット**
- **developブランチへの直接コミット**
- **大きな変更の一括コミット**
- **意味のないコミットメッセージ**
- **プルリクエストなしでのマージ**

### 避けるべきこと
- **長時間のブランチ運用**（1週間以上）
- **複数の機能を1つのブランチで開発**
- **コミットメッセージの日本語使用**
- **デバッグコードの残存**

---

## 🛠️ トラブルシューティング

### よくある問題と解決方法

#### 1. コンフリクトの解決
```bash
# コンフリクトの確認
git status

# コンフリクトファイルの編集
# コンフリクトマーカーの解決

# 解決後のコミット
git add .
git commit -m "fix: コンフリクトを解決"
```

#### 2. 間違ったブランチでの作業
```bash
# 現在の変更を一時保存
git stash

# 正しいブランチに切り替え
git checkout correct-branch

# 変更を復元
git stash pop
```

#### 3. コミットの取り消し
```bash
# 直前のコミットを取り消し（変更は保持）
git reset --soft HEAD~1

# 直前のコミットを完全に取り消し
git reset --hard HEAD~1

# 特定のコミットを取り消し
git revert <commit-hash>
```

#### 4. ブランチの復元
```bash
# 削除されたブランチの復元
git reflog
git checkout -b <branch-name> <commit-hash>
```

---

## 📊 品質管理

### コードレビュー
- **必須**: すべてのプルリクエストでレビュー
- **レビュアー**: 学習者自身（自己レビュー）
- **基準**: コード品質、テスト、ドキュメント

### 自動化
- **CI/CD**: GitHub Actionsによる自動テスト
- **コード品質**: Black、Flake8による自動チェック
- **テストカバレッジ**: 80%以上を維持

### メトリクス
- **コミット頻度**: 1日1回以上
- **ブランチ寿命**: 1週間以内
- **プルリクエストサイズ**: 300行以内

---

## 📚 学習目標

### Phase 1での目標
- [ ] Git Flowワークフローの完全理解
- [ ] プルリクエスト・レビューの実践
- [ ] コミットメッセージ規約の習得
- [ ] ブランチ戦略の実践

### 評価基準
- **理解度**: ワークフローの説明ができる
- **実践度**: 実際の開発でワークフローを活用
- **品質**: 適切なコミットメッセージ・プルリクエスト
- **効率**: 効率的なブランチ運用

---

## 📞 サポート

### 参考資料
- [Git公式ドキュメント](https://git-scm.com/doc)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)

### 質問・相談
- **技術的な質問**: GitHub Issues
- **ワークフローの相談**: 学習ログに記録
- **トラブルシューティング**: このドキュメントの該当セクション

---

## ✅ 承認

| 役割 | 名前 | 承認日 | 署名 |
|------|------|--------|------|
| プロジェクトマネージャー | 学習者 | 2025年7月22日 | - |
| 技術責任者 | AIアシスタント | 2025年7月22日 | - |

---

**文書バージョン**: v1.0  
**最終更新日**: 2025年7月22日 