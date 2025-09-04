# Go プロキシサーバー用 Dockerfile
FROM golang:1.21-alpine AS builder

# 必要なパッケージのインストール
RUN apk add --no-cache git curl

# 作業ディレクトリの設定
WORKDIR /app

# Go modules の設定
ENV GO111MODULE=on
ENV CGO_ENABLED=0

# 依存関係のコピーとダウンロード
COPY go.mod go.sum ./
RUN go mod download

# ソースコードのコピー
COPY . .

# アプリケーションのビルド
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o proxy-server ./cmd/proxy.go

# 本番用イメージ
FROM alpine:latest

# 必要なパッケージのインストール
RUN apk --no-cache add ca-certificates curl

# 作業ディレクトリの設定
WORKDIR /app

# ビルドしたアプリケーションをコピー
COPY --from=builder /app/proxy-server .

# 必要なディレクトリの作成
RUN mkdir -p /app/data /app/logs

# ポートの公開
EXPOSE 50575

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:50575/health || exit 1

# アプリケーションの実行
CMD ["./proxy-server"]
