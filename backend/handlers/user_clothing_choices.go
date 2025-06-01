package handlers

import (
	"encoding/json"
	"log"
	"net/http"

	"backend/utils"
)

func AddUserClothingChoice(w http.ResponseWriter, r *http.Request) {
	// URLパラメータから user_id 取得も可能。ここではリクエストボディに含める想定

var req utils.UserClothingChoiceRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		log.Println("リクエストJSONデコードエラー:", err)
		http.Error(w, "リクエスト形式エラー", http.StatusBadRequest)
		return
	}

	db, err := utils.GetDB()
	if err != nil {
		log.Println("DB接続エラー:", err)
		http.Error(w, "DB接続エラー", http.StatusInternalServerError)
		return
	}
	defer db.Close()

	tx, err := db.Begin()
	if err != nil {
		log.Println("トランザクション開始エラー:", err)
		http.Error(w, "DBエラー", http.StatusInternalServerError)
		return
	}

	stmt, err := tx.Prepare(`
		INSERT INTO user_clothing_choices
			(user_id, clothing_id, choice_date, weather, temperature, is_recommended)
		VALUES (?, ?, ?, ?, ?, ?)
	`)
	if err != nil {
		log.Println("ステートメント準備エラー:", err)
		tx.Rollback()
		http.Error(w, "DBエラー", http.StatusInternalServerError)
		return
	}
	defer stmt.Close()

	for _, choice := range req.Choices {
		_, err := stmt.Exec(req.UserID, choice.ClothingID, req.ChoiceDate, req.Weather, req.Temperature, req.IsRecommended)
		if err != nil {
			log.Println("データ挿入エラー:", err)
			tx.Rollback()
			http.Error(w, "DB挿入エラー", http.StatusInternalServerError)
			return
		}
	}

	if err := tx.Commit(); err != nil {
		log.Println("コミットエラー:", err)
		http.Error(w, "DBコミットエラー", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"message": "服装選択を保存しました"})
}
