# StudyTracker セットアップガイド

## 📋 文書情報

| 項目 | 内容 |
|------|------|
| プロジェクト名 | StudyTracker |
| 文書名 | セットアップガイド |
| 版数 | v1.0 |
| 作成日 | 2025年7月22日 |
| 作成者 | 学習者 |
| 承認者 | - |

---

## 🚀 クイックスタート

### 前提条件
- Python 3.11以上
- Git
- VS Code / Cursor
- GitHubアカウント

### 1. リポジトリのクローン
```bash
# リポジトリをクローン
git clone https://github.com/syokota-cyber/study-tracker-project-.git
cd study-tracker-project-

# 現在のディレクトリを確認
pwd
ls -la
```

### 2. 仮想環境の作成
```bash
# Python仮想環境を作成
python -m venv venv

# 仮想環境をアクティベート
# macOS/Linux
source venv/bin/activate

# Windows
# venv\Scripts\activate

# 仮想環境の確認
which python
python --version
```

### 3. 依存関係のインストール
```bash
# 依存関係をインストール
pip install -r requirements.txt

# インストール確認
pip list
```

### 4. 開発環境の設定
```bash
# Cursorでプロジェクトを開く
cursor .

# またはVS Codeで開く
code .
```

---

## 🛠️ 詳細セットアップ

### 開発環境の準備

#### Python環境
```bash
# Pythonバージョン確認
python --version

# pipの更新
pip install --upgrade pip

# 仮想環境ツールの確認
python -m venv --help
```

#### Git設定
```bash
# Git設定確認
git config --list

# 必要に応じて設定
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# SSH鍵の設定（推奨）
ssh-keygen -t ed25519 -C "your.email@example.com"
```

#### エディタ設定
```bash
# Cursorのインストール確認
cursor --version

# またはVS Codeのインストール確認
code --version
```

### プロジェクト構造の確認

#### ディレクトリ構造
```
study-tracker-project-/
├── README.md                    # プロジェクト概要
├── requirements.txt             # Python依存関係
├── .gitignore                   # Git除外ファイル
├── .cursorrules                 # Cursor設定
├── requirements/                # 要件定義・仕様書
│   ├── requirements.md         # 要件定義書
│   └── specification.md        # 技術仕様書
├── docs/                       # ドキュメント
│   └── setup.md               # このファイル
├── rules/                      # ルール・ガイドライン
│   └── git-workflow.md        # Gitワークフロー
├── plans/                      # 学習計画・スケジュール
│   └── phase1-plan.md         # Phase 1詳細計画
└── logs/                       # 学習ログ・進捗記録
    └── progress-tracker.md    # 進捗追跡
```

#### ファイルの確認
```bash
# プロジェクトファイルの確認
ls -la

# ドキュメントの確認
ls -la requirements/
ls -la docs/
ls -la rules/
ls -la plans/
ls -la logs/
```

### 開発ツールの設定

#### Cursor設定
1. **プロジェクトを開く**
   ```bash
   cursor .
   ```

2. **.cursorrulesファイルの確認**
   - プロジェクトルートに`.cursorrules`ファイルが存在することを確認
   - Cursorの設定で「Include .cursorrules file」をONに設定

3. **拡張機能の確認**
   - Python拡張機能
   - Git拡張機能
   - その他必要な拡張機能

#### VS Code設定（代替）
1. **プロジェクトを開く**
   ```bash
   code .
   ```

2. **推奨拡張機能**
   - Python
   - Git Graph
   - GitLens
   - Python Test Explorer
   - Black Formatter

### テスト環境の準備

#### テストツールのインストール
```bash
# テスト関連ツールのインストール
pip install pytest pytest-cov

# コード品質ツールのインストール
pip install black flake8

# インストール確認
pytest --version
black --version
flake8 --version
```

#### テスト設定
```bash
# pytest設定ファイルの作成
cat > pytest.ini << EOF
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=src --cov-report=html
EOF
```

---

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### Python環境の問題
```bash
# Pythonが見つからない場合
which python3
python3 --version

# 仮想環境がアクティベートされていない場合
echo $VIRTUAL_ENV
source venv/bin/activate
```

#### Gitの問題
```bash
# リポジトリの状態確認
git status
git remote -v

# 認証の問題
git config --global credential.helper store
```

#### 依存関係の問題
```bash
# 依存関係の再インストール
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# キャッシュのクリア
pip cache purge
```

#### Cursorの問題
```bash
# Cursorの再起動
cursor --disable-gpu

# 設定のリセット
# Cursorの設定から「Reset to Defaults」
```

### エラーログの確認
```bash
# Pythonエラーの詳細確認
python -v your_script.py

# pipエラーの詳細確認
pip install -v package_name

# Gitエラーの詳細確認
git --help
```

---

## 📊 セットアップ確認

### 確認チェックリスト
- [ ] Python 3.11以上がインストールされている
- [ ] Gitが設定されている
- [ ] リポジトリがクローンされている
- [ ] 仮想環境が作成・アクティベートされている
- [ ] 依存関係がインストールされている
- [ ] Cursor/VS Codeでプロジェクトが開ける
- [ ] .cursorrulesファイルが認識されている
- [ ] テストツールがインストールされている

### 動作確認
```bash
# 基本的な動作確認
python -c "print('StudyTracker Project Ready!')"

# Git動作確認
git status

# テスト環境確認
pytest --version

# コード品質ツール確認
black --version
flake8 --version
```

---

## 🎯 次のステップ

### 学習開始前の準備
1. **学習計画の確認**
   ```bash
   cat plans/phase1-plan.md
   ```

2. **進捗追跡の確認**
   ```bash
   cat logs/progress-tracker.md
   ```

3. **Gitワークフローの確認**
   ```bash
   cat rules/git-workflow.md
   ```

### Day 1の準備
1. **学習時間の確保**: 90分の確保
2. **環境の最終確認**: 上記チェックリストの確認
3. **学習開始**: 7月24日（明日）からの学習開始

---

## 📞 サポート

### 問題が発生した場合
1. **エラーメッセージの確認**: 詳細なエラーメッセージを記録
2. **GitHub Issues**: [GitHub Issues](https://github.com/syokota-cyber/study-tracker-project-/issues)で質問
3. **ドキュメント確認**: このファイルの該当セクションを確認
4. **学習ログ記録**: 問題と解決方法を学習ログに記録

### 参考資料
- [Python公式ドキュメント](https://docs.python.org/)
- [Git公式ドキュメント](https://git-scm.com/doc)
- [Cursor公式ドキュメント](https://cursor.sh/docs)
- [VS Code公式ドキュメント](https://code.visualstudio.com/docs)

---

## ✅ 承認

| 役割 | 名前 | 承認日 | 署名 |
|------|------|--------|------|
| プロジェクトマネージャー | 学習者 | 2025年7月22日 | - |
| 技術責任者 | AIアシスタント | 2025年7月22日 | - |

---

**このガイドに従って、StudyTrackerプロジェクトの開発環境を準備しましょう！** 🚀

**文書バージョン**: v1.0  
**最終更新日**: 2025年7月22日 