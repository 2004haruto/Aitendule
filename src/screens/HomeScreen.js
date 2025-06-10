import React, { useEffect, useState } from "react";
import {
  StyleSheet,
  View,
  Text,
  ScrollView,
  TouchableOpacity,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as Location from "expo-location";
import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";

import WeatherSection from "../components/WeatherSection";
import TodaySchedule from "../components/TodaySchedule";
import ClothingSuggestion from "../components/ClothingSuggestion";

export default function HomeScreen({ navigation }) {
  const [location, setLocation] = useState(null);
  const [locationError, setLocationError] = useState(null);
  const [userName, setUserName] = useState("ユーザー");

  useEffect(() => {
    const fetchData = async () => {
      // ユーザー名取得（任意）
      const name = await AsyncStorage.getItem("userName");
      if (name) setUserName(name);

      // 位置情報の取得と送信
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        setLocationError("位置情報の許可が必要です");
        return;
      }

      let loc = await Location.getCurrentPositionAsync({});
      setLocation(loc);

      try {
        const storedUserId = await AsyncStorage.getItem("user_id");
        if (!storedUserId) {
          console.error("ユーザーIDが見つかりません");
          return;
        }

        const response = await axios.post(
          `http://10.104.0.167:3000/api/users/${storedUserId}/locations`,
          {
            latitude: loc.coords.latitude,
            longitude: loc.coords.longitude,
            timestamp: loc.timestamp,
          }
        );
        console.log("位置情報送信成功:", response.data);
      } catch (error) {
        console.error("位置情報送信エラー:", error);
      }
    };

    fetchData();
  }, []);

  return (
    <View style={styles.container}>
      {/* ヘッダー */}
      <View style={styles.header}>
        <View style={styles.profileIcon} />
        <View>
          <Text style={styles.userName}>{userName}さん</Text>
          <Text style={styles.appDescription}>AIによる日常サポートアプリ</Text>
        </View>
      </View>

      <ScrollView style={styles.content}>
        {/* 天気情報 */}
        <View style={styles.weatherContainer}>
          <WeatherSection styles={styles} />
        </View>

        {/* 服装提案 */}
        <View style={styles.suggestionContainer}>
          {locationError ? (
            <Text style={{ color: "red" }}>{locationError}</Text>
          ) : location ? (
            <ClothingSuggestion location={location} />
          ) : (
            <Text>位置情報を取得中...</Text>
          )}
        </View>

        {/* 今日の予定 */}
        <View style={styles.scheduleContainer}>
          <TodaySchedule />
        </View>

        {/* AI学習メモ */}
        <View style={styles.learningMemoContainer}>
          <Text style={styles.sectionTitle}>AI学習メモ</Text>
          <View style={styles.memoItem}>
            <View style={styles.memoIcon} />
            <Text style={styles.memoText}>最近の好み</Text>
          </View>
        </View>
      </ScrollView>

      {/* ボトムナビゲーション */}
      <View style={styles.bottomNavigation}>
        <TouchableOpacity style={styles.navItem}>
          <Ionicons name="cart-outline" size={24} color="gray" />
          <Text style={styles.navText}>ショップ</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.navItem}
          onPress={() => navigation.navigate("Calendar")}
        >
          <Ionicons name="calendar-outline" size={24} color="gray" />
          <Text style={styles.navText}>スケジュール</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.navItem}>
          <Ionicons name="document-text-outline" size={24} color="gray" />
          <Text style={styles.navText}>ノート</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f4f4f4",
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    backgroundColor: "white",
    borderBottomWidth: 1,
    borderBottomColor: "#ddd",
  },
  profileIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#ccc",
    marginRight: 12,
  },
  userName: {
    fontSize: 18,
    fontWeight: "bold",
  },
  appDescription: {
    fontSize: 12,
    color: "gray",
  },
  content: {
    flex: 1,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "bold",
    marginBottom: 12,
  },
  weatherContainer: {
    backgroundColor: "white",
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  suggestionContainer: {
    backgroundColor: "white",
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  scheduleContainer: {
    backgroundColor: "white",
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  learningMemoContainer: {
    backgroundColor: "white",
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  memoItem: {
    flexDirection: "row",
    alignItems: "center",
  },
  memoIcon: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: "#ffc0cb",
    marginRight: 12,
  },
  memoText: {
    fontSize: 14,
  },
  bottomNavigation: {
    flexDirection: "row",
    justifyContent: "space-around",
    paddingVertical: 12,
    backgroundColor: "#fff",
    borderTopWidth: 1,
    borderTopColor: "#ddd",
  },
  navItem: {
    alignItems: "center",
  },
  navText: {
    fontSize: 12,
    color: "gray",
  },
});
