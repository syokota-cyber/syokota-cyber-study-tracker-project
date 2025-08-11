# GitHub通知設定の調整方法

## 📧 CI/CDパイプライン失敗メールの停止方法

### 問題の概要
StudyTrackerプロジェクトは学習目的で構築されており、CI/CDパイプラインの失敗メールが毎回届くことで開発効率が低下しています。

### 解決策

#### 1. CI/CDパイプラインの無効化（完了）
- **ファイル**: `.github/workflows/ci.yml`
- **変更内容**: 
  - `push`と`pull_request`トリガーを無効化
  - `workflow_dispatch`（手動実行）のみ有効化
  - 学習目的のプロジェクトであることを明記

#### 2. GitHub通知設定の調整

##### 方法1: リポジトリレベルでの通知設定
1. GitHubリポジトリページにアクセス
2. **Settings** → **Notifications** を選択
3. **Actions** セクションで以下を設定：
   - ✅ **Workflow runs**: チェックを外す
   - ✅ **Workflow run failures**: チェックを外す
   - ✅ **Workflow run successes**: チェックを外す

##### 方法2: アカウントレベルでの通知設定
1. GitHub右上のプロフィールアイコン → **Settings**
2. **Notifications** を選択
3. **Actions** セクションで以下を設定：
   - ✅ **Workflow runs**: チェックを外す
   - ✅ **Workflow run failures**: チェックを外す
   - ✅ **Workflow run successes**: チェックを外す

##### 方法3: メール通知の無効化
1. GitHub右上のプロフィールアイコン → **Settings**
2. **Notifications** → **Email notifications**
3. **Actions** のメール通知を無効化

#### 3. リポジトリのWatch設定調整
1. リポジトリページで **Watch** ボタンをクリック
2. **Custom** を選択
3. **Actions** のチェックを外す

### 推奨設定

#### 学習目的プロジェクトに適した通知設定
```yaml
# 推奨設定
Notifications:
  Actions:
    - Workflow runs: ❌ 無効
    - Workflow run failures: ❌ 無効
    - Workflow run successes: ❌ 無効
  
  Issues:
    - New issues: ✅ 有効（学習ログとして活用）
    - Issue comments: ✅ 有効
  
  Pull requests:
    - New pull requests: ✅ 有効
    - Pull request reviews: ✅ 有効
  
  Discussions:
    - New discussions: ✅ 有効
    - Discussion comments: ✅ 有効
```

### 手動でのCI/CD実行

#### 必要な場合の手動実行方法
1. GitHubリポジトリページにアクセス
2. **Actions** タブを選択
3. **CI/CD Pipeline (DISABLED)** ワークフローを選択
4. **Run workflow** ボタンをクリック
5. 必要に応じてブランチを選択して実行

### 代替案

#### 1. ローカルでのテスト実行
```bash
# コードフォーマットチェック
black --check --diff src/ tests/

# リンター実行
flake8 src/ tests/

# テスト実行
pytest tests/ --cov=src
```

#### 2. スクリプトでの自動化
```bash
# scripts/run-ci-local.sh
#!/bin/bash
echo "Running local CI checks..."

# フォーマットチェック
black --check --diff src/ tests/
if [ $? -ne 0 ]; then
    echo "❌ Code formatting check failed"
    exit 1
fi

# リンター
flake8 src/ tests/
if [ $? -ne 0 ]; then
    echo "❌ Linting failed"
    exit 1
fi

# テスト
pytest tests/ --cov=src
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

echo "✅ All checks passed!"
```

### 今後の方針

#### 学習目的プロジェクトのCI/CD戦略
1. **自動CI/CD**: 無効化（学習効率を優先）
2. **手動実行**: 必要に応じて手動で実行
3. **ローカルテスト**: 開発時の品質保証
4. **段階的デプロイ**: 学習効果を重視した手動デプロイ

#### メリット
- **学習効率向上**: 不要な通知による中断を防止
- **開発速度向上**: CI/CD待機時間の削除
- **学習効果最大化**: 実際の開発プロセスに集中

#### デメリット
- **品質チェック**: 手動での品質保証が必要
- **デプロイリスク**: 手動デプロイによるミスの可能性
- **チーム開発**: 複数人での開発時の調整が必要

### まとめ

学習目的のプロジェクトでは、CI/CDパイプラインの自動実行を無効化し、手動での品質保証を行うことで、学習効率を最大化できます。必要に応じて手動でCI/CDを実行し、ローカルでのテストを活用して品質を保証しましょう。
