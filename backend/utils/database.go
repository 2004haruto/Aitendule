package utils

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"regexp"
	"time"

	"github.com/go-sql-driver/mysql"
	"golang.org/x/crypto/bcrypt"
)

// DB はデータベース接続のグローバル変数
var DB *sql.DB

// DB接続関数
func ConnectDB() error {
	config := mysql.Config{
		User:                 os.Getenv("MYSQL_USER"),
		Passwd:               os.Getenv("MYSQL_PASSWORD"),
		Net:                  "tcp",
		Addr:                 os.Getenv("MYSQL_HOST"),
		DBName:               os.Getenv("MYSQL_DB"),
		ParseTime:            true,
		AllowNativePasswords: true,
		Timeout:              5 * time.Second,
		Params: map[string]string{
				"charset": "utf8mb4", // ← ここで指定する
			},
	}

	var err error
	DB, err = sql.Open("mysql", config.FormatDSN())
	if err != nil {
		return fmt.Errorf("error opening database: %v", err)
	}

	// 接続テスト
	if err = DB.Ping(); err != nil {
		DB = nil // 明示的に nil にする
		return fmt.Errorf("error connecting to the database: %v", err)
	}

	DB.SetMaxOpenConns(25)
	DB.SetMaxIdleConns(25)
	DB.SetConnMaxLifetime(5 * time.Minute)

	log.Println("✅ DB connection established.")
	return nil
}

// DB接続にリトライを追加した関数
func ConnectDBWithRetry(maxRetries int, retryDelay time.Duration) error {
	var err error

	for i := 1; i <= maxRetries; i++ {
		err = ConnectDB()
		if err == nil {
			log.Printf("✅ DB接続成功（%d回目）", i)
			return nil // 接続成功したら終了
		}

		// リトライ時のログを出力
		log.Printf("⏳ DB接続リトライ中（%d/%d）: %v", i, maxRetries, err)
		// 指定した間隔でリトライ
		time.Sleep(retryDelay)
	}

	return fmt.Errorf("DB接続失敗: %v", err)
}

// DB利用前に nil チェックを行うヘルパー関数
func GetDB() (*sql.DB, error) {
	if DB == nil {
		return nil, fmt.Errorf("database connection is not initialized")
	}

	// DB接続が切れているかチェック
	if err := DB.Ping(); err != nil {
		log.Println("⚠️ DB.Ping failed:", err)
		// 接続が切れていた場合、再接続を試みる
		log.Println("再接続を試みます...")
		// maxRetries と retryDelay を引数として渡す
		err := ConnectDBWithRetry(3, 3*time.Second) // ここでリトライ回数と間隔を設定
		if err != nil {
			return nil, fmt.Errorf("database connection is closed or invalid: %v", err)
		}
	}

	return DB, nil
}

// パスワードハッシュ化
func HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)
	return string(bytes), err
}

// パスワード検証
func CheckPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}

// メールアドレスのバリデーション
func ValidateEmail(email string) bool {
	emailRegex := regexp.MustCompile(`^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,4}$`)
	return emailRegex.MatchString(email)
}
