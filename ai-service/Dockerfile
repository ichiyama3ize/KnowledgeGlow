# Python AIサービス用 Dockerfile
FROM python:3.11-slim AS builder

# システムパッケージの更新と必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# Python の依存関係のコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 本番用イメージ
FROM python:3.11-slim

# システムパッケージの更新と必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# ビルドしたPythonパッケージをコピー
COPY --from=builder /root/.local /root/.local

# 環境変数の設定
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# ソースコードのコピー
COPY . .

# 必要なディレクトリの作成
RUN mkdir -p /app/data /app/logs

# ポートの公開
EXPOSE 8001

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8001/ai/health || exit 1

# アプリケーションの実行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
