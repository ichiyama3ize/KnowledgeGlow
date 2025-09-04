# Go メインアプリケーション用 Dockerfile
FROM golang:1.21-alpine AS builder

# 必要なパッケージのインストール
RUN apk add --no-cache git curl

# 作業ディレクトリの設定
WORKDIR /app

# Go modules の設定
ENV GO111MODULE=on
ENV CGO_ENABLED=1

# 依存関係のコピーとダウンロード
COPY go.mod go.sum ./
RUN go mod download

# ソースコードのコピー
COPY . .

# アプリケーションのビルド
RUN CGO_ENABLED=1 GOOS=linux go build -a -installsuffix cgo -o knowledge-app .

# 本番用イメージ
FROM alpine:latest

# 必要なパッケージのインストール
RUN apk --no-cache add ca-certificates sqlite curl

# 作業ディレクトリの設定
WORKDIR /app

# ビルドしたアプリケーションをコピー
COPY --from=builder /app/knowledge-app .

# 設定ファイルとテンプレートのコピー
COPY --from=builder /app/config ./config
COPY --from=builder /app/templates ./templates
COPY --from=builder /app/static ./static

# 必要なディレクトリの作成
RUN mkdir -p /app/data /app/logs /app/exports

# ポートの公開
EXPOSE 8080

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/api/health || exit 1

# アプリケーションの実行
CMD ["./knowledge-app"]
