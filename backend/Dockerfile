# Goのベースイメージを指定
FROM golang:1.20-alpine

# 作業ディレクトリを指定
WORKDIR /app

# Goモジュールファイルをコピー
COPY go.mod go.sum ./

# 依存関係のパッケージをインストール
RUN go mod download

# 必要なGoパッケージをインストール（corsなどの依存があればここでインストール）
RUN go get github.com/rs/cors

# Goアプリケーションのソースコードをコピー
COPY . .

# 依存関係を整理して不要なパッケージを削除
RUN go mod tidy

# アプリケーションをビルド
RUN go build -o main .

# コンテナ起動時に実行するコマンド
CMD ["./main"]

# ポートを公開
EXPOSE 8080
