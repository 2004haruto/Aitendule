package handlers

import (
	"encoding/json"
	"log"
	"net/http"
	"backend/utils"
)

func Login(w http.ResponseWriter, r *http.Request) {
	log.Println("Login API called")

	// ConnectDBを呼び出してエラーチェック
	err := utils.ConnectDB()
	if err != nil {
		log.Printf("Database connection error: %v", err)
		http.Error(w, "Internal server error: Unable to connect to database", http.StatusInternalServerError)
		return
	}
	defer utils.DB.Close()

	var EmailPass utils.EmailPass

	// JSONデータを受け取ってパース
	decoder := json.NewDecoder(r.Body)
	err = decoder.Decode(&EmailPass)
	if err != nil {
		http.Error(w, "Invalid JSON data", http.StatusBadRequest)
		return
	}

	rows, err := utils.DB.Query("SELECT password, user_id FROM users WHERE email = ?", EmailPass.Email)
	if err != nil {
		log.Printf("Error fetching user data: %v", err)
		http.Error(w, "Error fetching user data", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var idPass utils.IdPass
	if rows.Next() {
		err := rows.Scan(&idPass.Password, &idPass.User_id)
		if err != nil {
			log.Println("Error scanning user data")
			http.Error(w, "Error processing user data", http.StatusInternalServerError)
			return
		}
	} else {
		log.Println("User not found")
		http.Error(w, "Invalid email or password", http.StatusUnauthorized)
		return
	}

	// パスワードの確認（ハッシュ化している場合は bcrypt.CompareHashAndPassword を使用）
	if EmailPass.Password != idPass.Password {
		log.Println("Incorrect password")
		http.Error(w, "Invalid email or password", http.StatusUnauthorized)
		return
	}

	// JSONレスポンスを送信
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	response := map[string]string{"user_id": idPass.User_id, "message": "Login successful"}
	json.NewEncoder(w).Encode(response)
}
