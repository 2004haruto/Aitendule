package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"github.com/joho/godotenv"
	"github.com/rs/cors"
	"github.com/gorilla/mux"
	"backend/handlers"
	"backend/utils"
)

func init() {
	// .env ファイルのロード
	err := godotenv.Load()
	if err != nil {
		log.Println("Warning: .envファイルがないよ")
	}

	// 必須環境変数の検証
	requiredEnv := []string{"JWT_SECRET", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_HOST", "MYSQL_DB"}
	for _, envVar := range requiredEnv {
		if os.Getenv(envVar) == "" {
			log.Fatalf("Missing required environment variable: %s", envVar)
		}
	}
}

func main() {
	// DB接続（リトライ付き）
	const maxRetries = 10
	const retryDelay = 3 * time.Second // リトライの間隔を設定

	if err := utils.ConnectDBWithRetry(maxRetries, retryDelay); err != nil {
		log.Fatalf("DB接続失敗（最大リトライ%d回）: %v", maxRetries, err)
	}

	// CORS 設定
	corsHandler := cors.New(cors.Options{
		AllowedOrigins: []string{"http://localhost:3000", "http://10.104.0.175:3000"},
		AllowedMethods: []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders: []string{"Content-Type", "Authorization"},
	})

	// ルーターの作成
	r := mux.NewRouter()

	// ルート設定
	r.HandleFunc("/api/login", handlers.Login).Methods("POST")
	r.HandleFunc("/api/users/{id}/cities", handlers.GetUserCities).Methods("GET")
	r.HandleFunc("/api/users/{id}/cities", handlers.AddUserCity).Methods("POST")
	r.HandleFunc("/api/users/{id}/cities/name/{cityName}", handlers.DeleteCityByName).Methods("DELETE")
	r.HandleFunc("/api/users/{id}/clothing_choices", handlers.AddUserClothingChoice).Methods("POST")
	r.HandleFunc("/api/clothing_items", handlers.GetClothingItems).Methods("GET")
	r.HandleFunc("/api/users/{id}/locations", handlers.PostUserLocation).Methods("POST")


	// サーバー設定
	server := &http.Server{
		Addr:    ":3000", // ポート3000でリスン
		Handler: corsHandler.Handler(r),
	}

	// サーバー起動
	log.Println("✅ Starting server on port 3000...")
	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("Server startup error: %v", err)
	}
}
