# ナレッジ管理ツール - Makefile

.PHONY: help build up down logs clean test lint format

# デフォルトターゲット
help: ## 利用可能なコマンドを表示
	@echo "利用可能なコマンド:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# 開発環境の構築
setup: ## 開発環境の初期セットアップ
	@echo "開発環境のセットアップを開始..."
	@mkdir -p data logs exports config ssl
	@cp env.example .env
	@echo "環境変数ファイル .env を作成しました。API キーを設定してください。"
	@echo "セットアップ完了！"

# Docker イメージのビルド
build: ## Docker イメージをビルド
	@echo "Docker イメージをビルド中..."
	docker-compose build

# 開発環境の起動
up: ## 開発環境を起動
	@echo "開発環境を起動中..."
	docker-compose up -d

# 本番環境の起動
up-prod: ## 本番環境を起動（Nginx含む）
	@echo "本番環境を起動中..."
	docker-compose --profile production up -d

# 監視環境の起動
up-monitoring: ## 監視環境を起動
	@echo "監視環境を起動中..."
	docker-compose --profile monitoring up -d

# 全環境の起動
up-all: ## 全環境を起動
	@echo "全環境を起動中..."
	docker-compose --profile production --profile monitoring up -d

# 環境の停止
down: ## 環境を停止
	@echo "環境を停止中..."
	docker-compose down

# ログの表示
logs: ## ログを表示
	docker-compose logs -f

# 特定サービスのログ
logs-go: ## Go アプリケーションのログを表示
	docker-compose logs -f go-app

logs-ai: ## Python AIサービスのログを表示
	docker-compose logs -f python-ai

# 環境のクリーンアップ
clean: ## 環境をクリーンアップ
	@echo "環境をクリーンアップ中..."
	docker-compose down -v
	docker system prune -f

# テストの実行
test: ## テストを実行
	@echo "テストを実行中..."
	docker-compose exec go-app go test ./...
	docker-compose exec python-ai pytest

# リンターの実行
lint: ## リンターを実行
	@echo "リンターを実行中..."
	docker-compose exec go-app golangci-lint run
	docker-compose exec python-ai flake8 .

# コードフォーマット
format: ## コードをフォーマット
	@echo "コードをフォーマット中..."
	docker-compose exec go-app go fmt ./...
	docker-compose exec python-ai black .

# データベースの初期化
init-db: ## データベースを初期化
	@echo "データベースを初期化中..."
	docker-compose exec go-app ./knowledge-app migrate

# バックアップの作成
backup: ## データベースのバックアップを作成
	@echo "バックアップを作成中..."
	@mkdir -p backups
	@tar -czf backups/backup_$(shell date +%Y%m%d_%H%M%S).tar.gz data/

# ヘルスチェック
health: ## ヘルスチェックを実行
	@echo "ヘルスチェックを実行中..."
	@curl -f http://localhost:8080/api/health || echo "Go アプリケーション: 異常"
	@curl -f http://localhost:8001/ai/health || echo "Python AIサービス: 異常"

# 開発用のシェルアクセス
shell-go: ## Go アプリケーションコンテナにシェルアクセス
	docker-compose exec go-app sh

shell-ai: ## Python AIサービスコンテナにシェルアクセス
	docker-compose exec python-ai bash

# データベース管理ツールの起動
db-admin: ## データベース管理ツールを起動
	@echo "データベース管理ツールを起動中..."
	docker-compose --profile dev up -d db-admin
	@echo "http://localhost:8081 でアクセス可能です"

# 監視ダッシュボードの起動
monitoring: ## 監視ダッシュボードを起動
	@echo "監視ダッシュボードを起動中..."
	docker-compose --profile monitoring up -d
	@echo "Grafana: http://localhost:3000 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"

# 開発用のホットリロード
dev: ## 開発用のホットリロード環境を起動
	@echo "開発用環境を起動中..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# 本番用のビルド
build-prod: ## 本番用のイメージをビルド
	@echo "本番用イメージをビルド中..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# セキュリティスキャン
security-scan: ## セキュリティスキャンを実行
	@echo "セキュリティスキャンを実行中..."
	docker-compose exec go-app gosec ./...
	docker-compose exec python-ai bandit -r .

# パフォーマンステスト
perf-test: ## パフォーマンステストを実行
	@echo "パフォーマンステストを実行中..."
	@which ab > /dev/null || (echo "Apache Bench (ab) をインストールしてください" && exit 1)
	ab -n 1000 -c 10 http://localhost:8080/api/health
