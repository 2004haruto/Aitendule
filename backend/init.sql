-- データベース作成
CREATE DATABASE IF NOT EXISTS AI_Seminar_IE3B;
USE AI_Seminar_IE3B;

-- ユーザーマスタ（平文パスワード対応）
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 服装アイテム（マスタ）
CREATE TABLE IF NOT EXISTS clothing_items (
    clothing_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ユーザーの服装選択履歴（学習データ）
CREATE TABLE IF NOT EXISTS user_clothing_choices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    clothing_id INT NOT NULL,
    weather VARCHAR(20),
    temperature FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (clothing_id) REFERENCES clothing_items(clothing_id)
);

-- ユーザー位置情報（最新の位置を保存）
CREATE TABLE IF NOT EXISTS user_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 初期データ（服装アイテム）
INSERT INTO clothing_items (name, category) VALUES
  ('Tシャツ', 'tops'),
  ('長袖シャツ', 'tops'),
  ('ジーンズ', 'bottoms'),
  ('チノパン', 'bottoms'),
  ('スニーカー', 'shoes'),
  ('ブーツ', 'shoes'),
  ('ダウンジャケット', 'outer'),
  ('トレンチコート', 'outer'),
  ('マフラー', 'accessory'),
  ('帽子', 'accessory');

-- 初期ユーザー（テスト用）
INSERT INTO users (name, email, password) VALUES
  ('テストユーザー', 'daichi@example.com', 'password');