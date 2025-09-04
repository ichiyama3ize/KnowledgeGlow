# Web UI用 Dockerfile
FROM python:3.11-slim

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# Pythonの依存関係をインストール
RUN pip install --no-cache-dir fastapi uvicorn

# アプリケーションファイルのコピー
COPY . .

# ポートの公開
EXPOSE 8000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# アプリケーションの実行
CMD ["python", "server.py"]