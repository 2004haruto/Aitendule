package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"
	"log"

	"github.com/gorilla/mux"
	"backend/utils"
)

// 位置情報を受け取りDBに保存するAPI
func PostUserLocation(w http.ResponseWriter, r *http.Request) {
	userIDStr := mux.Vars(r)["id"]
	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		http.Error(w, "無効なユーザーID", http.StatusBadRequest)
		return
	}

	var loc utils.Location
	if err := json.NewDecoder(r.Body).Decode(&loc); err != nil {
		log.Println("リクエスト読み込みエラー:", err)
		http.Error(w, "リクエスト読み込みエラー", http.StatusBadRequest)
		return
	}

	db, err := utils.GetDB()
	if err != nil {
		log.Println("DB接続エラー:", err)
		http.Error(w, "DB接続エラー", http.StatusInternalServerError)
		return
	}
	defer db.Close()

	// 位置情報をuser_locationsテーブルに保存する想定
	_, err = db.Exec(`
		INSERT INTO user_locations (user_id, latitude, longitude, created_at)
		VALUES (?, ?, ?, NOW())
	`, userID, loc.Latitude, loc.Longitude)
	if err != nil {
		log.Println("位置情報保存失敗:", err)
		http.Error(w, "位置情報保存失敗", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"message": "位置情報を保存しました"})
}
