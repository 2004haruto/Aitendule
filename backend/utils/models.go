package utils

type EmailPass struct {
	Email string `json:"email"`
	Password string `json:"password"`
}
type IdPass struct {
	Password string `json:"password"`
	User_id string `json:"user_id"`
}
type Id struct {
	User_id string `json:"user_id"`
}

// 都市情報
type City struct {
	CityID     int    `json:"city_id"`      // city_id を追加
	CityName   string `json:"city_name"`    // city_name を追加
	DisplayOrder int   `json:"display_order"` // display_order を追加
	IsFavorite  int  `json:"is_favorite"`  // is_favorite を追加
}

type ClothingChoice struct {
	ClothingID int `json:"clothing_id"`
	IsRecommended  bool `json:"is_recommended"`
}

type UserClothingChoiceRequest struct {
	UserID        int              `json:"user_id"`
	ChoiceDate    string           `json:"choice_date"`    // 例: "2025-05-27"
	Weather       string           `json:"weather"`        // 例: "晴れ"
	Temperature   float64          `json:"temperature"`    // 例: 25.5
	Choices       []ClothingChoice `json:"choices"`        // 選択した服装アイテムIDリスト
	IsRecommended bool             `json:"is_recommended"` // AI提案の服装か否か
}

type ClothingItem struct {
	ClothingID int    `json:"clothing_id"`
	Name       string `json:"name"`
	Category   string `json:"category"`
}

// 位置情報リクエスト用の構造体
type Location struct {
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
}