# ナレッジ管理ツール - KnowledgeFlow

個人・小規模チーム向けのAI支援ナレッジ管理ツールです。URLやテキストを投入するだけで、AIが自動的に再利用可能なナレッジに変換します。

## 🚀 特徴

- **AI自動加工**: OpenAI GPT-4による高品質なナレッジ生成
- **ローカル動作**: データはローカルに保存、プライバシー保護
- **直感的UI**: シンプルで使いやすいWebインターフェース
- **多様な出力**: チェックリスト、サマリー、詳細レポートの生成
- **高速検索**: 全文検索とフィルタ機能

## 🏗️ アーキテクチャ

```
┌─────────────────┐
│   Web Browser   │
│   (Frontend UI) │
└─────────────────┘
         ↕ HTTP
┌──────────────────┐     ┌─────────────────┐
│   Go Main App    │     │  Python AI      │
│   - Web Server   │←───→│  Service        │
│   - Business     │HTTP │  - LangChain    │
│   - Database     │API  │  - OpenAI       │
└──────────────────┘     │  - Vector DB    │
         ↕               └─────────────────┘
┌─────────────────┐
│    SQLite       │
│   Main Database │
└─────────────────┘
```

## 🛠️ 技術スタック

- **Backend**: Go 1.21+ (Gin, GORM)
- **AI Service**: Python 3.11+ (FastAPI, LangChain, OpenAI)
- **Database**: SQLite 3.x
- **Frontend**: HTML + htmx + CSS
- **Container**: Docker + Docker Compose

## 📋 前提条件

- Docker 20.10+
- Docker Compose 2.0+
- 4GB以上のメモリ
- 2GB以上の空き容量

## 🚀 クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/ichiyama3ize/KnowledgeGlow.git
cd KnowledgeGlow
```

### 2. 環境設定

```bash
# 環境変数ファイルの作成
cp env.example .env

# API キーの設定
# .env ファイルを編集して OpenAI API キーを設定
```

### 3. 開発環境の起動

```bash
# 開発環境のセットアップ
make setup

# 環境の起動
make up

# ヘルスチェック
make health
```

### 4. アクセス

- **メインアプリケーション**: http://localhost:8080
- **データベース管理**: http://localhost:8081 (開発時のみ)

## 📖 使用方法

### 基本的な使い方

1. **ナレッジの作成**
   - URLまたはテキストを入力
   - AIが自動的に構造化・分類・要約
   - 生成結果を確認・編集

2. **ナレッジの検索**
   - キーワード検索
   - カテゴリ・日付・品質でのフィルタ
   - 関連ナレッジの自動提案

3. **エクスポート**
   - チェックリスト形式
   - サマリー形式
   - 詳細レポート形式

## 🛠️ 開発

### 開発環境の構築

```bash
# 依存関係のインストール
make build

# 開発環境の起動
make dev

# テストの実行
make test

# リンターの実行
make lint
```

### 利用可能なコマンド

```bash
make help          # 利用可能なコマンドを表示
make setup         # 開発環境の初期セットアップ
make build         # Docker イメージをビルド
make up            # 開発環境を起動
make down          # 環境を停止
make logs          # ログを表示
make test          # テストを実行
make lint          # リンターを実行
make format        # コードをフォーマット
make clean         # 環境をクリーンアップ
```

### プロジェクト構造

```
KnowledgeGlow/
├── go-app/                 # Go メインアプリケーション
│   ├── Dockerfile
│   ├── go.mod
│   ├── main.go
│   ├── handlers/           # HTTP ハンドラー
│   ├── models/             # データモデル
│   ├── services/           # ビジネスロジック
│   └── templates/          # HTML テンプレート
├── ai-service/             # Python AIサービス
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── processors/         # AI処理ロジック
│   ├── chains/             # LangChain設定
│   └── utils/              # ユーティリティ
├── config/                 # 設定ファイル
│   ├── nginx.conf
│   ├── prometheus.yml
│   └── loki.yml
├── data/                   # データファイル
├── logs/                   # ログファイル
├── exports/                # エクスポートファイル
├── docker-compose.yml      # Docker Compose設定
├── Makefile               # 開発用コマンド
└── README.md              # このファイル
```

## 🔧 設定

### 環境変数

主要な環境変数は以下の通りです：

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Claude API Configuration (Optional)
CLAUDE_API_KEY=sk-ant-your-claude-api-key-here

# Application Configuration
KNOWLEDGE_APP_PORT=8080
AI_SERVICE_PORT=8001

# Database Configuration
DATABASE_PATH=./data/knowledge.db

# Logging Configuration
LOG_LEVEL=INFO
```

### 設定ファイル

- `config/config.yaml`: アプリケーション設定
- `config/nginx.conf`: Nginx設定（本番環境用）
- `config/prometheus.yml`: Prometheus設定（監視用）

## 📊 監視・ログ

### 監視ダッシュボード

```bash
# 監視環境の起動
make monitoring

# アクセス
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

### ログの確認

```bash
# 全ログの表示
make logs

# 特定サービスのログ
make logs-go    # Go アプリケーション
make logs-ai    # Python AIサービス
```

## 🔒 セキュリティ

- データはローカルに保存
- API キーは環境変数で管理
- HTTPS通信（本番環境）
- 入力検証・サニタイゼーション

## 🧪 テスト

```bash
# 全テストの実行
make test

# 特定のテスト
docker-compose exec go-app go test ./handlers
docker-compose exec python-ai pytest tests/

# カバレッジレポート
docker-compose exec go-app go test -cover ./...
docker-compose exec python-ai pytest --cov=.
```

## 📈 パフォーマンス

### 要件

- 応答時間: 2秒以内（検索）
- 同時処理: 10リクエストまで
- メモリ使用量: 1GB以下

### 最適化

- データベースインデックス
- キャッシュ機能
- 非同期処理

## 🚀 デプロイ

### 本番環境

```bash
# 本番環境の起動
make up-prod

# 全環境の起動（監視含む）
make up-all
```

### バックアップ

```bash
# バックアップの作成
make backup

# 復旧
tar -xzf backups/backup_YYYYMMDD_HHMMSS.tar.gz
```

## 🤝 コントリビューション

1. フォークを作成
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 📞 サポート

- 問題報告: [GitHub Issues](https://github.com/your-org/knowledge-management/issues)
- ドキュメント: [Wiki](https://github.com/your-org/knowledge-management/wiki)
- ディスカッション: [GitHub Discussions](https://github.com/your-org/knowledge-management/discussions)

## 🙏 謝辞

- [OpenAI](https://openai.com/) - AI処理エンジン
- [LangChain](https://langchain.com/) - AI フレームワーク
- [Gin](https://gin-gonic.com/) - Go Web フレームワーク
- [FastAPI](https://fastapi.tiangolo.com/) - Python Web フレームワーク
