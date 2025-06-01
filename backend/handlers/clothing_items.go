package handlers

import (
	"encoding/json"
	"log"
	"net/http"

	"backend/utils"
)

// 服装アイテム一覧取得
func GetClothingItems(w http.ResponseWriter, r *http.Request) {
	db, err := utils.GetDB()
	if err != nil {
		log.Println("DB接続エラー:", err)
		http.Error(w, "DB接続エラー", http.StatusInternalServerError)
		return
	}
	defer db.Close()

	rows, err := db.Query("SELECT clothing_id, name, category FROM clothing_items ORDER BY category, name")
	if err != nil {
		log.Println("クエリエラー:", err)
		http.Error(w, "DBクエリエラー", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var items []utils.ClothingItem
	for rows.Next() {
		var item utils.ClothingItem
		if err := rows.Scan(&item.ClothingID, &item.Name, &item.Category); err != nil {
			log.Println("スキャンエラー:", err)
			http.Error(w, "データ読み込みエラー", http.StatusInternalServerError)
			return
		}
		items = append(items, item)
	}

	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	json.NewEncoder(w).Encode(items)
}
