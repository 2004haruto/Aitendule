package handlers

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"strconv"
	"log"

	"github.com/gorilla/mux"
	"backend/utils"
	_ "github.com/go-sql-driver/mysql"
)

// 都市一覧の取得
func GetUserCities(w http.ResponseWriter, r *http.Request) {
	userIDStr := mux.Vars(r)["id"]
	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		http.Error(w, "無効なユーザーID", http.StatusBadRequest)
		return
	}

	db, err := utils.GetDB()
	if err != nil {
		log.Println("DB接続エラー:", err)
		http.Error(w, "DB接続エラー", http.StatusInternalServerError)
		return
	}
	defer db.Close()

	rows, err := db.Query(`
		SELECT uc.city_id, uc.display_order, uc.is_favorite, c.city_name
		FROM user_cities uc
		JOIN cities c ON uc.city_id = c.city_id
		WHERE uc.user_id = ?`, userID)
	if err != nil {
		log.Println("クエリ実行エラー:", err)
		http.Error(w, "DBクエリエラー", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var cities []utils.City
	for rows.Next() {
		var city utils.City
		if err := rows.Scan(&city.CityID, &city.DisplayOrder, &city.IsFavorite, &city.CityName); err != nil {
			log.Println("データ読み取りエラー:", err)
			http.Error(w, "データ読み取りエラー", http.StatusInternalServerError)
			return
		}
		cities = append(cities, city)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(cities)
}

// 都市の追加
func AddUserCity(w http.ResponseWriter, r *http.Request) {
	userIDStr := mux.Vars(r)["id"]
	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		http.Error(w, "無効なユーザーID", http.StatusBadRequest)
		return
	}

	db, err := utils.GetDB()
	if err != nil {
		log.Println("DB接続エラー:", err)
		http.Error(w, "DB接続エラー", http.StatusInternalServerError)
		return
	}
	defer db.Close()

	var city utils.City
	if err := json.NewDecoder(r.Body).Decode(&city); err != nil {
		log.Println("リクエスト読み込みエラー:", err)
		http.Error(w, "リクエスト読み込みエラー", http.StatusBadRequest)
		return
	}

	// city_id を取得 or 追加
	var cityID int
	err = db.QueryRow(`SELECT city_id FROM cities WHERE city_name = ?`, city.CityName).Scan(&cityID)
	if err == sql.ErrNoRows {
		result, err := db.Exec(`INSERT INTO cities (city_name) VALUES (?)`, city.CityName)
		if err != nil {
			log.Println("都市追加失敗:", err)
			http.Error(w, "都市追加失敗", http.StatusInternalServerError)
			return
		}
		lastInsertID, err := result.LastInsertId()
		if err != nil {
			log.Println("ID取得失敗:", err)
			http.Error(w, "ID取得失敗", http.StatusInternalServerError)
			return
		}
		cityID = int(lastInsertID)
	} else if err != nil {
		log.Println("都市検索失敗:", err)
		http.Error(w, "都市検索失敗", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec(`
		INSERT INTO user_cities (user_id, city_id, display_order, is_favorite)
		VALUES (?, ?, ?, ?)`,
		userID, cityID, city.DisplayOrder, city.IsFavorite)
	if err != nil {
		log.Println("user_cities 追加失敗:", err)
		http.Error(w, "都市追加失敗", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"message": "都市が正常に追加されました"})
}

// 都市の削除（都市名ベース）
func DeleteCityByName(w http.ResponseWriter, r *http.Request) {
	userIDStr := mux.Vars(r)["id"]
	cityName := mux.Vars(r)["cityName"]

	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		http.Error(w, "無効なユーザーID", http.StatusBadRequest)
		return
	}

	db, err := utils.GetDB()
	if err != nil {
		log.Println("DB接続エラー:", err)
		http.Error(w, "DB接続エラー", http.StatusInternalServerError)
		return
	}
	defer db.Close()

	var cityID int
	err = db.QueryRow(`SELECT city_id FROM cities WHERE city_name = ?`, cityName).Scan(&cityID)
	if err == sql.ErrNoRows {
		http.Error(w, "都市が見つかりません", http.StatusNotFound)
		return
	} else if err != nil {
		log.Println("都市ID取得エラー:", err)
		http.Error(w, "都市ID取得エラー", http.StatusInternalServerError)
		return
	}

	// user_cities から削除
	_, err = db.Exec(`DELETE FROM user_cities WHERE user_id = ? AND city_id = ?`, userID, cityID)
	if err != nil {
		log.Println("user_cities 削除失敗:", err)
		http.Error(w, "user_cities 削除失敗", http.StatusInternalServerError)
		return
	}

	// cities から削除
	_, err = db.Exec(`DELETE FROM cities WHERE city_id = ?`, cityID)
	if err != nil {
		log.Println("cities 削除失敗:", err)
		http.Error(w, "cities 削除失敗", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"message": "都市を削除しました"})
}
